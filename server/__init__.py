from flask import Flask
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, support_credentials=True)

from server.routes import *