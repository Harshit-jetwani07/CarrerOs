from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.assistant import AssistantMessage
from app.models.resume import Resume
from app.models.roadmap import Roadmap
from app.models.user import User
from app.services.ai_service import active_provider, career_assistant_reply
from app.services.matching_service import compute_role_matches
from app.services.skill_gap_service import compute_skill_gap
from app.services.providers.base import ProviderError

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None

def _context(db: Session, user: User) -> str:
    matches = compute_role_matches(db, user.id)
    chosen = next((item for item in matches if item["role_name"] == user.target_role), matches[0] if matches else None)
    if not chosen: return "No target role or score is available yet."
    gap = compute_skill_gap(db, user.id, chosen["role_name"])
    gaps = "; ".join(f"{item['skill']} ({item['priority']}, {item['user_level']}% to {item['required_level']}%)" for item in gap["gaps"][:5]) or "No recorded gaps"
    roadmap = db.query(Roadmap).join(Roadmap.role).filter(Roadmap.user_id == user.id, Roadmap.role.has(name=chosen["role_name"])).first()
    road = "No roadmap generated."
    if roadmap:
        done = sum(1 for item in roadmap.items if item.completed)
        current = next((item.topic for item in roadmap.items if not item.completed), "All roadmap items completed")
        road = f"{done}/{len(roadmap.items)} weeks complete; next focus: {current}."
    resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.uploaded_at.desc()).first()
    resume_text = "No uploaded resume analysis."
    if resume and resume.analysis:
        weakest = min(resume.analysis.category_scores, key=resume.analysis.category_scores.get, default="unknown")
        resume_text = f"Overall {resume.analysis.overall_score}/100; weakest section: {weakest}."
    return f"Target role: {chosen['role_name']} ({chosen['match_percent']}% ready). Breakdown: {chosen['breakdown']}. Top gaps: {gaps}. Roadmap: {road} Resume: {resume_text}"

@router.get("/status")
def status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    provider = active_provider(db, current_user.id)
    return {"connected": bool(provider), "provider": provider}

@router.post("/chat")
def chat(payload: ChatIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    provider = active_provider(db, current_user.id)
    if not provider: raise HTTPException(status_code=409, detail="Connect an API key in Settings to use the Career Assistant.")
    conversation_id = payload.conversation_id or str(uuid4())
    db.add(AssistantMessage(user_id=current_user.id, conversation_id=conversation_id, role="user", content=payload.message)); db.commit()
    try:
        reply = career_assistant_reply(db, current_user.id, _context(db, current_user), payload.message)
    except ProviderError as exc: raise HTTPException(status_code=422, detail=exc.reason) from exc
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.add(AssistantMessage(user_id=current_user.id, conversation_id=conversation_id, role="assistant", content=reply)); db.commit()
    return {"reply": reply, "conversation_id": conversation_id, "provider": provider}

@router.get("/conversations/{conversation_id}")
def history(conversation_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(AssistantMessage).filter(AssistantMessage.user_id == current_user.id, AssistantMessage.conversation_id == conversation_id).order_by(AssistantMessage.created_at.asc()).all()
