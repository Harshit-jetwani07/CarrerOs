from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserProfileUpdate, UserOut

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.patch("/target-role", response_model=UserOut)
def set_target_role(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Persist the selected role so every dashboard tab uses the same target."""
    role_name = payload.get("role_name")
    if not isinstance(role_name, str) or not role_name.strip():
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="role_name is required.")
    current_user.target_role = role_name.strip()
    db.commit(); db.refresh(current_user)
    return current_user


@router.delete("/target-role", response_model=UserOut)
def remove_target_role(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Clear the chosen target role and return to comparing all roles."""
    current_user.target_role = None
    db.commit(); db.refresh(current_user)
    return current_user


@router.put("", response_model=UserOut)
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user
