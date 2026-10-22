from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis
from app.models.skill import Skill, UserSkill
from app.services.skill_alias import canonicalize
from app.schemas.resume import ResumeOut
from app.services import resume_parser, ai_service
from app.services.providers.base import ProviderError

router = APIRouter(prefix="/api/resume", tags=["resume"])

MAX_FILE_SIZE_MB = 5
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _validate_upload(file: UploadFile, file_bytes: bytes) -> None:
    name = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()
    is_pdf = name.endswith(".pdf") and file_bytes.startswith(b"%PDF-")
    is_docx = name.endswith(".docx") and file_bytes.startswith(b"PK\\x03\\x04")
    if not (is_pdf or is_docx):
        raise HTTPException(status_code=400, detail="Upload a real PDF or DOCX resume file.")
    if content_type and content_type not in ALLOWED_CONTENT_TYPES and content_type != "application/octet-stream":
        raise HTTPException(status_code=400, detail="The uploaded file type does not match a PDF or DOCX resume.")


def _sync_skills_from_resume(db: Session, user_id: int, skill_names: list[str]) -> int:
    """Persist evidence-backed resume skills once so all downstream tools agree."""
    synced = 0
    known = {canonicalize(skill.name): skill for skill in db.query(Skill).all()}
    for raw_name in skill_names:
        if not isinstance(raw_name, str) or not raw_name.strip():
            continue
        key = canonicalize(raw_name)
        skill = known.get(key)
        if skill is None:
            skill = Skill(name=raw_name.strip())
            db.add(skill)
            db.flush()
            known[key] = skill
        link = db.query(UserSkill).filter(UserSkill.user_id == user_id, UserSkill.skill_id == skill.id).first()
        if link is None:
            db.add(UserSkill(user_id=user_id, skill_id=skill.id, proficiency=65, evidence_source="resume"))
            synced += 1
        else:
            link.proficiency = max(link.proficiency, 65)
            if link.evidence_source not in {"resume", "manual"}:
                link.evidence_source = "resume"
            synced += 1
    return synced


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large (max {MAX_FILE_SIZE_MB}MB).")
    _validate_upload(file, file_bytes)

    try:
        raw_text = resume_parser.extract_text(file.filename, file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Couldn't extract any text from this file.")

    resume = Resume(user_id=current_user.id, filename=file.filename, raw_text=raw_text)
    db.add(resume)
    db.flush()

    try:
        analysis_data = ai_service.analyze_resume(db, current_user.id, raw_text)
    except ProviderError as exc:
        raise HTTPException(status_code=422, detail=exc.reason) from exc
    analysis = ResumeAnalysis(
        resume_id=resume.id,
        overall_score=analysis_data.get("overall_score", 0),
        ats_score=analysis_data.get("ats_score", 0),
        category_scores=analysis_data.get("category_scores", {}),
        parsed_profile=analysis_data.get("parsed_profile", {}),
        strengths=analysis_data.get("strengths", []),
        weaknesses=analysis_data.get("weaknesses", []),
        bullet_rewrites=analysis_data.get("bullet_rewrites", []),
    )
    db.add(analysis)
    parsed_skills = analysis_data.get("parsed_profile", {}).get("skills", [])
    _sync_skills_from_resume(db, current_user.id, parsed_skills if isinstance(parsed_skills, list) else [])
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/latest", response_model=ResumeOut)
def get_latest_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    if resume is None:
        raise HTTPException(status_code=404, detail="No resume uploaded yet.")
    return resume


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove one user-owned resume and its analysis without touching other account data."""
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    has_another_resume = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.id != resume.id,
    ).first() is not None
    db.delete(resume)
    # Skills added by the user stay. Auto-detected skills are removed only when
    # the user no longer has any resume supporting them.
    if not has_another_resume:
        db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id,
            UserSkill.evidence_source == "resume",
        ).delete(synchronize_session=False)
    db.commit()
    return {"deleted": resume_id}
