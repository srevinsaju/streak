import os
from . import api_post
from . import api_get
import uuid
from .api_post import engine
from flask import Flask, render_template, request
from . import app
from sqlalchemy.orm import sessionmaker

from .core import utility_funcs
from .api_post import login_required


default_render_params = {
    "logo": "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/man-running_1f3c3-200d-2642-fe0f.png",
    "app_name": "Streak",
    "static_url": os.getenv("STATIC_ENDPOINT"),
}


@app.route("/login")
def login_view():
    return render_template("login/index.html", **default_render_params)


@app.route("/register")
@login_required
def register_view():
    return render_template("register/index.html", **default_render_params)


@app.route("/")
@login_required
def index():
    user_uuid = request.environ["user_id"]
    with sessionmaker(engine)() as session:
        tasks = utility_funcs.get_tasks(session, user_uuid)
    print(tasks)
    return render_template("index.html", tasks=tasks, **default_render_params)


@app.route("/task/<task_uuid>")
@login_required
def task_view(task_uuid: str):
    user_uuid = request.environ["user_id"]
    with sessionmaker(engine)() as session:
        task = utility_funcs.get_task(session, user_uuid, task_uuid)
    print(task)
    return render_template("task/index.html", task=task, **default_render_params)

@app.route("/user/<user_uuid>")
def user_view(user_uuid: str):
    user_uuid = uuid.UUID(user_uuid)
    with sessionmaker(engine)() as session:
        user = utility_funcs.get_user(session, user_uuid)
    print(user)
    return render_template("user/index.html", user=user, **default_render_params)


@app.route("/@me")
@login_required
def profile_view(username: str):
    user_uuid = request.environ["user_id"]
    with sessionmaker(engine)() as session:
        user = utility_funcs.get_user(session, user_uuid=user_uuid)
    print(user)
    if user is None:
        # this should never happen
        raise EnvironmentError
    return render_template("user/index.html", user=user, **default_render_params)


@app.route("/@<username>")
def user_id_view(username: str):
    with sessionmaker(engine)() as session:
        user = utility_funcs.get_user_by_name(session, username)
    print(user)
    if user is None:
        return "User not found", 404
    return render_template("user/index.html", user=user, **default_render_params)



def main():
    app.run(port=os.getenv("PORT", 5000))


