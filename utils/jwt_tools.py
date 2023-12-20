from datetime import datetime, timedelta

import jwt
from flask_jwt_extended import get_jwt
from jwt import DecodeError, ExpiredSignatureError

from app.exceptions import NotAuthorized
from app.models import User
from config import Config


def decode_jwt_to_user(jwt_token) -> User:
    try:
        decoded_token = jwt.decode(jwt_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
    except (DecodeError, ExpiredSignatureError):
        raise NotAuthorized

    return User.from_jwt_dict(token_sub_data=decoded_token['sub'])


def get_two_fa_status_from_jwt():
    a = get_jwt().get("is_2fa_completed")
    return a if a else False


def get_role_from_jwt():
    return get_jwt().get("role")


def __gen_jwt_token_by_user(user: dict, hours):
    return jwt.encode(
        {
            "user": user,
            'exp': datetime.utcnow() + timedelta(hours=hours)
        },
        Config.JWT_SECRET_KEY,
        algorithm='HS256'
    )
