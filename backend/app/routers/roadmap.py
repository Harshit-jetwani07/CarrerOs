from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.roadmap import Roadmap
from app.schemas.roadmap import RoadmapOut, RoadmapGenerateRequest
from app.services.roadmap_service import generate_roadmap
from app.services.providers.base import ProviderError

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


def _to_out(roadmap: Roadmap) -> dict:
    weekly_hours = {4: 18, 8: 10, 12: 7, 16: 5}.get(roadmap.total_weeks, 8)
    return {
        "id": roadmap.id,
        "role_name": roadmap.role.name,
        "total_weeks": roadmap.total_weeks,
        "items": roadmap.items,
        "weekly_study_hours": weekly_hours,
    }


@router.post("/generate", response_model=RoadmapOut)
def create_roadmap(
    payload: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        roadmap = generate_roadmap(db, current_user.id, payload.role_name, payload.total_weeks)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ProviderError as exc:
        raise HTTPException(status_code=422, detail=exc.reason) from exc
    return _to_out(roadmap)


@router.get("/{role_name}", response_model=RoadmapOut)
def get_roadmap(
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = (
        db.query(Roadmap)
        .join(Roadmap.role)
        .filter(Roadmap.user_id == current_user.id, Roadmap.role.has(name=role_name))
        .first()
    )
    if roadmap is None:
        raise HTTPException(status_code=404, detail="No roadmap yet for this role — generate one first.")
    return _to_out(roadmap)


@router.patch("/item/{item_id}/toggle")
def toggle_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.roadmap import RoadmapItem
    item = (
        db.query(RoadmapItem)
        .join(RoadmapItem.roadmap)
        .filter(RoadmapItem.id == item_id, Roadmap.user_id == current_user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Roadmap item not found.")
    item.completed = not item.completed
    db.commit()
    return {"id": item.id, "completed": item.completed}
