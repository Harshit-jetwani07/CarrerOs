"""
Run once after your first migration to populate the roles/skills tables:

    python seed.py

Safe to re-run — it upserts by name instead of duplicating rows.
"""
from app.database import SessionLocal
# Import every SQLAlchemy model before querying. Relationship targets such as
# UserSkill -> User are string-based and must all be registered first.
from app.models import user, skill, role, resume, roadmap, job  # noqa: F401
from app.models.skill import Skill
from app.models.role import Role, RoleSkill
from app.data.seed_roles import ROLES


def get_or_create_skill(db, name: str) -> Skill:
    skill = db.query(Skill).filter(Skill.name == name).first()
    if skill is None:
        skill = Skill(name=name)
        db.add(skill)
        db.flush()
    return skill


def main():
    db = SessionLocal()
    try:
        for role_name, data in ROLES.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            if role is None:
                role = Role(name=role_name, description=data["description"])
                db.add(role)
                db.flush()

            for skill_name, importance in data["skills"].items():
                skill = get_or_create_skill(db, skill_name)
                existing_link = (
                    db.query(RoleSkill)
                    .filter(RoleSkill.role_id == role.id, RoleSkill.skill_id == skill.id)
                    .first()
                )
                if existing_link is None:
                    db.add(RoleSkill(role_id=role.id, skill_id=skill.id, importance=importance))

        db.commit()
        print(f"Seeded {len(ROLES)} roles with their required skills.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
