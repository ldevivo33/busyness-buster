import os.path
import pytz
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    """Return an authenticated Google Calendar API service object."""
    creds = None

    # 1. Try loading saved user credentials (token.json)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 2. If no valid creds, refresh or go through OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=8080)

        # Save creds for next time
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # 3. Build and return the Calendar API client
    service = build("calendar", "v3", credentials=creds)
    return service

def fetch_events():
    """Fetch events for the current day in EST (America/New_York)."""
    service = get_calendar_service()

    # Define timezone
    est = pytz.timezone("America/New_York")

    # Get "now" in EST
    now_est = datetime.now(est)

    # Start of today (midnight)
    start_of_day = now_est.replace(hour=0, minute=0, second=0, microsecond=0)

    # End of today (23:59:59)
    end_of_day = start_of_day + timedelta(days=1)

    # Convert to RFC3339 format (Google Calendar API expects this)
    time_min = start_of_day.isoformat()
    time_max = end_of_day.isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return events_result.get("items", [])