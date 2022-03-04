import os
from . import api_post
from . import api_get
from flask import Flask, render_template
from . import app


default_render_params = {
    "logo": "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/man-running_1f3c3-200d-2642-fe0f.png",
    "app_name": "Streak",
    "static_url": os.getenv("STATIC_ENDPOINT"),
}


@app.route("/")
def index():
    return render_template("index.html", **default_render_params)


def main():
    app.run(port=os.getenv("PORT", 5000))
