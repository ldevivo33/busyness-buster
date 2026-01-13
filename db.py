from sqlalchemy import Column, Integer, String, DateTime, Boolean, CheckConstraint, Enum, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationships
    tasks = relationship("Task", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    events = relationship("Event", back_populates="user")


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    due_date = Column(DateTime)
    priority = Column(Integer, default=0)
    completed = Column(Boolean, default=False)

    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    goal = relationship("Goal", back_populates="tasks")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")

    __table_args__ = (
        CheckConstraint('priority >= 0 AND priority <= 10', name='task_priority_range'),
    )

class Goal(Base):
    __tablename__ = 'goals'

    id = Column(Integer, primary_key=True)
    goal = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    accomplished = Column(Boolean, default=False)
    forecast = Column(Enum('Short', 'Medium', 'Long', name='forecast_enum'))

    tasks = relationship("Task", back_populates="goal")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="goals")

    __table_args__ = (
        CheckConstraint('priority >= 0 AND priority <= 10', name='goal_priority_range'),
    )

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    google_id = Column(String, nullable=False, unique=True)
    summary = Column(String, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="events")

engine = create_engine("sqlite:///busyness.db", echo=True)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

__all__ = ["User", "Task", "Goal", "Event"]

""" 
test_task = Task(title = "Finish Busyness Buster!", due_date = datetime(2025, 9, 22), priority = 10)
test_event = Event(name = "Study for GA", time = datetime(2025,9,23,14,30))
test_goal = Goal(goal = 'Get a job', priority = 10, forecast = 'Short')

session.add(test_task)
session.add(test_event)
session.add(test_goal)
"""

#session.commit()