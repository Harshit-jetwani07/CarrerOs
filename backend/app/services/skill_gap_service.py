"""
Compares a user's current skills against a target role's requirements
and buckets the gaps into HIGH / MEDIUM / LOW priority using the role's
per-skill importance weight.
"""
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.skill import UserSkill
from app.services.skill_alias import canonicalize


def _priority_for(importance: float) -> str:
    if importance >= 0.7:
        return "HIGH"
    if importance >= 0.4:
        return "MEDIUM"
    return "LOW"


def compute_skill_gap(db: Session, user_id: int, role_name: str) -> dict:
    role = db.query(Role).filter(Role.name == role_name).first()
    if role is None:
        raise ValueError(f"Unknown role: {role_name}")

    user_skills = {
        canonicalize(us.skill.name): us.proficiency
        for us in db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    }

    matched = []
    gaps = []
    for rs in role.required_skills:
        name = rs.skill.name
        user_level = int(user_skills.get(canonicalize(name), 0))
        if user_level >= 60:
            matched.append(name)
        if user_level < 60:
            gaps.append({
                "skill": name,
                "priority": _priority_for(rs.importance),
                "user_level": user_level,
                "required_level": 70,
                "status": "missing" if user_level == 0 else "developing",
            })

    # HIGH priority first, then MEDIUM, then LOW
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    gaps.sort(key=lambda g: order[g["priority"]])

    return {
        "role_name": role.name,
        "matched_skills": matched,
        "gaps": gaps,
    }
