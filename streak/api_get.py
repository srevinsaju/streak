from flask import jsonify, make_response, request
from . import app
from .api_post import engine, login
from .core import utility_funcs
from sqlalchemy.orm import sessionmaker
from sqlalchemy_cockroachdb import run_transaction
from .api_post import login_required


@app.route("/api/v1/tasks/list")
@login_required
def list():
    user_uuid = request.environ["user_id"]
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
@login_required
def meta(task_uuid):
    user_uuid = request.environ["user_id"]
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
@login_required
def get_completed(task_uuid):
    user_uuid = request.environ["user_id"]
    is_completed = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.has_task_completed(
            session, task_id=task_uuid, user_id=user_uuid
        ),
    )
    return {"completed": is_completed}


@app.route("/api/v1/task/<task_uuid>/current-streak")
@login_required
def get_current_streak(task_uuid):
    user_uuid = request.environ["user_id"]
    streak = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.task_streak_status(
            session, task_id=task_uuid, user_id=user_uuid
        ),
    )
    return {"streak": streak}


def _get_info_fmt(session, user_uuid):
    user = utility_funcs.get_user(session, user_uuid)
    return {
        "id": str(user.user_id),
        "username": user.username,
        "name": user.name,
        "last_seen": user.last_seen,
        "last_checked_events": user.last_checked_events,
    }


@app.route("/api/v1/users/<user_id>")
@login_required
def get_info(user_uuid):
    return run_transaction(
        sessionmaker(bind=engine), lambda session: _get_info_fmt(session, user_uuid)
    )


@app.route("/api/v1/self")
@login_required
def get_self_info():
    user_uuid = request.environ["user_id"]
    return run_transaction(
        sessionmaker(bind=engine), lambda session: _get_info_fmt(session, user_uuid)
    )


@app.route("/api/v1/users/<friend_id>/friend_status")
@login_required
def friend_status(friend_id):
    user_uuid = request.environ["user_id"]
    print(friend_id, user_uuid, friend_id == str(user_uuid))
    if friend_id == str(user_uuid):
        return make_response("Cannot make friends with yourself", 403)
    return {
        "friends": run_transaction(
            sessionmaker(bind=engine),
            lambda session: utility_funcs.check_friend(session, user_uuid, friend_id),
        )
    }


@app.route("/api/v1/streaks/maximum")
@login_required
def max_streak():
    user_uuid = request.environ["user_id"]
    all, month, year = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.get_max_streak(session, user_uuid),
    )


    return {"all_time": all, "month": month, "year": year}


@app.route("/api/v1/task/<task_id>/maximum")
@login_required
def max_streak_task(task_id):
    user_uuid = request.environ["user_id"]
    all, month, year = run_transaction(
        sessionmaker(bind=engine),
        lambda session: utility_funcs.get_max_streak_task(session, user_uuid, task_id),
    )
    

    return {"all_time": all, "month": month, "year": year}
