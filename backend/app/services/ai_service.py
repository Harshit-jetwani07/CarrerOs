"""
Provider-agnostic AI layer. Every other service calls INTO this module,
never directly into an SDK — so swapping OpenAI for Gemini/Claude later
means changing this one file, not the whole codebase.

If no OPENAI_API_KEY is set, every function falls back to a deterministic
stub response so the rest of the app keeps working during local dev /
demos without burning API credits.
"""
import json
import re
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.crypto import decrypt_key
from app.models.api_key import UserApiKey
from app.services.skill_alias import SKILL_ALIASES
from app.services.providers import get_provider


def active_provider(db: Session, user_id: int) -> str | None:
    saved = db.query(UserApiKey).filter(UserApiKey.user_id == user_id).order_by(UserApiKey.is_default.desc(), UserApiKey.created_at.asc()).first()
    return saved.provider if saved else None

def _matching_snippets(raw_text: str, pattern: str, limit: int = 3) -> list[str]:
    """Return a few unique, readable resume lines that match a section."""
    snippets: list[str] = []
    seen: set[str] = set()
    for line in raw_text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip(" -•\t")
        if len(cleaned) < 12 or not re.search(pattern, cleaned, re.IGNORECASE):
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        snippets.append(f"{cleaned[:177].rstrip()}…" if len(cleaned) > 178 else cleaned)
        if len(snippets) == limit:
            break
    return snippets


def _chat_json(db: Session, user_id: int, system_prompt: str, user_prompt: str, fallback: dict) -> dict:
    """Use the account's selected provider, or the deterministic no-key path."""
    saved = db.query(UserApiKey).filter(UserApiKey.user_id == user_id).order_by(UserApiKey.is_default.desc(), UserApiKey.created_at.asc()).first()
    if saved is None:
        return fallback
    try:
        result = get_provider(saved.provider, decrypt_key(saved.encrypted_key)).chat_json(system_prompt, user_prompt)
        saved.last_used_at = datetime.now(timezone.utc)
        db.commit()
        return result
    except Exception:
        # Provider errors are deliberately surfaced to the caller; do not hide
        # a rejected user key behind the no-key pattern-matching result.
        db.rollback()
        raise


