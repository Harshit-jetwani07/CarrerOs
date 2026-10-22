from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.schemas.role import SkillGapOut
from app.services.skill_gap_service import compute_skill_gap

router = APIRouter(prefix="/api/skills", tags=["skills"])


class UserSkillIn(BaseModel):
    skill_name: str
    proficiency: float = 50
    evidence_source: str = "manual"


@router.post("")
def upsert_skill(
    payload: UserSkillIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = db.query(Skill).filter(Skill.name == payload.skill_name).first()
    if skill is None:
        skill = Skill(name=payload.skill_name)
        db.add(skill)
        db.flush()

    link = (
        db.query(UserSkill)
        .filter(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill.id)
        .first()
    )
    if link is None:
        link = UserSkill(user_id=current_user.id, skill_id=skill.id, proficiency=payload.proficiency, evidence_source=payload.evidence_source)
        db.add(link)
    else:
        link.proficiency = payload.proficiency

    db.commit()
    return {"skill_name": skill.name, "proficiency": link.proficiency, "evidence_source": link.evidence_source}


@router.get("")
def list_my_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    links = db.query(UserSkill).filter(UserSkill.user_id == current_user.id).all()
    return [{"skill_name": l.skill.name, "proficiency": l.proficiency, "evidence_source": l.evidence_source} for l in links]


@router.delete("/{skill_name}")
def remove_skill(skill_name: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Remove a user-owned manual skill without affecting the shared skill catalogue."""
    link = db.query(UserSkill).join(UserSkill.skill).filter(UserSkill.user_id == current_user.id, Skill.name == skill_name).first()
    if link is None:
        raise HTTPException(status_code=404, detail="Skill not found.")
    db.delete(link)
    db.commit()
    return {"removed": skill_name}


@router.get("/gap/{role_name}", response_model=SkillGapOut)
def get_skill_gap(
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return compute_skill_gap(db, current_user.id, role_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
