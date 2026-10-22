from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.services.matching_service import compute_role_matches

router = APIRouter(prefix="/api/career", tags=["career"])


@router.get("/matches")
def get_role_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return compute_role_matches(db, current_user.id)
