import api_post
import api_get
from flask import Flask


app = Flask(__name__)


for name in (lambda a: not a.startswith("_"), dir(api_post)):
    app.route(f"/api/v1/{name}", methods=["POST"])(getattr(api_post, name))

for name in filter(lambda a: not a.startswith("_"), dir(api_get)):
    app.route(f"/api/v1/{name}")(getattr(api_get, name))
