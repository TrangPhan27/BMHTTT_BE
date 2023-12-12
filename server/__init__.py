from flask import Flask
from flask_cors import CORS
from config import Config
import getpass
import oracledb
import os

user = os.environ['ORACLE_USER']
pw = os.environ['ORACLE_PASSWORD']
dsn = os.environ['ORACLE_DSN']

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)


connection = oracledb.connect(
    user=user,
    password=pw,
    dsn=dsn)

print("Successfully connected to Oracle Database")
cursor = connection.cursor()

from server.routes import *