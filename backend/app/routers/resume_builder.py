import base64
import textwrap
from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.resume import Resume
from app.models.resume_draft import ResumeDraft
from app.models.skill import Skill, UserSkill
from app.models.user import User
from app.services import ai_service
from app.services.skill_alias import canonicalize

router = APIRouter(prefix="/api/resume-builder", tags=["resume builder"])
FIELDS = ("personal_info", "summary", "education", "skills", "projects", "experience", "certifications", "achievements")


class DraftInput(BaseModel):
    personal_info: dict = Field(default_factory=dict)
    summary: str = ""
    education: list = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list = Field(default_factory=list)
    experience: list = Field(default_factory=list)
    certifications: list = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


def _empty() -> dict:
    return {"id": None, "personal_info": {}, "summary": "", "education": [], "skills": [], "projects": [], "experience": [], "certifications": [], "achievements": [], "has_saved_draft": False}


def _out(draft: ResumeDraft | None) -> dict:
    if draft is None:
        return _empty()
    return {"id": draft.id, **{name: getattr(draft, name) or ({} if name == "personal_info" else "" if name == "summary" else []) for name in FIELDS}, "use_for_overview": draft.use_for_overview, "has_saved_draft": True}


def _prefill(resume: Resume | None) -> dict:
    data = _empty()
    profile = resume.analysis.parsed_profile if resume and resume.analysis else {}
    data.update({key: profile.get(key, data[key]) for key in ("education", "skills", "projects", "experience", "certifications", "achievements")})
    return data


def _sync_builder_skills(db: Session, user_id: int, skills: list[str]) -> None:
    known = {canonicalize(item.name): item for item in db.query(Skill).all()}
    for raw in skills:
        if not isinstance(raw, str) or not raw.strip():
            continue
        key = canonicalize(raw)
        skill = known.get(key)
        if skill is None:
            skill = Skill(name=raw.strip()); db.add(skill); db.flush(); known[key] = skill
        link = db.query(UserSkill).filter(UserSkill.user_id == user_id, UserSkill.skill_id == skill.id).first()
        if link is None:
            db.add(UserSkill(user_id=user_id, skill_id=skill.id, proficiency=65, evidence_source="builder"))
        elif link.evidence_source != "manual":
            link.proficiency = max(link.proficiency, 65)
            link.evidence_source = "builder"


