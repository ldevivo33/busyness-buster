from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db import Event, get_db
from schemas.events import EventCreate, EventRead

from services.google_calendar import fetch_events

from dateutil import parser

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/sync", response_model=list[EventRead])

def sync_events(db: Session = Depends(get_db)):
    google_events = fetch_events()

    stored_events = []
    for g_event in google_events:
        google_id = g_event["id"]
        summary = g_event.get("summary", "No Title")

        # Parse RFC3339 strings safely
        start_raw = g_event["start"].get("dateTime") or g_event["start"].get("date")
        end_raw = g_event["end"].get("dateTime") or g_event["end"].get("date")

        start_time = parser.parse(start_raw) if start_raw else None
        end_time = parser.parse(end_raw) if end_raw else None

        # upsert: check if event already exists in DB
        event = db.query(Event).filter(Event.google_id == google_id).first()
        if event:
            event.summary = summary
            event.start_time = start_time
            event.end_time = end_time
        else:
            event = Event(
                google_id=google_id,
                summary=summary,
                start_time=start_time,
                end_time=end_time
            )
            db.add(event)
        stored_events.append(event)

    db.commit()
    return stored_events

@router.get("/{event_id}}", response_model=EventRead)
def read_event(event_id:int, db:Session = Depends(get_db)):
    event = db.get(Event,event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event
