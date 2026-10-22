"""Career role matching from user skills, resume evidence and roadmap progress.

    Role Match Score = Skill Match (50%) + Project Evidence (20%)
                      + Experience (15%) + Education (5%) + Interest (10%)

Kept as plain, auditable arithmetic (not an LLM call) so every score can
be explained in a viva/interview: "here is exactly why you got 84%."
"""
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.skill import UserSkill
from app.models.resume import Resume
from app.models.resume_draft import ResumeDraft
from app.models.roadmap import Roadmap, RoadmapItem
from app.models.user import User
from app.services.skill_alias import canonicalize


WEIGHTS = {
    "skill_match": 0.50,
    "project_evidence": 0.20,
    "experience": 0.15,
    "education": 0.05,
    "interest": 0.10,
}


def _skill_match_score(user_skill_levels: dict[str, float], role: Role) -> float:
    """Weight each required skill by both role importance and user proficiency.

    A listed skill at 50% is evidence of a developing capability, not the
    same thing as the same skill at 90%. This keeps Career Match aligned with
    the level selector in the UI.
    """
    if not role.required_skills:
        return 0.0
    total_weight = sum(rs.importance for rs in role.required_skills)
    if total_weight == 0:
        return 0.0
    proficiency_weight = sum(
        rs.importance * max(0.0, min(100.0, float(user_skill_levels.get(canonicalize(rs.skill.name), 0)))) / 100
        for rs in role.required_skills
    )
    return (proficiency_weight / total_weight) * 100


def _latest_profile(db: Session, user_id: int) -> tuple[dict, bool]:
    resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc()).first()
    if not resume or not resume.analysis:
        draft = db.query(ResumeDraft).filter(ResumeDraft.user_id == user_id, ResumeDraft.use_for_overview.is_(True)).first()
        if draft:
            return {"projects": draft.projects or [], "experience": draft.experience or [], "education": draft.education or []}, True
        return {}, False
    return resume.analysis.parsed_profile or {}, True


def compute_role_matches(db: Session, user_id: int) -> list[dict]:
    """Return every role scored against this user, sorted best-first."""
    user_skills = (
        db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    )
    user_skill_levels: dict[str, float] = {}
    for user_skill in user_skills:
        key = canonicalize(user_skill.skill.name)
        user_skill_levels[key] = max(user_skill_levels.get(key, 0), float(user_skill.proficiency or 0))
    profile, has_resume = _latest_profile(db, user_id)
    projects = profile.get("projects", []) if isinstance(profile, dict) else []
    experience = profile.get("experience", []) if isinstance(profile, dict) else []
    education = profile.get("education", []) if isinstance(profile, dict) else []
    # A skill may come from manual entry or the builder, but it must never
    # pretend to be project, education, or experience evidence. Those three
    # inputs remain zero until an uploaded resume provides them.
    project_evidence_score = min(100, len(projects) * 20) if has_resume and projects else 0
    experience_score = min(100, len(experience) * 25) if experience else 0
    education_score = 85 if has_resume and education else 0
    user = db.query(User).filter(User.id == user_id).first()
    interests = [str(value).lower() for value in (user.interests or [])] if user else []

    roles = db.query(Role).all()
    results = []
    for role in roles:
        role_interest = role.name.lower()
        interest_score = 100 if any(term in role_interest or role_interest in term for term in interests) else 0
        skill_score = _skill_match_score(user_skill_levels, role)
        breakdown = {
            "skill_match": round(skill_score * WEIGHTS["skill_match"]),
            "project_evidence": round(project_evidence_score * WEIGHTS["project_evidence"]),
            "experience": round(experience_score * WEIGHTS["experience"]),
            "education": round(education_score * WEIGHTS["education"]),
            "interest": round(interest_score * WEIGHTS["interest"]),
        }
        base_match_percent = sum(breakdown.values())
        roadmap = db.query(Roadmap).filter(Roadmap.user_id == user_id, Roadmap.role_id == role.id).first()
        items = roadmap.items if roadmap else []
        roadmap_bonus = round((sum(1 for item in items if item.completed) / len(items)) * 5) if items else 0
        breakdown["roadmap_bonus"] = roadmap_bonus
        match_percent = min(100, base_match_percent + roadmap_bonus)
        results.append({
            "role_name": role.name,
            "match_percent": match_percent,
            "base_match_percent": base_match_percent,
            "breakdown": breakdown,
        })

    return sorted(results, key=lambda r: r["match_percent"], reverse=True)