@router.get("/draft")
def get_draft(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    draft = db.query(ResumeDraft).filter(ResumeDraft.user_id == current_user.id).first()
    if draft:
        return _out(draft)
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    data = _prefill(resume)
    data["can_prefill"] = bool(resume and resume.analysis)
    return data


@router.put("/draft")
def save_draft(payload: DraftInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    photo = payload.personal_info.get("photo_data_url")
    if photo and (not isinstance(photo, str) or not photo.startswith("data:image/") or len(photo) > 3_000_000):
        raise HTTPException(status_code=422, detail="Use an image under 2MB for your resume photo.")
    draft = db.query(ResumeDraft).filter(ResumeDraft.user_id == current_user.id).first()
    if draft is None:
        draft = ResumeDraft(user_id=current_user.id); db.add(draft)
    for name, value in payload.model_dump().items():
        setattr(draft, name, value)
    _sync_builder_skills(db, current_user.id, payload.skills)
    db.commit(); db.refresh(draft)
    return _out(draft)


@router.post("/improve-summary")
def improve_summary(payload: DraftInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return {"summary": ai_service.improve_resume_summary(
            db, current_user.id, payload.summary,
            str(payload.personal_info.get("headline") or ""), payload.skills,
        )}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.patch("/draft/overview")
def choose_draft_for_overview(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    draft = db.query(ResumeDraft).filter(ResumeDraft.user_id == current_user.id).first()
    if draft is None:
        raise HTTPException(status_code=404, detail="Save your builder resume before using it in Overview.")
    draft.use_for_overview = bool(payload.get("enabled"))
    _sync_builder_skills(db, current_user.id, draft.skills or [])
    db.commit(); db.refresh(draft)
    return _out(draft)


@router.delete("/draft")
def reset_draft(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    draft = db.query(ResumeDraft).filter(ResumeDraft.user_id == current_user.id).first()
    if draft is not None:
        db.delete(draft); db.commit()
    # Manual and uploaded-resume skills remain intact; only this builder's
    # auto-synced evidence is cleared for a true fresh start.
    db.query(UserSkill).filter(UserSkill.user_id == current_user.id, UserSkill.evidence_source == "builder").delete(synchronize_session=False)
    db.commit()
    return {"reset": True}


def _lines(draft: ResumeDraft) -> list[str]:
    info = draft.personal_info or {}
    lines = [info.get("name", "Your Name"), " | ".join(filter(None, [info.get("email"), info.get("phone"), info.get("location")]))]
    if draft.summary: lines += ["SUMMARY", draft.summary]
    if draft.skills: lines += ["SKILLS", ", ".join(draft.skills)]
    for section, entries in (("EDUCATION", draft.education or []), ("PROJECTS", draft.projects or []), ("EXPERIENCE", draft.experience or []), ("CERTIFICATIONS", draft.certifications or []), ("ACHIEVEMENTS", draft.achievements or [])):
        if entries:
            lines.append(section)
            for item in entries:
                lines.append(item if isinstance(item, str) else " — ".join(str(value) for value in item.values() if value))
    return [str(line) for line in lines if line]


def _as_text(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return str(value or "")


def _render_pdf(draft: ResumeDraft) -> bytes:
    """Create a polished, single-column, ATS-safe PDF without layout tables."""
    import fitz

    document = fitz.open()
    width, height = 595, 842  # A4 points
    left, right, top, bottom = 52, 52, 48, 48
    page = document.new_page(width=width, height=height)
    y = top

    def new_page():
        nonlocal page, y
        page = document.new_page(width=width, height=height)
        y = top

    def box(text: str, size: float = 10, color=(0.11, 0.14, 0.20), bold=False, gap=5):
        nonlocal y
        if not text:
            return
        font = "hebo" if bold else "helv"
        estimated = max(18, (len(text) / 88 + 1) * (size * 1.45))
        if y + estimated > height - bottom:
            new_page()
        rect = fitz.Rect(left, y, width - right, min(height - bottom, y + max(estimated + 18, 42)))
        remaining = page.insert_textbox(rect, text, fontname=font, fontsize=size, color=color, lineheight=1.28)
        used = rect.height - max(0, remaining)
        y += max(size * 1.55, used) + gap

    def heading(text: str):
        nonlocal y
        if y + 30 > height - bottom:
            new_page()
        page.draw_line(fitz.Point(left, y + 17), fitz.Point(width - right, y + 17), color=(0.65, 0.36, 0.20), width=0.8)
        box(text.upper(), 11, color=(0.48, 0.24, 0.12), bold=True, gap=7)

    info = draft.personal_info or {}
    box(str(info.get("name") or "YOUR NAME").upper(), 20, color=(0.10, 0.17, 0.28), bold=True, gap=3)
    box(" | ".join(filter(None, [str(info.get("email") or ""), str(info.get("phone") or ""), str(info.get("location") or "")])), 9, color=(0.30, 0.36, 0.45), gap=2)
    box(" | ".join(filter(None, [str(info.get("linkedin") or ""), str(info.get("github") or ""), str(info.get("portfolio") or "")])), 8, color=(0.30, 0.36, 0.45), gap=10)
    if draft.summary:
        heading("Profile"); box(draft.summary, 10, gap=9)
    if draft.skills:
        heading("Skills"); box(" | ".join(str(item) for item in draft.skills if item), 9.5, gap=9)
    if draft.projects:
        heading("Projects")
        for project in draft.projects:
            if not isinstance(project, dict):
                box(str(project), 10); continue
            title = " - ".join(filter(None, [_as_text(project.get("name")), _as_text(project.get("tech_stack"))]))
            box(title, 10.5, bold=True, gap=2); box(_as_text(project.get("description")), 9.5, gap=2)
            if project.get("link"): box(_as_text(project.get("link")), 8.5, color=(0.25, 0.35, 0.62), gap=6)
    if draft.experience:
        heading("Experience")
        for job in draft.experience:
            if not isinstance(job, dict):
                box(str(job), 10); continue
            title = " - ".join(filter(None, [_as_text(job.get("role")), _as_text(job.get("company"))]))
            dates = " - ".join(filter(None, [_as_text(job.get("start")), _as_text(job.get("end"))]))
            box(title, 10.5, bold=True, gap=1); box(dates, 8.5, color=(0.35, 0.40, 0.48), gap=2)
            bullets = job.get("bullets", [])
            if isinstance(bullets, str): bullets = bullets.splitlines()
            for bullet in bullets if isinstance(bullets, list) else []: box(f"- {bullet}", 9.5, gap=1)
            y += 5
    if draft.education:
        heading("Education")
        for item in draft.education:
            if not isinstance(item, dict): box(str(item), 10); continue
            box(" - ".join(filter(None, [_as_text(item.get("degree")), _as_text(item.get("institution"))])), 10, bold=True, gap=1)
            box(" | ".join(filter(None, [_as_text(item.get("field")), " - ".join(filter(None, [_as_text(item.get("start")), _as_text(item.get("end"))]))])), 9, color=(0.35, 0.40, 0.48), gap=5)
    if draft.certifications:
        heading("Certifications")
        for item in draft.certifications: box(_as_text(item) if not isinstance(item, dict) else " - ".join(filter(None, [_as_text(item.get("name")), _as_text(item.get("issuer")), _as_text(item.get("year"))])), 9.5)
    if draft.achievements:
        heading("Achievements")
        for item in draft.achievements: box(f"- {item}", 9.5, gap=1)
    return document.tobytes(garbage=4, deflate=True)


def _render_template_pdf(draft: ResumeDraft) -> bytes:
    """Render the fixed SyncLyft-inspired two-column CareerOS template."""
    import fitz

    document = fitz.open()
    width, height, sidebar = 595, 842, 170
    main_left, main_right = sidebar + 18, 28
    info = draft.personal_info or {}
    template = str(info.get("template") or "synclift")
    palettes = {
        "synclift": ((0.62, 0.38, 0.23), (0.97, 0.94, 0.92), (0.57, 0.50, 0.51), (0.16, 0.14, 0.14), (0.38, 0.34, 0.34)),
        "midnight": ((0.20, 0.42, 0.72), (0.96, 0.98, 1.0), (0.06, 0.12, 0.22), (0.06, 0.10, 0.16), (0.25, 0.32, 0.42)),
        "sage": ((0.20, 0.43, 0.36), (0.98, 0.98, 0.94), (0.38, 0.51, 0.43), (0.10, 0.16, 0.13), (0.28, 0.35, 0.30)),
    }
    accent, paper, mauve, ink, muted = palettes.get(template, palettes["synclift"])
    page = None
    y = 0.0

    def initials() -> str:
        words = str(info.get("name") or "Your Name").split()
        return "".join(word[0].upper() for word in words[:2]) or "YN"

    def left_block(title: str, text: str, top: float, max_lines: int = 16) -> float:
        """Draw sidebar content line-by-line so long fields cannot disappear."""
        page.insert_text(fitz.Point(14, top + 10), title.upper(), fontname="hebo", fontsize=10, color=(0.96, 0.94, 0.93))
        page.draw_line(fitz.Point(14, top + 18), fitz.Point(sidebar - 14, top + 18), color=(0.96, 0.94, 0.93), width=.7)
        lines: list[str] = []
        for raw_line in str(text or "").splitlines() or [""]:
            lines.extend(textwrap.wrap(raw_line, width=24, break_long_words=True, break_on_hyphens=False) or [""])
        for index, line in enumerate(lines[:max_lines]):
            page.insert_text(fitz.Point(14, top + 36 + index * 11), line, fontname="helv", fontsize=8.3, color=(0.96, 0.94, 0.93))
        return top + 36 + min(len(lines), max_lines) * 11 + 14

    def shell() -> None:
        nonlocal page, y
        page = document.new_page(width=width, height=height)
        page.draw_rect(fitz.Rect(0, 0, sidebar, height), color=mauve, fill=mauve)
        page.draw_rect(fitz.Rect(sidebar, 0, width, height), color=paper, fill=paper)
        photo = info.get("photo_data_url")
        if isinstance(photo, str) and photo.startswith("data:image/"):
            try:
                page.insert_image(fitz.Rect(42, 29, 128, 115), stream=base64.b64decode(photo.split(",", 1)[1]))
                page.draw_circle(fitz.Point(sidebar / 2, 72), 43, color=(0.95, 0.92, 0.90), width=1.4)
            except Exception:
                photo = None
        if not photo:
            page.draw_circle(fitz.Point(sidebar / 2, 72), 43, color=(0.95, 0.92, 0.90), fill=(0.95, 0.92, 0.90), width=1)
            page.insert_text(fitz.Point(sidebar / 2 - 14, 79), initials(), fontname="hebo", fontsize=19, color=mauve)
        sidebar_y = left_block("Profile", str(draft.summary or "Add a focused profile summary in CareerOS Resume Builder."), 185, 16)
        sidebar_y = left_block("Contact me", "\n".join(filter(None, [str(info.get("phone") or ""), str(info.get("email") or ""), str(info.get("location") or "")])), sidebar_y, 7)
        left_block("Links", "\n".join(filter(None, [str(info.get("github") or ""), str(info.get("linkedin") or ""), str(info.get("portfolio") or "")])), sidebar_y, 7)
        y = 34

    def next_page() -> None:
        shell()

    def fit(text: str, size: float = 9.4, bold: bool = False, color=ink, gap: float = 5) -> None:
        nonlocal y
        if not text:
            return
        if height - y - 34 < 70:
            next_page()
        rect = fitz.Rect(main_left, y, width - main_right, height - 34)
        remaining = page.insert_textbox(rect, text, fontname="hebo" if bold else "helv", fontsize=size, color=color, lineheight=1.28)
        if remaining < 0:
            next_page()
            rect = fitz.Rect(main_left, y, width - main_right, height - 34)
            remaining = page.insert_textbox(rect, text, fontname="hebo" if bold else "helv", fontsize=size, color=color, lineheight=1.28)
        used = rect.height - max(0, remaining)
        y += max(size * 1.55, used) + gap

    def heading(title: str) -> None:
        nonlocal y
        if y + 28 > height - 34:
            next_page()
        page.insert_text(fitz.Point(main_left, y + 11), f"> {title.upper()}", fontname="hebo", fontsize=10.5, color=accent)
        page.draw_line(fitz.Point(main_left, y + 17), fitz.Point(width - main_right, y + 17), color=accent, width=.55)
        y += 25

    shell()
    name = str(info.get("name") or "YOUR NAME").upper()
    fit(name, 20, True, ink, 0)
    fit(str(info.get("headline") or "Professional candidate | CareerOS resume"), 10.2, False, muted, 7)
    if draft.skills:
        heading("Skills")
        fit(" | ".join(str(skill) for skill in draft.skills if skill), 9.2, False, ink, 8)
    if draft.projects:
        heading("Projects")
        for project in draft.projects:
            if not isinstance(project, dict):
                fit(str(project), 9.2, True); continue
            project_name = _as_text(project.get("name"))
            tech = _as_text(project.get("tech_stack"))
            fit(project_name + (f"  /  {tech}" if tech else ""), 10.2, True, ink, 1)
            fit(_as_text(project.get("description")), 9.1, False, ink, 2)
            if project.get("link"):
                fit(_as_text(project.get("link")), 8.1, False, (0.35, 0.22, 0.40), 5)
    if draft.experience:
        heading("Experience")
        for job in draft.experience:
            if not isinstance(job, dict):
                fit(str(job), 9.2, True); continue
            title = " - ".join(filter(None, [_as_text(job.get("role")), _as_text(job.get("company"))]))
            fit(title, 10.0, True, ink, 1)
            fit(" | ".join(filter(None, [_as_text(job.get("start")), _as_text(job.get("end"))])), 8.3, False, muted, 2)
            bullets = job.get("bullets", [])
            if isinstance(bullets, str):
                bullets = bullets.splitlines()
            for bullet in bullets if isinstance(bullets, list) else []:
                fit(f"- {bullet}", 9.0, False, ink, 1)
            y += 3
    if draft.education:
        heading("Education")
        for item in draft.education:
            if not isinstance(item, dict):
                fit(str(item), 9.2); continue
            fit(" - ".join(filter(None, [_as_text(item.get("degree")), _as_text(item.get("institution"))])), 9.7, True, ink, 1)
            fit(" | ".join(filter(None, [_as_text(item.get("field")), " - ".join(filter(None, [_as_text(item.get("start")), _as_text(item.get("end"))]))])), 8.4, False, muted, 4)
    if draft.certifications:
        heading("Certifications")
        for certificate in draft.certifications:
            fit(f"- {_as_text(certificate)}", 9.0, False, ink, 2)
    if draft.achievements:
        heading("Achievements")
        for achievement in draft.achievements:
            fit(f"- {_as_text(achievement)}", 9.0, False, ink, 2)
    return document.tobytes(garbage=4, deflate=True)


def _render_template_docx(draft: ResumeDraft) -> bytes:
    """DOCX companion with the same sidebar/right-content structure."""
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
    from docx.shared import Inches, Pt, RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    def shade(cell, color: str) -> None:
        properties = cell._tc.get_or_add_tcPr()
        node = OxmlElement("w:shd"); node.set(qn("w:fill"), color); properties.append(node)

    def para(cell, text: str, size: float = 10, bold: bool = False, color: str = "302D2D"):
        p = cell.add_paragraph(); p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text); run.bold = bold; run.font.size = Pt(size); run.font.color.rgb = RGBColor.from_string(color)
        return p

    info = draft.personal_info or {}
    document = Document()
    section = document.sections[0]
    section.top_margin = section.bottom_margin = Inches(.35)
    section.left_margin = section.right_margin = Inches(.35)
    table = document.add_table(rows=1, cols=2)
    table.autofit = False
    left, right = table.rows[0].cells
    left.width, right.width = Inches(2.05), Inches(5.6)
    shade(left, "938385"); shade(right, "F7F0EC")
    left.vertical_alignment = right.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    para(left, "", 18)
    para(left, "  " + "".join(word[:1].upper() for word in str(info.get("name") or "Your Name").split()[:2]), 26, True, "F7F0EC")
    para(left, "", 18)
    para(left, "PROFILE", 11, True, "F7F0EC")
    para(left, str(draft.summary or "Add a focused profile summary in CareerOS Resume Builder."), 9, False, "F7F0EC")
    para(left, "CONTACT ME", 11, True, "F7F0EC")
    para(left, "\n".join(filter(None, [str(info.get("phone") or ""), str(info.get("email") or ""), str(info.get("location") or "")])), 9, False, "F7F0EC")
    para(left, "LINKS", 11, True, "F7F0EC")
    para(left, "\n".join(filter(None, [str(info.get("github") or ""), str(info.get("linkedin") or ""), str(info.get("portfolio") or "")])), 8.5, False, "F7F0EC")
    para(right, str(info.get("name") or "YOUR NAME").upper(), 22, True)
    para(right, str(info.get("headline") or "Professional candidate | CareerOS resume"), 11, False, "6B5A55")

    def section_block(title: str, entries: list[str]) -> None:
        if not entries:
            return
        para(right, f"> {title.upper()}", 11, True, "9E603B")
        for entry in entries:
            para(right, entry, 9.5)

    section_block("Skills", [" | ".join(str(skill) for skill in draft.skills if skill)] if draft.skills else [])
    projects = []
    for project in draft.projects or []:
        if isinstance(project, dict):
            projects += [" - ".join(filter(None, [_as_text(project.get("name")), _as_text(project.get("tech_stack"))])), _as_text(project.get("description"))]
        else: projects.append(_as_text(project))
    section_block("Projects", [entry for entry in projects if entry])
    experience = []
    for job in draft.experience or []:
        if isinstance(job, dict):
            experience.append(" - ".join(filter(None, [_as_text(job.get("role")), _as_text(job.get("company"))])))
            bullets = job.get("bullets", [])
            experience += [f"- {bullet}" for bullet in (bullets.splitlines() if isinstance(bullets, str) else bullets) if bullet]
        else: experience.append(_as_text(job))
    section_block("Experience", [entry for entry in experience if entry])
    education = []
    for item in draft.education or []:
        education.append(" - ".join(filter(None, [_as_text(item.get("degree")), _as_text(item.get("institution"))])) if isinstance(item, dict) else _as_text(item))
    section_block("Education", [entry for entry in education if entry])
    section_block("Certifications", [_as_text(item) for item in draft.certifications or []])
    section_block("Achievements", [_as_text(item) for item in draft.achievements or []])
    output = BytesIO(); document.save(output)
    return output.getvalue()


@router.post("/export")
def export_draft(format: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    draft = db.query(ResumeDraft).filter(ResumeDraft.user_id == current_user.id).first()
    if draft is None:
        raise HTTPException(status_code=404, detail="Save a resume draft before exporting it.")
    _sync_builder_skills(db, current_user.id, draft.skills or []); db.commit()
    if format == "docx":
        return Response(_render_template_docx(draft), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": "attachment; filename=careeros-resume.docx"})
    if format == "pdf":
        pdf = _render_template_pdf(draft)
        return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=careeros-resume.pdf"})
    raise HTTPException(status_code=422, detail="Choose PDF or DOCX export.")
