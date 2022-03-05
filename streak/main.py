import os
from . import api_post
from . import api_get
import uuid
from .api_post import engine
from flask import Flask, render_template
from . import app
from sqlalchemy.orm import sessionmaker
from .core import utility_funcs


default_render_params = {
    "logo": "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/man-running_1f3c3-200d-2642-fe0f.png",
    "app_name": "Streak",
    "static_url": os.getenv("STATIC_ENDPOINT"),
}


@app.route("/")
def index():
    user_uuid = uuid.UUID("342a8c4a-130a-40b9-a79f-8b784b3b3e24")
    with sessionmaker(engine)() as session:
        tasks = utility_funcs.get_tasks(session, user_uuid)
    print(tasks)
    return render_template("index.html", tasks=tasks, **default_render_params)


@app.route("/task/<task_uuid>")
def task_view(task_uuid: str):
    user_uuid = uuid.UUID("342a8c4a-130a-40b9-a79f-8b784b3b3e24")
    with sessionmaker(engine)() as session:
        task = utility_funcs.get_task(session, user_uuid, task_uuid)
    print(task)
    return render_template("task/index.html", task=task, **default_render_params)


def main():
    app.run(port=os.getenv("PORT", 5000))
