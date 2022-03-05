from argparse import ArgumentParser
import os
from typing import List
import urllib.parse
import datetime
import uuid
from datetime import timedelta
import jwt
from sqlalchemy import create_engine
from ..exceptions import AuthenticationError
from .models import Friends, Tasks, TaskStreak, Users
from . import models
from sqlalchemy import func

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


def create_task(
    session,
    task_uuid: uuid.UUID,
    task_name: str,
    task_description: str,
    schedule,
    user_id: uuid.UUID,
):
    task = models.Tasks(
        task_id=task_uuid,
        user_id=user_id,
        task_name=task_name,
        task_description=task_description,
        timestamp=datetime.datetime.now(),
        schedule=schedule,
    )
    session.add_all([task])


def create_streak(session, task_id: uuid.UUID, user_id: uuid.UUID):

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


def delete_streak(session, task_id: uuid.UUID, user_id: uuid.UUID):
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


def has_task_completed(session, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
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


def get_userid_from_jwt_token(session, jwt_token: str) -> uuid.UUID:
    payload = jwt.decode(jwt_token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
    return get_user(session, payload["user_id"]).user_id


def get_user(session, user_uuid: uuid.UUID) -> Users:
    return session.query(Users).filter(Users.user_id == user_uuid).first()


def get_user_by_name(session, username: str) -> Users:
    return session.query(Users).filter(Users.username == username).first()


def validate_user_login(session, username, password):
    user = session.query(Users).filter(Users.username == username).first()
    if not user:
        raise AuthenticationError("User does not exist")

    return (Users.check_password(user, password), user.user_id)


# returns UUID of all the friends
def get_friends(session, user_uuid):
    friends = []
    data = (
        session.query(Friends)
        .filter((Friends.friend_col1 == user_uuid) | (Friends.friend_col2 == user_uuid))
        .all()
    )
    for i, j in data:
        if i != user_uuid:
            friends.append(i)
        else:
            friends.append(j)
    return friends


# add friend
def add_friend(session, user_uuid, friend_uuid):
    if check_friend(session, user_uuid, friend_uuid):
        raise ValueError("Already friends")
    data = models.Friends(friend_col1=user_uuid, friend_col2=friend_uuid, relation_id=uuid.uuid4())
    session.add_all([data])


def remove_friend(session, user_uuid, friend_uuid):
    friend = (
        session.query(Friends)
        .filter(
            (Friends.friend_col1 == user_uuid) & (Friends.friend_col2 == friend_uuid)
        )
        .first()
    ) or (
        session.query(Friends)
        .filter(
            (Friends.friend_col1 == friend_uuid) & (Friends.friend_col2 == user_uuid)
        )
        .first()
    )
    if not friend:
        raise ValueError("Friend doesn't exist")
    session.delete(friend)


def check_friend(session, user_uuid, friend_uuid):
    return bool(
        (
            session.query(Friends)
            .filter(
                (Friends.friend_col1 == user_uuid)
                & (Friends.friend_col2 == friend_uuid)
            )
            .first()
        )
        or (
            session.query(Friends)
            .filter(
                (Friends.friend_col1 == friend_uuid)
                & (Friends.friend_col2 == user_uuid)
            )
            .first()
        )
    )


def get_max_streak(session, user_uuid):
    all_time = session.query(func.max(TaskStreak.streak)).filter(
        TaskStreak.user_id == user_uuid
    )
    month = session.query(func.max(TaskStreak.streak)).filter(
        TaskStreak.user_id
        == user_uuid & (TaskStreak.timestamp.month() == datetime.today().month())
    )
    year = session.query(func.max(TaskStreak.streak)).filter(
        TaskStreak.user_id
        == user_uuid & (TaskStreak.timestamp.year() == datetime.today().year())
    )
    return all_time, month, year


def get_max_streak_task(session, user_uuid, task_uuid):
    all_time = session.query(func.max(TaskStreak.streak)).filter(
        (TaskStreak.user_id == user_uuid) & (TaskStreak.task_id == task_uuid)
    )
    month = session.query(func.max(TaskStreak.streak)).filter(
        (TaskStreak.user_id == user_uuid)
        & (TaskStreak.task_id == task_uuid)
        & (TaskStreak.timestamp.month() == datetime.today().month())
    )
    year = session.query(func.max(TaskStreak.streak)).filter(
        (TaskStreak.user_id == user_uuid)
        & (TaskStreak.task_id == task_uuid)
        & (TaskStreak.timestamp.year() == datetime.today().year())
    )
    return all_time, month, year


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
