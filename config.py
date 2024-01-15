import os
import ssl
from datetime import timedelta


class Config:
    BASE_API_URL = os.environ.get('BASE_API_URL')

    FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', 'referral-firebase.json')

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'key')
    JWT_ACCESS_TOKEN_EXPIRES = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES') or '300'
    JWT_REFRESH_TOKEN_EXPIRES = os.environ.get('JWT_REFRESH_TOKEN_EXPIRES') or '600'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(JWT_ACCESS_TOKEN_EXPIRES))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(JWT_REFRESH_TOKEN_EXPIRES))

    DB_NAME = os.environ.get('DB_NAME', 'dev-referral-new')
    DB_USER = os.environ.get('DB_USER', 'glib')
    DB_HOST = os.environ.get('DB_HOST', '195.189.60.221')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_PW = os.environ.get('DB_PW', '')

    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    EVERY_MINUTES = 10
    # every minute = 1440 per day
    INSPECTION_FREQUENCY = 24 * 60 / EVERY_MINUTES

    class INJECTIVE:
        CONTRACT = "inj1ulkyckufg8f0q20nsavcq5shcttq0n8nlc39t4"
        RPC_ENDPOINT = "https://injective-testnet-rest.publicnode.com" #"https://1rpc.io/572U5ZFx2yBj3pH5Q/inj-lcd" #"https://testnet.sentry.lcd.injective.network:443"
        BORROW_MULTIPLIER = 2

    class CeleryConfig:
        _REDIS_HOST = os.environ.get('REDIS_HOST', '172.21.0.6')
        _REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
        _REDIS_PW = os.environ.get('REDIS_PW', 'WKyhkXfsXeqipME7')
        _REDIS_DB_CELERY = os.environ.get('REDIS_DB_CELERY_TASKS', 0)
        REDIS_CELERY_URL = f"redis://:{_REDIS_PW}@{_REDIS_HOST}:{_REDIS_PORT}/{_REDIS_DB_CELERY}"

    CELERY_CONFIG = {
        'broker_url': CeleryConfig.REDIS_CELERY_URL,
        'result_backend': CeleryConfig.REDIS_CELERY_URL,
        'ignore_result': False,
        'task_track_started': True,
        'task_store_eager_result': True,
        'broker_connection_retry_on_startup': False,
        'broker_connection_retry': False,
    }
