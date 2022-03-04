
from flask import Flask
from dotenv import load_dotenv


app = Flask(__name__)

print("Loading environment variables")
load_dotenv()

