from argparse import ArgumentParser
import os
import urllib.parse
import datetime
from sqlalchemy import create_engine
from .models import Tasks
from . import models

# The code below inserts new accounts.


def create_account(session, user_uuid, name, password):
    """Create new accounts with random account IDs and default field values"""
    account = models.Users(
        user_id=user_uuid,
        name=name,
        password=models.Users.get_hashed(password),
        last_seen=datetime.datetime.now(),
        last_checked_events=datetime.datetime.now(),
    )
    session.add_all([account])


def create_task(session, task_uuid, task_name, task_description, schedule, user_id):
    """Create new accounts with random account IDs and default field values"""
    task = models.Tasks(
        task_id=task_uuid,
        user_id=user_id,
        task_name=task_name,
        task_description=task_description,
        timestamp=datetime.datetime.now(),
        schedule=schedule,
    )
    session.add_all([task])


def create_streak(session, streak_uuid, task_id, user_id, task_description, schedule):
    """Create new accounts with random account IDs and default field values"""
    streak = models.Tasks(
        streak_id=streak_uuid, task_id=task_id, user_id=user_id, streak=0
    )
    session.add_all([streak])


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
