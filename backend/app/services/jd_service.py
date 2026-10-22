"""Evidence-based Job Description matching.

The offline path compares requirements, not just isolated skill words. This
prevents one broad keyword such as "Machine Learning" from turning a whole JD
into a misleading 100% match.
"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.models.job import JobDescription
from app.models.resume import Resume
from app.models.skill import UserSkill
from app.services import ai_service
from app.services.skill_alias import SKILL_ALIASES, canonicalize


# label, score weight, direct resume terms, related tracked-skill evidence
ML_REQUIREMENTS = [
    ("Programming fundamentals", 15, ("python", "c++", "java", "programming", "data structures", "algorithms"), ("python", "c++", "java", "sql")),
    ("Machine Learning", 20, ("machine learning", "ml", "scikit", "tensorflow", "pytorch"), ("machine learning", "pytorch")),
    ("Data preprocessing", 15, ("preprocessing", "data cleaning", "feature engineering", "data preparation"), ("pandas", "python")),
    ("Model development", 15, ("model development", "model building", "trained", "training models", "built model"), ("machine learning", "pytorch")),
    ("Model evaluation", 10, ("model evaluation", "evaluation", "accuracy", "precision", "recall", "f1 score", "metrics"), ("machine learning", "statistics")),
    ("ML deployment", 10, ("model deployment", "deploy", "fastapi", "flask", "docker", "rest api"), ("docker", "rest apis")),
    ("Production ML environment", 10, ("production", "production environment", "monitoring", "mlops"), ("docker", "aws")),
    ("Scalable ML applications", 5, ("scalable", "scale", "distributed", "high availability", "load balancing"), ("aws", "docker")),
]


def _has_any(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text)]


def _requirements_for_jd(raw_text: str, extracted: list[str]) -> list[tuple[str, int, tuple[str, ...], tuple[str, ...]]]:
    """Create a visible requirement list from the actual pasted JD."""
    lowered = raw_text.lower()
    is_ml = "machine learning" in lowered or "ml models" in lowered or "ml model" in lowered
    requirements = list(ML_REQUIREMENTS) if is_ml else []
    known_terms = {term for _, _, terms, _ in requirements for term in terms}

    for skill in extracted:
        canonical = canonicalize(skill)
        if canonical in known_terms:
            continue
        terms = tuple({canonical, *SKILL_ALIASES.get(canonical, set())})
        requirements.append((skill, 10, terms, (canonical,)))
    return requirements


def _resume_evidence(db: Session, user_id: int) -> tuple[str, set[str]]:
    resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc()).first()
    resume_text = (resume.raw_text or "").lower() if resume else ""
    user_skills = {canonicalize(item.skill.name) for item in db.query(UserSkill).filter(UserSkill.user_id == user_id).all()}
    return resume_text, user_skills


def _evaluate(label: str, weight: int, terms: tuple[str, ...], support: tuple[str, ...], resume_text: str, user_skills: set[str]) -> dict:
    direct = _has_any(resume_text, terms)
    related = [skill for skill in support if canonicalize(skill) in user_skills]
    if direct:
        return {"label": label, "status": "matched", "weight": weight, "evidence": f"Resume mentions {', '.join(direct[:2])}."}
    if related:
        return {"label": label, "status": "partial", "weight": weight, "evidence": f"Related evidence found: {', '.join(related[:2])}; this requirement is not explicit in the resume."}
    return {"label": label, "status": "missing", "weight": weight, "evidence": "No explicit evidence found in the current resume or tracked skills."}


def _recommendation(score: int, partial: list[str], missing: list[str]) -> str:
    focus = (missing + partial)[:2]
    if score >= 90 and not missing:
        return "Very strong match. Make the partial evidence explicit before applying."
    if score >= 70:
        return f"Good match overall. Strengthen proof for {', '.join(focus)} before applying." if focus else "Good match overall; tailor your resume to this job before applying."
    return f"There are meaningful gaps. Prioritize {', '.join(focus)} before applying." if focus else "Add more relevant evidence to your resume before applying."


def analyze_jd(db: Session, user_id: int, title: str | None, raw_text: str) -> JobDescription:
    extracted = ai_service.extract_jd_skills(db, user_id, raw_text)
    resume_text, user_skills = _resume_evidence(db, user_id)
    breakdown = [_evaluate(label, weight, terms, support, resume_text, user_skills) for label, weight, terms, support in _requirements_for_jd(raw_text, extracted)]
    total = sum(item["weight"] for item in breakdown)
    earned = sum(item["weight"] if item["status"] == "matched" else item["weight"] * 0.45 if item["status"] == "partial" else 0 for item in breakdown)
    score = round((earned / total) * 100) if total else 0
    matched = [item["label"] for item in breakdown if item["status"] == "matched"]
    partial = [item["label"] for item in breakdown if item["status"] == "partial"]
    missing = [item["label"] for item in breakdown if item["status"] == "missing"]

    jd = JobDescription(user_id=user_id, title=title, raw_text=raw_text, extracted_skills=extracted, match_score=score, matched_skills=matched, missing_skills=missing, requirement_breakdown=breakdown, recommendation=_recommendation(score, partial, missing))
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return jd
