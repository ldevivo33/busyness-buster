# Busyness Buster
Personal AI-powered productivity agent to review your calendar, tasks and goals to make sure you're working on business, not just busyness.
Coming soon...

** Back-End **
Built a RESTful API integration using FASTAPI to for three resources: Events, Tasks, Goals. Identify the endpoints and build proceessing ipeline to ensure smooth scraping of events to store in the database. Next steps will be to implement openAI API calls for AI analysis of the info. 

1. **Events** : Create through syncing with google calendar for all events in current day based in EST timezone. Read through get
2. **Goals** : Create through manual JSON post from front end, read through get. 
3. **Tasks** : Create through manual JSON post from front end, read through get.

Run with uvicorn main:app. Currently accessing swaggerui frontend at localhost:8000/docs.

COMING SOON:
1. Open ai api call for insight on alignment.
2. Complete CRUD of REST API for all
3. Simple REACT frontend .
4. Test (Unit, smoke, e2e)
5. Automated endpoint testing
6. Database migration.
7. containerize and deploy.
