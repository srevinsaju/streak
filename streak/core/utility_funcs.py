from argparse import ArgumentParser
import os
from typing import List
import urllib.parse
import datetime
import uuid
from datetime import timedelta
import jwt
from sqlalchemy import create_engine
from .models import Tasks, TaskStreak, Users
from . import models

# The code below inserts new accounts.


def check_account_exists(session, username):
    return bool(session.query(Users).filter(Users.username == username).first())


def create_account(session, user_uuid, username, name, password):
    account = models.Users(
        user_id=user_uuid,
        username=username,
        name=name,
        password=models.Users.get_hashed_password(password),
        last_seen=datetime.datetime.now(),
        last_checked_events=datetime.datetime.now(),
    )
    session.add_all([account])


def create_task(session, task_uuid, task_name, task_description, schedule, user_id):
    task = models.Tasks(
        task_id=task_uuid,
        user_id=user_id,
        task_name=task_name,
        task_description=task_description,
        timestamp=datetime.datetime.now(),
        schedule=schedule,
    )
    session.add_all([task])


def create_streak(session, task_id, user_id):

    task = (
        session.query(TaskStreak)
        .filter(TaskStreak.task_id == task_id)
        .filter(TaskStreak.user_id == user_id)
        .filter(
            (TaskStreak.timestamp + datetime.timedelta(days=1))
            > datetime.datetime.now()
        )
        .first()
    )

    if task is not None:
        # already have a streak
        return

    previous_task = (
        session.query(TaskStreak)
        .filter(TaskStreak.task_id == task_id)
        .filter(TaskStreak.user_id == user_id)
        .filter(
            (TaskStreak.timestamp + timedelta(days=1))
            > datetime.datetime.now() - timedelta(days=1)
        )
        .first()
    )

    if previous_task and previous_task.completed:
        # user completed the task yesterday
        streak = previous_task.streak + 1
    else:
        streak = 1

    streak_uuid = uuid.uuid4()
    streak = models.TaskStreak(
        streak_id=streak_uuid,
        task_id=task_id,
        user_id=user_id,
        streak=streak,
        timestamp=datetime.datetime.now(),
        completed=True,
    )
    session.add_all([streak])


def delete_streak(session, task_id, user_id):
    task = (
        session.query(TaskStreak)
        .filter(TaskStreak.task_id == task_id)
        .filter(TaskStreak.user_id == user_id)
        .filter(
            (TaskStreak.timestamp + datetime.timedelta(days=1))
            > datetime.datetime.now()
        )
        .first()
    )
    if task is None:
        raise ValueError("Cannot delete streak, streak does not exist")
    session.delete(task)


def has_task_completed(session, task_id, user_id):
    task = (
        session.query(TaskStreak)
        .filter(TaskStreak.task_id == task_id)
        .filter(TaskStreak.user_id == user_id)
        .filter(
            (TaskStreak.timestamp + datetime.timedelta(days=1))
            > datetime.datetime.now()
        )
        .first()
    )
    return task is not None and task.completed


def update_task(session, task_id, task_name=None, task_description=None, schedule=None):
    task = session.query(Tasks).filter(Tasks.task_id == task_id).first()
    if task_name:
        task.task_name = task_name
    if task_description:
        task.task_description = task_description
    if schedule:
        task.schedule = schedule


def delete_task(session, task_id):
    """Delete a task, given task id"""
    task = session.query(Tasks).filter(Tasks.task_id == task_id).first()
    session.delete(task)


def get_tasks(session, user_uuid) -> List[Tasks]:
    return session.query(Tasks).filter(Tasks.user_id == user_uuid).all()


def get_task(session, user_uuid, task_uuid) -> Tasks:
    return (
        session.query(Tasks)
        .filter(Tasks.user_id == user_uuid)
        .filter(Tasks.task_id == task_uuid)
        .first()
    )

def get_user_from_jwt_token(session, jwt_token: str):
    payload = jwt.decode(jwt_token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
    return get_user(session, payload["user_id"])


def get_user(session, user_uuid) -> Users:
    return session.query(Users).filter(Tasks.user_id == user_uuid).first()


def validate_user_login(session, name, password):
    user = session.query(Users).filter(Users.name == name).first()
    if not user:
        raise ValueError("User does not exist")
    
    return (Users.check_password(user, password), user.user_id)


def parse_cmdline():
    parser = ArgumentParser()
    parser.add_argument("url", help="Enter your node's connection string\n")
    opt = parser.parse_args()
    return opt


if __name__ == "__main__":

    opt = parse_cmdline()
    conn_string = opt.url

    # For CockroachCloud:
    # postgres://<username>:<password>@<globalhost>:26257/<cluster_name>.defaultdb?sslmode=verify-full&sslrootcert=<certs_dir>/<ca.crt>
    try:
        db_uri = os.path.expandvars(conn_string)
        db_uri = urllib.parse.unquote(db_uri)

        psycopg_uri = (
            db_uri.replace("postgresql://", "cockroachdb://")
            .replace("postgres://", "cockroachdb://")
            .replace("26257?", "26257/bank?")
        )

        # The "cockroachdb://" prefix for the engine URL indicates that we are
        # connecting to CockroachDB using the 'cockroachdb' dialect.
        # For more information, see
        # https://github.com/cockroachdb/sqlalchemy-cockroachdb.

        engine = create_engine(psycopg_uri)
    except Exception as e:
        print("Failed to connect to database.")
        print("{0}".format(e))
        exit()
