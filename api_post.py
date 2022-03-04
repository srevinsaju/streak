import json
import uuid

from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_cockroachdb import run_transaction

from core import utility_funcs

db_uri = "placeholder"

try:
    psycopg_uri = (
        db_uri.replace("postgresql://", "cockroachdb://")
        .replace("postgres://", "cockroachdb://")
        .replace("26257?", "26257/bank?")
    )
    engine = create_engine(psycopg_uri)

except Exception as e:
    print("Failed to connected to database")
    print(f"Error {e}")
    exit()


def create():
    dct = json.loads(request.body).get("tasks")
    if (
        dct
        and (name := dct.get("name"))
        and (description := dct.get("description"))
        and (schedule := dct.get("schedule"))
    ):
        user_uuid = uuid.UUID("342a8c4a-130a-40b9-a79f-8b784b3b3e24")
        task_uuid = uuid.uuid4()
        run_transaction(
            sessionmaker(bind=engine),
            lambda session: utility_funcs.create_task(
                session, task_uuid, name, description, schedule, user_uuid
            ),
        )
    return json.dump({"task": {"id": str(task_uuid)}})
