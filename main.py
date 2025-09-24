from fastapi import FastAPI

from routers import tasks, goals, events

app = FastAPI(title="Busyness Buster API")
app.include_router(tasks.router)
app.include_router(goals.router)
app.include_router(events.router)