from fastapi import FastAPI

from routers import auth, tasks, goals, events, analysis

app = FastAPI(title="Busyness Buster API")

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(goals.router)
app.include_router(events.router)
app.include_router(analysis.router)