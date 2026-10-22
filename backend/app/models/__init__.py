"""Import all models so SQLAlchemy can resolve cross-model relationships."""
from . import api_key, assistant, job, resume, resume_draft, roadmap, role, skill, user  # noqa: F401
