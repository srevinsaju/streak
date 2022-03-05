
from flask import Flask
from dotenv import load_dotenv
import os


app = Flask(__name__)
if os.getenv("SERVER_NAME"):
    app.config["SERVER_NAME"] = os.getenv("SERVER_NAME")

print("Loading environment variables")
if os.getenv("DOTENV_LOAD_PATH") is not None:
    load_dotenv(os.getenv("DOTENV_LOAD_PATH"))
else:
    load_dotenv()

