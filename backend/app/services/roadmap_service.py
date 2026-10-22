"""
Turns a skill gap list into a week-by-week roadmap. Each topic is
enriched via the AI layer with why/practice/project fields, falling
back to sensible static text when no AI key is configured.
"""
from sqlalchemy.orm import Session

from app.models.roadmap import Roadmap, RoadmapItem
from app.services import ai_service
from app.services.skill_gap_service import compute_skill_gap
from app.models.role import Role


SUBTOPIC_LIBRARY = {
    "postgresql": ["Tables, data types, keys and constraints", "SELECT queries, joins, grouping and subqueries", "Indexes, query plans and transactions", "Design a normalized schema for a real feature"],
    "docker": ["Images, containers, volumes and ports", "Write a Dockerfile for an API", "Docker Compose for API plus database", "Environment variables, logs and production basics"],
    "rest apis": ["HTTP methods, status codes and resource design", "Request validation and consistent error responses", "Authentication and authorization flow", "Document and test an API endpoint"],
    "aws": ["IAM users, roles and least-privilege access", "Core services: EC2, S3 and RDS", "Deploy a small API with environment variables", "Monitoring, cost awareness and security basics"],
    "machine learning": ["Problem framing and train/test split", "Feature preparation and baseline models", "Training, validation and common metrics", "Package a reproducible model workflow"],
    "python": ["Functions, modules and virtual environments", "Data structures and error handling", "Write clean, testable application code", "Build a small automation or API utility"],
    "react": ["Components, props and state", "Effects, forms and data fetching", "Reusable UI patterns and routing", "Ship a responsive feature with error states"],
    "sql": ["SELECT, filtering and sorting", "Joins, aggregates and subqueries", "Schema design and constraints", "Analyze a realistic dataset with SQL"],
}


def _subtopics(topic: str) -> list[str]:
    """Give every offline roadmap a concrete study structure, not filler text."""
    normalized = topic.strip().lower()
    if normalized in SUBTOPIC_LIBRARY:
        return SUBTOPIC_LIBRARY[normalized]
    return [
        f"Core concepts and vocabulary for {topic}",
        f"Hands-on exercises using {topic}",
        f"Common mistakes, testing and debugging in {topic}",
        f"Add a measurable {topic} feature to a portfolio project",
    ]


def generate_roadmap(db: Session, user_id: int, role_name: str, total_weeks: int = 8) -> Roadmap:
    if total_weeks not in {4, 8, 12, 16}:
        raise ValueError("Choose a 4, 8, 12, or 16-week roadmap.")
    gap = compute_skill_gap(db, user_id, role_name)
    role = db.query(Role).filter(Role.name == role_name).first()

    # Existing roadmap for this user+role gets replaced, not duplicated.
    existing = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == user_id, Roadmap.role_id == role.id)
        .first()
    )
    if existing:
        db.delete(existing)
        db.flush()

    roadmap = Roadmap(user_id=user_id, role_id=role.id, total_weeks=total_weeks)
    db.add(roadmap)
    db.flush()  # get roadmap.id before adding items

    enrichments = ai_service.enrich_roadmap_batch(db, user_id, gap["gaps"], role_name)
    by_skill = {str(item.get("skill", "")).lower(): item for item in enrichments if isinstance(item, dict)}
    gaps = gap["gaps"] or [{"skill": "Career foundation", "user_level": 0}]
    for week in range(1, total_weeks + 1):
        # Spread every real gap across the chosen timeframe; shorter plans
        # revisit the same gap more intensely instead of dropping content.
        gap_item = gaps[min(len(gaps) - 1, ((week - 1) * len(gaps)) // total_weeks)]
        current_level = "Beginner" if gap_item["user_level"] < 30 else "Intermediate"
        enrichment = by_skill.get(gap_item["skill"].lower(), {})
        db.add(RoadmapItem(
            roadmap_id=roadmap.id,
            week_number=week,
            topic=gap_item["skill"],
            why_needed=enrichment.get("why_needed"),
            current_level=current_level,
            target_level="Intermediate",
            estimated_days=max(2, round(7 / max(1, total_weeks / 8))),
            practice_task=enrichment.get("practice_task"),
            project_suggestion=enrichment.get("project_suggestion"),
            subtopics=enrichment.get("subtopics") if isinstance(enrichment.get("subtopics"), list) and enrichment.get("subtopics") else _subtopics(gap_item["skill"]),
        ))

    db.commit()
    db.refresh(roadmap)
    return roadmap
