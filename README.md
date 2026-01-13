# Busyness Buster
Personal AI-powered productivity agent to review your calendar, tasks and goals to make sure you're working on business, not just busyness.

** Back-End **
Built a RESTful API integration using FASTAPI for three resources: Events, Tasks, Goals. Built in services to sync events from Google Calendar, and to call GPT API for AI analysis.

JWT authentication with per-user data isolation. All routes protected, data scoped to logged-in user.

** Setup **
1. Install deps: `pip install -r requirements.txt`
2. Create user: `python seed_user.py`
3. Run: Double-click `start.pyw` (cleanest) or `run_bb.bat`

COMING SOON:
1. Async background tasks
2. Previous day, next week syncing (Currently only next day)
3. Tests (Unit, smoke, e2e)
4. Database migrations (Alembic)
5. Containerize and deploy
