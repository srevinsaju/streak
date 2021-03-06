import os

from sqlalchemy import inspect
from . import api_post
from . import api_get
import uuid
from .api_post import engine
from flask import Flask, abort, make_response, redirect, render_template, request
from . import app
from sqlalchemy.orm import sessionmaker

from .core import utility_funcs
from .api_post import login_required


default_render_params = {
    "logo": "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/man-running_1f3c3-200d-2642-fe0f.png",
    "app_name": "Streak",
    "static_url": os.getenv("STATIC_ENDPOINT"),
}

@app.errorhandler(404)
def resource_not_found(e):
    return render_template("404.html", err=e, **default_render_params), 404

@app.errorhandler(500)
def resource_not_found(e):
    return render_template("500.html", err=e, **default_render_params), 404



@app.route("/login")
def login_view():
    return render_template("login/index.html", **default_render_params)


@app.route("/register")
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


@app.route("/events")
@login_required
def events_view():
    user_uuid = request.environ["user_id"]
    with sessionmaker(engine)() as session:
        notifications = utility_funcs.get_notifications(session, user_uuid)

    return render_template(
        "events/index.html", 
        **default_render_params,
        greetings=["Hifive 👏", "Congrats! 🥳"], 
        notifications=[
            {"streak": x.Events.streak, 
            "name": x.Users.username,
            "task_name": x.Tasks.task_name,
            } for x in notifications
        ])


@app.route("/task/<task_uuid>")
@login_required
def task_view(task_uuid: str):
    user_uuid = request.environ["user_id"]
    with sessionmaker(engine)() as session:
        task = utility_funcs.get_task(session, user_uuid, task_uuid)
    print(task)
    if task is None:
        abort(404, description="Task not found")
    return render_template("task/index.html", task=task, **default_render_params, tasks_page=True)

@app.route("/user/<user_uuid>")
def user_view(user_uuid: str):
    user_uuid = uuid.UUID(user_uuid)
    with sessionmaker(engine)() as session:
        user = utility_funcs.get_user(session, user_uuid)
    print(user)
    if user is None:
        abort(404, description="User not found")
    return render_template("user/index.html", user=user, **default_render_params)


@app.route("/@me")
@login_required
def profile_view():
    with sessionmaker(engine)() as session:
        user = utility_funcs.get_user(session, request.environ["user_id"])
    if user is None:
        raise EnvironmentError("User self is not found")
    return redirect("/@{}".format(user.username))


@app.route("/@<username>")
def user_id_view(username: str):
    with sessionmaker(engine)() as session:
        user = utility_funcs.get_user_by_name(session, username)
    print(user)
    if user is None:
        abort(404, description="User not found")
    
    with sessionmaker(engine)() as session:
        all_time, month, year = utility_funcs.get_max_streak(session, user.user_id)
    total = all_time + month + year
    if total == 0: total = 1
    
    print(all_time, month, year)
    if user is None:
        return "User not found", 404
    return render_template("user/index.html", 
        user=user, 
        all_time=all_time,
        month=month,
        year=year,
        monthly_percentage=(month / total) * 100,
        yearly_percentage=(year / total) * 100,
        alltime_percentage=(all_time / total) * 100,
        **default_render_params)



def main():
    app.run(port=os.getenv("PORT", 5000), host="0.0.0.0")


