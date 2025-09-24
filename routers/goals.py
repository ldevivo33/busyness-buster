from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db import Goal, get_db
from schemas.goals import GoalCreate, GoalRead

router = APIRouter(prefix="/goals", tags=["goals"])

@router.post("/", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    goal = Goal(**payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.get("/{goal_id}", response_model=GoalRead)
def read_goal(goal_id:int, db:Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    return goal
