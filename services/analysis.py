from datetime import datetime, timedelta

import pytz
from openai import OpenAI

from db import Task, Goal, Event
from schemas import TaskRead, GoalRead, EventRead

client = OpenAI()


def gpt_analyze(db, user_id: int):
    """Analyze user's goals, tasks, and events using GPT."""
    goals = db.query(Goal).filter(
        Goal.accomplished == False,
        Goal.user_id == user_id
    ).all()

    tasks = db.query(Task).filter(
        Task.user_id == user_id
    ).order_by(Task.priority.desc()).limit(10).all()

    est = pytz.timezone("US/Eastern")
    today_start = datetime.now(est).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    events = db.query(Event).filter(
        Event.start_time >= today_start,
        Event.start_time < today_end,
        Event.user_id == user_id
    )

    tasks_out = [TaskRead.model_validate(t).model_dump() for t in tasks]
    goals_out = [GoalRead.model_validate(g).model_dump() for g in goals]
    events_out = [EventRead.model_validate(e).model_dump() for e in events]

    prompt = f"""
    Unaccomplished Goals:
    {goals_out}

    Top Tasks for the Week (max 10, by priority):
    {tasks_out}

    Today's Planned Work:
    {events_out}

    Please analyze whether today's work align with my tasks and goals,
    and point out anything that looks like busywork rather than working towards my tasks , and thus my important goals ! The idea is to identify 'busyness' (bad) versus 'business' (good). 

    Finish with a sentence that gives a final verdict on if today's plan is good, and if not what changes to make to nudge me towards acutally accomplishing my goals. Identify any flaws on the daily work side, how tasks are organized and related to goals, or even hihg level goals.

    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )

    return response.choices[0].message.content