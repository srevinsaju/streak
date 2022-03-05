import jwt
import uuid
import os
import datetime
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import make_response, request
from sqlalchemy_cockroachdb import run_transaction

from streak.exceptions import AuthenticationError
from . import app
from .core import utility_funcs
from .core.dbinit import create_tables
from functools import wraps
from flask import g, request, redirect, url_for
from sqlalchemy_cockroachdb import run_transaction

db_uri = "placeholder"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
       
        not_authorized = redirect(url_for('login_view', next=request.url))
        if not request.cookies.get("token"):
            print("No token", request.cookies)
            return not_authorized
        user_id = run_transaction(
            sessionmaker(bind=engine),
            lambda session: utility_funcs.get_userid_from_jwt_token(session, request.cookies.get("token")),
        )
        if not user_id:
            return not_authorized
        request.environ["user_id"] = user_id
        return f(*args, **kwargs)
    return decorated_function

try:
    _psycopg_uri = os.getenv("BACKEND_DSN")
    engine = create_engine(_psycopg_uri)
    create_tables(engine)

except Exception as e:
    print("Failed to connected to database")
    print(f"Error {e}")
    exit()


@app.route("/api/v1/tasks/create", methods=["POST"])
@login_required
def create():
    dct = request.get_json().get("task")
    name = dct.get("name")
    description = dct.get("description")
    schedule = dct.get("schedule")

    if not description or not schedule:
        raise ValueError("Invalid task payload")

    
    task_uuid = uuid.uuid4()
    user_uuid = request.environ["user_id"]
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.create_task(
            session=session, 
            task_uuid=task_uuid,
            user_uuid=user_uuid, 
            description=description, 
            schedule=schedule, 
            name=name
        ),
    )
    return {"task": {"id": str(task_uuid)}}


@app.route("/api/v1/task/<task_id>/delete", methods=["POST"])
@login_required
def delete(task_id):
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.delete_task(uuid.UUID(task_id)),
    )
    return "OK"


@app.route("/api/v1/task/<task_uuid>/update", methods=["POST"])
@login_required
def update(task_uuid):
    dct = request.get_json().get("task")
    name = dct.get("name")
    description = dct.get("description")
    schedule = dct.get("schedule")
    if not task_uuid or (not name and not description and not schedule):
        raise ValueError("Invalid task payload")
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.update_task(
            session=session, 
            task_uuid=task_uuid,
            task_name=name,
            task_description=description, 
            schedule=schedule,
        ),
    )
    return "OK"


@app.route("/api/v1/task/<task_uuid>/completed", methods=["POST"])
@login_required
def set_completed(task_uuid):
    user_uuid = request.environ["user_id"]
    if not task_uuid:
        raise ValueError("Invalid task payload")
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.create_streak(
            session=session, 
            task_uuid=task_uuid, 
            user_uuid=user_uuid),
    )
    return "OK"


@app.route("/api/v1/task/<task_uuid>/reset", methods=["POST"])
@login_required
def reset_streak(task_uuid):
    user_uuid = request.environ["user_id"]
    if not task_uuid:
        raise ValueError("Invalid task payload")
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.delete_streak(
            session=session, 
            task_uuid=task_uuid, 
            user_uuid=user_uuid),
    )
    return "OK"


@app.route("/api/v1/login", methods=["POST"])
def login():
    dct = request.get_json()
    print(dct)
    if not dct.get("username") or not dct.get("password"):
        raise ValueError("Invalid login payload")
    check, user = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.validate_user_login(
            session=session, 
            username=dct["username"], 
            password=dct["password"]
        ),
    )
    if not check:
        raise AuthenticationError("Invalid credentials")
    
    token = jwt.encode(
        {
            "user_id": str(user),
            "time": str(datetime.datetime.now()),
        },
        os.getenv("SECRET_KEY"),
        algorithm="HS256",
    )
    resp = make_response({
        "user_id": str(user),
        "token": token
    })
    resp.set_cookie("token", token)
    return resp


@app.route("/api/v1/register", methods=["POST"])
def register():
    dct = request.get_json()
    if not dct.get("username") or not dct.get("password") or not dct.get("name"):
        raise ValueError("Invalid register payload")
    
    if not re.match(r"^[a-zA-Z0-9_]+$", dct["username"]):
        raise ValueError("Invalid username")

    if run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.check_account_exists(session, dct["username"]),
    ):
        raise ValueError("Username already in database")

    user_id = uuid.uuid4()
    run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.create_account(
            session, user_uuid=user_id, 
            username=dct["username"], 
            name=dct["name"], 
            password=dct["password"]
        ),
    )
    return "OK"
