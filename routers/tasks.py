from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db import Task, get_db
from schemas.tasks import TaskCreate, TaskRead

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())  # convert schema → Task model
    db.add(task)
    db.commit()
    db.refresh(task)
    return task  

@router.get("/{task_id}", response_model = TaskRead)
def read_task(task_id:int, db: Session = Depends(get_db)):
    task = db.get(Task,task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task