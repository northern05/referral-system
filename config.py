import logging
import os
from datetime import timedelta


class Config:
    BASE_API_URL = os.environ.get('BASE_API_URL')

    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', '')

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'key')
    JWT_ACCESS_TOKEN_EXPIRES = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES') or '3'
    JWT_REFRESH_TOKEN_EXPIRES = os.environ.get('JWT_REFRESH_TOKEN_EXPIRES') or '30'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(JWT_ACCESS_TOKEN_EXPIRES))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(JWT_REFRESH_TOKEN_EXPIRES))

    DB_NAME = os.environ.get('DB_NAME', 'dev-mawari')
    DB_USER = os.environ.get('DB_USER', 'alex')
    DB_HOST = os.environ.get('DB_HOST', '195.189.62.182')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_PW = os.environ.get('DB_PW', 'WjqxFUFKwh9kftnz')

    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    # every minute = 1440 per day
    INSPECTION_FREQUENCY = 1440