from pydantic import BaseModel, conint
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    due_date: Optional[datetime] = None
    priority: Optional[conint(ge=0, le=10)] = 0
    completed: Optional[bool] = False

#class TaskUpdate(BaseModel):

class TaskRead(BaseModel):
    id: int
    title: str
    due_date: Optional[datetime]
    priority: int 
    completed: bool

    class Config:
        from_attributes = True