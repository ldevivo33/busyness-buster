from sqlalchemy import Column, Integer, String, DateTime, Boolean, CheckConstraint
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key = True)
    title = Column(String, nullable = False)
    due_date = Column(DateTime)
    priority = Column(Integer, default = 0)
    completed = Column(Boolean, default = False)

    __table_args__ = (
        CheckConstraint('priority >= 0 AND priority <= 10', name='priority_range'),
    )

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    time = Column(DateTime)


engine = create_engine("sqlite:///busyness.db", echo=True)
Base.metadata.create_all(engine)

test_task = Task(title = "Finish Busyness Buster!", due_date = datetime(2025, 9, 22), priority = 10)
test_event = Event(name = "Study for GA", time = datetime(2025,9,23,14,30))

Session = sessionmaker(bind=engine)
session = Session()

session.add(test_task)
session.add(test_task)

session.commit()