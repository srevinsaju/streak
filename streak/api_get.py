from . import app
from .core import utility_funcs
import uuid
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy_cockroachdb import run_transaction
from .api_post import engine


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
    return json.dumps(d)
