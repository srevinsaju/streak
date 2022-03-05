from sqlalchemy import Column, Boolean, Integer, Text, DateTime, ForeignKey, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import bcrypt

Base = declarative_base()


class Users(Base):
    """The Users class corresponds to the "users" database table."""

    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(Text)
    name = Column(Text)
    password = Column(Text)
    last_seen = Column(DateTime)
    last_checked_events = Column(DateTime)

    @staticmethod
    def get_hashed_password(plain_text_password: str):
        return bcrypt.hashpw(plain_text_password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, plain_text_password: str):
        return bcrypt.checkpw(plain_text_password.encode(), self.password.encode())

    def __repr__(self) -> str:
        return f"<Users(user_id={self.user_id}, name={self.name})>"


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

    # an integer which represents the number of days in streak
    streak = Column(Integer)

    # the time when the streak was last updated
    timestamp = Column(DateTime)
    # has the task for the time period completed?
    completed = Column(Boolean)


class Friends(Base):
    """A one to one friend uuid mapping table"""

    __tablename__ = "friend"
    relation_id = Column(UUID(as_uuid=True), primary_key=True)
    friend_col1 = Column(UUID(as_uuid=True))
    friend_col2 = Column(UUID(as_uuid=True))
