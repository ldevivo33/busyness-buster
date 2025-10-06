# Busyness Buster
Personal AI-powered productivity agent to review your calendar, tasks and goals to make sure you're working on business, not just busyness.

** Back-End **
Built a RESTful API integration using FASTAPI to for three resources: Events, Tasks, Goals. Identify the endpoints and build proceessing ipeline to ensure smooth scraping of events to store in the database. 

Built in services to sync events from Google Calendar, and to call chat-gpt api for AI analysis.

Run with uvicorn main:app, python app,py to open GUI. 

COMING SOON:
1. Previous day, next week syncing (Currently only next day)
2. Tests (Unit, smoke, e2e)
3. Automated endpoint testing
4. Database migration.
5. containerize and deploy.