def analyze_resume(db: Session, user_id: int, raw_text: str) -> dict:
    """Turn raw resume text into a structured analysis: scores + parsed profile."""
    system_prompt = (
        "You are a resume analysis engine for a career platform. "
        "Given raw resume text, return ONLY a JSON object with this exact shape: "
        '{"overall_score": int 0-100, "ats_score": int 0-100, '
        '"category_scores": {"skills": int, "projects": int, "experience": int, '
        '"education": int, "achievements": int, "resume_quality": int}, '
        '"parsed_profile": {"education": [], "skills": [], "projects": [], '
        '"experience": [], "certifications": [], "achievements": []}, '
        '"strengths": [string], "weaknesses": [string], '
        '"bullet_rewrites": [{"before": string, "after": string}]}. '
        "Be specific and honest, not generic."
    )
    lowered = raw_text.lower()
    discovered = []
    for canonical, aliases in SKILL_ALIASES.items():
        terms = {canonical, *aliases}
        if any(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", lowered) for term in terms):
            discovered.append(canonical.title() if canonical != "rest apis" else "REST APIs")
    project_pattern = r"\b(projects?|built|developed)\b"
    experience_pattern = r"\b(experience|internship|worked)\b"
    project_count = len(re.findall(project_pattern, lowered))
    experience_count = len(re.findall(experience_pattern, lowered))
    project_snippets = _matching_snippets(raw_text, project_pattern)
    experience_snippets = _matching_snippets(raw_text, experience_pattern)
    if project_count and not project_snippets:
        project_snippets = [
            f"Project-related content appears in {project_count} place"
            f"{'s' if project_count != 1 else ''} in this resume."
        ]
    if experience_count and not experience_snippets:
        experience_snippets = [
            f"Experience-related content appears in {experience_count} place"
            f"{'s' if experience_count != 1 else ''} in this resume."
        ]
    education_present = bool(re.search(r"\b(b\.?(tech|e)|bachelor|university|college|education)\b", lowered))
    skills_score = min(100, 35 + len(discovered) * 7)
    projects_score = min(100, 25 + project_count * 12)
    experience_score = min(100, 20 + experience_count * 15)
    education_score = 80 if education_present else 40
    category_scores = {"skills": skills_score, "projects": projects_score, "experience": experience_score, "education": education_score, "achievements": 45, "resume_quality": min(95, 42 + len(raw_text) // 220)}
    fallback = {
        "overall_score": round(sum(category_scores.values()) / len(category_scores)),
        "ats_score": min(95, 35 + len(discovered) * 6 + (10 if education_present else 0)),
        "category_scores": category_scores,
        "parsed_profile": {
            "education": ["An education section was found in this resume."] if education_present else [],
            "skills": discovered,
            "projects": project_snippets,
            "experience": experience_snippets,
            "certifications": [],
            "achievements": [],
        },
        "strengths": [
            f"Found {len(discovered)} recognizable skills in your resume text.",
        ],
        "weaknesses": [
            "This is a quick text-based scan, so it is a useful first pass but may miss details a deeper review could catch.",
        ],
        "bullet_rewrites": [],
    }
    return _chat_json(db, user_id, system_prompt, raw_text[:12000], fallback)


def extract_jd_skills(db: Session, user_id: int, jd_text: str) -> list[str]:
    """Extract a flat list of required/desired skills from a job description."""
    system_prompt = (
        "Extract the technical skills, tools and frameworks required or "
        "preferred in this job description. Return ONLY JSON: "
        '{"skills": [string, ...]}. Use canonical names (e.g. "PostgreSQL" '
        'not "postgres db").'
    )
    lowered = jd_text.lower()
    fallback = {"skills": [canonical.title() if canonical != "rest apis" else "REST APIs" for canonical, aliases in SKILL_ALIASES.items() if any(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", lowered) for term in {canonical, *aliases})]}
    result = _chat_json(db, user_id, system_prompt, jd_text[:8000], fallback)
    return result.get("skills", [])


def enrich_roadmap_topic(db: Session, user_id: int, topic: str, current_level: str, target_role: str) -> dict:
    """Ask the AI to flesh out one roadmap topic with practice + project ideas."""
    system_prompt = (
        "You help build career-development roadmaps. Given a skill topic, the "
        "learner's current level, and their target role, return ONLY JSON: "
        '{"why_needed": string, "practice_task": string, '
        '"project_suggestion": string, "estimated_days": int}. Keep each '
        "string to one or two sentences."
    )
    user_prompt = (
        f"Topic: {topic}\nCurrent level: {current_level}\n"
        f"Target role: {target_role}"
    )
    fallback = {
        "why_needed": f"{topic} is a required skill for {target_role}.",
        "practice_task": f"Build a small project focused only on {topic}.",
        "project_suggestion": f"Add a {topic}-focused feature to an existing project.",
        "estimated_days": 5,
    }
    return _chat_json(db, user_id, system_prompt, user_prompt, fallback)


def enrich_roadmap_batch(db: Session, user_id: int, gaps: list[dict], target_role: str) -> list[dict]:
    """Enrich all roadmap topics in one call to keep planning fast and coherent."""
    fallback = {"items": [{
        "skill": gap["skill"],
        "why_needed": f"{gap['skill']} is a required skill for {target_role}.",
        "practice_task": f"Build a small project focused on {gap['skill']}.",
        "project_suggestion": f"Add a {gap['skill']}-focused feature to an existing project.",
        "subtopics": [],
        "estimated_days": 5,
    } for gap in gaps]}
    if not gaps:
        return []
    result = _chat_json(
        db, user_id,
        "Return ONLY JSON: {\"items\":[{\"skill\":string,\"why_needed\":string,\"practice_task\":string,\"project_suggestion\":string,\"subtopics\":[string,string,string,string],\"estimated_days\":int}]}. Give four short, ordered study subtopics for each supplied gap. Keep one item per supplied gap, in the same order.",
        json.dumps({"target_role": target_role, "gaps": gaps}),
        fallback,
    )
    items = result.get("items", [])
    return items if isinstance(items, list) else fallback["items"]


def generate_recommendation(match_score: int, missing_skills: list[str]) -> str:
    """One-line human recommendation for a JD match result."""
    if not missing_skills:
        return "Strong match — your profile already covers the key requirements."
    if match_score >= 75:
        return (
            f"You're reasonably qualified, but adding "
            f"{', '.join(missing_skills[:2])} would significantly improve your match."
        )
    return (
        f"There's a meaningful skill gap here. Focus on "
        f"{', '.join(missing_skills[:3])} before applying."
    )


def career_assistant_reply(db: Session, user_id: int, context: str, message: str) -> str:
    if not active_provider(db, user_id):
        raise ValueError("Connect an API key in Settings to use the Career Assistant.")
    result = _chat_json(db, user_id, "You are CareerOS's career assistant. Use ONLY the supplied user facts. If a fact is missing, say so instead of guessing. Keep the answer concise and specific. Return ONLY JSON: {\"reply\": string}.", f"USER FACTS:\n{context}\n\nQUESTION:\n{message}", {})
    reply = result.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise ValueError("The provider returned an unusable answer. Please try again.")
    return reply.strip()


def improve_resume_summary(db: Session, user_id: int, summary: str, headline: str, skills: list[str]) -> str:
    """Rewrite only user-provided resume facts using the user's chosen provider."""
    if not active_provider(db, user_id):
        raise ValueError("Connect an API key in Settings to use AI improvements.")
    result = _chat_json(
        db, user_id,
        "You are an expert resume writer. Return ONLY JSON: {\"summary\": string}. "
        "Rewrite the supplied profile into 2 or 3 concise ATS-friendly sentences. "
        "Use only supplied facts; do not invent employers, years, achievements, or tools.",
        json.dumps({"headline": headline, "skills": skills[:20], "current_summary": summary}),
        {},
    )
    improved = result.get("summary")
    if not isinstance(improved, str) or not improved.strip():
        raise ValueError("The provider returned an unusable rewrite. Please try again.")
    return improved.strip()
