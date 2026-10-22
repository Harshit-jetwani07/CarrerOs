from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.job import JDAnalyzeRequest, JDAnalyzeOut
from app.services.jd_service import analyze_jd
from app.models.job import JobDescription
from app.services.providers.base import ProviderError

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/analyze", response_model=JDAnalyzeOut)
def analyze_job_description(
    payload: JDAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return analyze_jd(db, current_user.id, payload.title, payload.raw_text)
    except ProviderError as exc:
        raise HTTPException(status_code=422, detail=exc.reason) from exc


@router.get("")
def list_job_descriptions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Keep a compact account-scoped history so JD analysis is not a dead end."""
    return db.query(JobDescription).filter(JobDescription.user_id == current_user.id).order_by(JobDescription.created_at.desc()).limit(8).all()
