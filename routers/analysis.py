from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from services.analysis import gpt_analyze

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/")
def analyze(db: Session = Depends(get_db)):
    return {"analysis": gpt_analyze(db)}