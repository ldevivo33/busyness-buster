from pydantic import BaseModel, conint
from typing import Optional
from datetime import datetime

class EventCreate(BaseModel):
    google_id: str
    summary: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class EventRead(BaseModel):
    id: int
    google_id:str
    summary:str
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    class Config:
        from_attributes = True
