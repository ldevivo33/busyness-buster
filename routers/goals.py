from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from db import Goal, get_db
from schemas.goals import GoalCreate, GoalRead, GoalUpdate

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

@router.patch("/{goal_id}", response_model=GoalUpdate)
def update_goal(goal_id:int, payload: GoalUpdate, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    updates = payload.model_dump(exclude_unset=True)

    for key,value in updates.items():
        setattr(goal,key, value)
    
    db.commit()
    db.refresh(goal)

    return goal

@router.delete("/{goal_id}", status_code = 204)
def delete_goal(goal_id:int, db: Session = Depends(get_db)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(goal)
    db.commit()

    return None