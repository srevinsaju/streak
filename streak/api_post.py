import jwt
import uuid
import os
import datetime

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


@app.route("/api/v1/tasks/create", methods=["GET", "POST"])
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


@app.route("/api/v1/task/<task_id>/delete", methods=["POST"])
def delete(task_id):
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.delete_task(uuid.UUID(task_id)),
    )


@app.route("/api/v1/tasks/update", methods=["POST"])
def update():
    dct = request.get_json().get("task")
    task_uuid = dct.get("task_uuid")
    name = dct.get("name")
    description = dct.get("description")
    schedule = dct.get("schedule")
    if not task_uuid or (not name and not description and not schedule):
        raise ValueError("Invalid task payload")
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.update_task(
            session, task_uuid, name, description, schedule
        ),
    )


@app.route("/api/v1/login")
def login():
    dct = request.get_json()
    if not dct.get("name") or not dct.get("password"):
        raise ValueError("Invalid task payload")
    check, user = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.update_task(
            session, dct["name"], dct["password"]
        ),
    )
    if not check:
        raise ValueError("Invalid credentials")
    if check:
        return jwt.encode({"user_id": user.user_id, "time": datetime.datetime.now()})
