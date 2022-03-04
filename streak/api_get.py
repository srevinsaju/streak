from flask import jsonify
from . import app
from .api_post import engine
from .core import utility_funcs
from sqlalchemy.orm import sessionmaker
import uuid
import json


@app.route("/api/v1/tasks/list")
def list():
    user_uuid = uuid.UUID("342a8c4a-130a-40b9-a79f-8b784b3b3e24")
    d = []
    Session = sessionmaker(bind=engine)

    with Session() as session:
        for task in utility_funcs.get_tasks(session, user_uuid):
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
    Session = sessionmaker(bind=engine)
    with Session() as session:
        is_completed = utility_funcs.has_task_completed(session, task_id=task_uuid, user_id=user_uuid)
        
        return {
            "completed": is_completed
        }
