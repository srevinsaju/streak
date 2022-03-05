from flask import jsonify
from . import app
from .api_post import engine
from .core import utility_funcs
from sqlalchemy.orm import sessionmaker
import uuid
from sqlalchemy_cockroachdb import run_transaction


@app.route("/api/v1/tasks/list")
def list():
    user_uuid = uuid.UUID("342a8c4a-130a-40b9-a79f-8b784b3b3e24")
    d = []
    tasks = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.get_tasks(session, user_uuid),
    )
    for task in tasks:
        d.append(
            {
                "id": task.task_id,
                "name": task.task_name,
                "description": task.task_description,
                "schedule": str(task.schedule),
                "timestamp": str(task.timestamp),
            }
        )

    return jsonify(d)


@app.route("/api/v1/task/<task_uuid>")
def meta(task_uuid):
    user_uuid = uuid.UUID("342a8c4a-130a-40b9-a79f-8b784b3b3e24")
    Session = sessionmaker(bind=engine)
    with Session() as session:
        task = utility_funcs.get_task(session, user_uuid, task_uuid)

        return {
            "id": task.task_id,
            "name": task.task_name,
            "description": task.task_description,
            "schedule": str(task.schedule),
            "timestamp": str(task.timestamp),
        }


@app.route("/api/v1/task/<task_uuid>/completed")
def get_completed(task_uuid):
    user_uuid = uuid.UUID("342a8c4a-130a-40b9-a79f-8b784b3b3e24")
    is_completed = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.has_task_completed(
            session, task_id=task_uuid, user_id=user_uuid
        ),
    )
    return {"completed": is_completed}


@app.route("/api/v1/users/<user_id> ")
def get_info(user_uuid):
    user = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.get_user(session, user_uuid),
    )
    return {
        "id": str(user.user_uuid),
        "username": user.username,
        "name": user.name,
        "last_seen": user.last_seen,
        "last_checked_events": user.last_checked_events,
    }
