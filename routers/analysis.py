from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import User, get_db
from dependencies import get_current_user
from services.analysis import gpt_analyze

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/")
def analyze(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"analysis": gpt_analyze(db, current_user.id)}