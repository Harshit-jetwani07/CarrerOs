"""Auditable skill-name normalization shared by resumes, roles and job descriptions."""

SKILL_ALIASES: dict[str, set[str]] = {
    "python": {"python3", "py"}, "sql": {"structured query language"},
    "git": {"git scm"}, "rest apis": {"rest api", "restful api", "restful apis", "rest"},
    "postgresql": {"postgres", "postgres db", "psql"}, "docker": {"docker containers"},
    "authentication": {"auth", "user authentication"}, "testing": {"unit testing", "tests"},
    "aws": {"amazon web services"}, "redis": {"redis cache"},
    "javascript": {"js", "java script"}, "react": {"reactjs", "react.js"},
    "typescript": {"ts", "type script"}, "html": {"html5"}, "css": {"css3"},
    "next.js": {"nextjs", "next js"}, "excel": {"microsoft excel"},
    "statistics": {"statistical analysis"}, "data visualization": {"data visualisation", "visualization"},
    "pandas": {"pandas python"}, "machine learning": {"ml", "machine-learning"},
    "pytorch": {"py torch"}, "node.js": {"nodejs", "node js", "node"},
}


def canonicalize(name: str) -> str:
    """Return a stable comparison key while preserving unknown skill names."""
    normalized = " ".join(name.strip().lower().split())
    for canonical, aliases in SKILL_ALIASES.items():
        if normalized == canonical or normalized in aliases:
            return canonical
    return normalized
