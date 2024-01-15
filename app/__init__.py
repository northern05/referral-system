import logging
import os
from datetime import datetime

import firebase_admin
from flask import Flask
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from utils.injective_driver import InjectiveDriver

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ------ Database ---------
db = SQLAlchemy(app=app)

# ------ Firebase ---------
cred = firebase_admin.credentials.Certificate(Config.FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

# ------ CORS ---------
cors = CORS(app, resources='*')

# ------ Auth ---------
token_auth = HTTPTokenAuth()
jwt = JWTManager(app)

#-------- Injective driver----------
inj_driver = InjectiveDriver(Config)

# ----- Setup logging -------
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join('logs', 'errors', f'{datetime.now().strftime("%Y-%m-%d")}.error.log'))
file_handler.setLevel(logging.WARNING)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
# ------ Celery ---------
from celery import Celery
from init_celery import init_celery

celery = Celery("referral-system")
init_celery(celery, app)

# ----- Import api controllers -------
from app.api import api

api.init_app(app)
