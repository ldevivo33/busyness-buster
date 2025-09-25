from pydantic import BaseModel, conint
from typing import Optional
from datetime import datetime
from enum import Enum

# Enum for forecast choices
class ForecastEnum(str, Enum):
    short = "Short"
    medium = "Medium"
    long = "Long"


class GoalCreate(BaseModel):
    goal: str
    priority: Optional[conint(ge=0, le=10)] = 0
    accomplished: Optional[bool] = False
    forecast: Optional[ForecastEnum]

class GoalRead(BaseModel):
    id: int
    goal: str
    priority: int
    accomplished: bool
    forecast: Optional[str]

    class Config:
        from_attributes = True

class GoalUpdate(BaseModel):
    goal: Optional[str] = None
    priority: Optional[int] = None
    accomplished: Optional[bool] = None
    forecast: Optional[ForecastEnum] = None
