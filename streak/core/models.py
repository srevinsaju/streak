from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import bcrypt

Base = declarative_base()


class Users(Base):
    """The Users class corresponds to the "users" database table."""

    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(Text)
    password = Column(Text)
    last_seen = Column(DateTime)
    last_checked_events = Column(DateTime)

    @staticmethod
    def get_hashed_password(plain_text_password):
        return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

    def check_password(self, plain_text_password):
        return bcrypt.checkpw(plain_text_password, self.password)


class Tasks(Base):
    """The Tasks class corresponds to the "tasks" database table."""

    __tablename__ = "tasks"
    task_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    task_name = Column(Text)
    task_description = Column(Text)
    timestamp = Column(DateTime)
    schedule = Column(Time)
    
    def __repr__(self) -> str:
        return f"<Tasks(task_id='{self.task_id}', user_id='{self.user_id}', task_name='{self.task_name}', task_description='{self.task_description}', timestamp='{self.timestamp}', schedule='{self.schedule}')>"

class TaskStreak(Base):
    """The TaskStreak class corresponds to the "task_streak" database table."""

    __tablename__ = "task_streak"
    streak_id = Column(UUID(as_uuid=True), primary_key=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.task_id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    streak = Column(Integer)
