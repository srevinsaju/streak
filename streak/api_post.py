import json
import uuid
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import request
from sqlalchemy_cockroachdb import run_transaction
from . import app
from .core import utility_funcs
from .core.dbinit import create_tables

db_uri = "placeholder"

try:
    _psycopg_uri = os.getenv("BACKEND_DSN")
    engine = create_engine(_psycopg_uri)
    create_tables(engine)

except Exception as e:
    print("Failed to connected to database")
    print(f"Error {e}")
    exit()


@app.route("/api/v1/tasks/create", methods=["POST"])
def create():
    dct = request.get_json().get("task")
    name = dct.get("name")
    description = dct.get("description")
    schedule = dct.get("schedule")
    if not name or not description or not schedule:
        raise ValueError("Invalid task payload")
    
    user_uuid = uuid.UUID("342a8c4a-130a-40b9-a79f-8b784b3b3e24")
    task_uuid = uuid.uuid4()
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.create_task(
            session, task_uuid, name, description, schedule, user_uuid
        ),
    )
    return {"task": {"id": str(task_uuid)}}
