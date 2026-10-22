"""One-call overview data built from the same services as the detailed tabs."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.resume import Resume
from app.models.roadmap import Roadmap
from app.models.skill import UserSkill
from app.models.resume_draft import ResumeDraft
from app.models.user import User
from app.services.matching_service import compute_role_matches
from app.services.skill_gap_service import compute_skill_gap

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return readiness, priority gaps and progress together for a coherent overview."""
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc()).first()
    builder_draft = db.query(ResumeDraft).filter(ResumeDraft.user_id == current_user.id, ResumeDraft.use_for_overview.is_(True)).first()
    if not resume and not builder_draft:
        return {"status": "no_data", "resume_status": {"uploaded": False, "source": "none"}}
    if not db.query(UserSkill).filter(UserSkill.user_id == current_user.id).first():
        return {"status": "no_data", "resume_status": {"uploaded": bool(resume), "source": "upload" if resume else "builder"}}
    matches = compute_role_matches(db, current_user.id)
    chosen = next((item for item in matches if item["role_name"] == current_user.target_role), matches[0] if matches else None)
    if chosen is None:
        return {"status": "no_data", "resume_status": {"uploaded": bool(resume), "source": "upload" if resume else "builder"}}
    gap = compute_skill_gap(db, current_user.id, chosen["role_name"])
    roadmap = db.query(Roadmap).join(Roadmap.role).filter(Roadmap.user_id == current_user.id, Roadmap.role.has(name=chosen["role_name"])).first()
    progress = None if roadmap is None else {"completed_weeks": sum(1 for item in roadmap.items if item.completed), "total_weeks": len(roadmap.items), "role_name": chosen["role_name"]}
    resume_status = {"uploaded": bool(resume), "source": "upload" if resume else "builder"}
    if resume and resume.analysis:
        resume_status["overall_score"] = resume.analysis.overall_score
    return {"status": "ok", "readiness": {"match_percent": chosen["match_percent"], "role_name": chosen["role_name"]}, "top_gaps": gap["gaps"][:3], "roadmap_progress": progress, "resume_status": resume_status}
