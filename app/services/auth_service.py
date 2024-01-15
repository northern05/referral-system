import logging
from typing import Optional

import requests
from firebase_admin import auth
from flask import g
from flask import request
from flask_jwt_extended import get_jwt
from sqlalchemy.exc import IntegrityError

from app import db
from app.dao.session_dao import session_dao
from app.dao.user_dao import user_dao
from app.dao.referral_code_dao import referral_code_dao
from app.exceptions import *
from app.models import User
from app.services import referral_service
from config import Config
from utils import security_tools
from utils import totp_utils
from utils.data_validators.auth_validators import AuthForm
from utils.data_validators.auth_validators import RefreshTokenForm
from utils.data_validators.auth_validators import TwoFARefreshTokenForm


def auth_user(data: dict):
    """
    Method to authenticate user
    :param data: should contain fingerprint, idToken, role
    :return: dict with access token, refresh token
    and users information (email, name, role, id, is_totp_active, is_email_verified
    """
    data = AuthForm.parse_obj(data)
    logging.debug(f"Request with: {data}")

    try:
        decoded_token = auth.verify_id_token(data.idToken)
    except auth.InvalidIdTokenError as err:
        raise NotAuthorized(err)

    fingerprint = data.fingerprint
    firebase_uid, picture = decoded_token.get('uid'), decoded_token.get('picture')

    try:
        # check existing user
        user = user_dao.check_existing_user(
            firebase_uid=firebase_uid,
            wallet=data.wallet
        )
        if not user:
            _check_referral_code(data.referral_code)
            # registrate user
            reg_user(
                name=data.screenName,
                picture=picture,
                firebase_uid=firebase_uid,
                wallet=data.wallet,
                twitter_id=data.federatedId,
                referral_code=data.referral_code
            )
    except IntegrityError as err:
        db.session.rollback()
        raise UserAlreadyExists
    except Exception as err:
        logging.critical(f"Failed to register the user. Error: {err}. Data: {data}")

    # try:
    jwt_pair = login_user(firebase_uid=firebase_uid, fingerprint=fingerprint, wallet=data.wallet)

    return jwt_pair


def refresh_tokens(data: dict):
    """
    Method to refresh tokens
    :param data:
    :return: dict with tokens
    """
    data = RefreshTokenForm.parse_obj(data)
    tokens, user_dict = session_dao.refresh(
        refresh_token=data.refresh_token,
        fingerprint=data.fingerprint
    )
    logging.debug(f"Change RT {data.refresh_token[-8:]} -> {tokens['refresh_token'][-8:]}")

    # user_dict["role"] = data.role
    result = {
        'tokens': tokens,
        'user': user_dict
    }
    return result


def _check_referral_code(referral_code: str):
    referral_code = referral_code_dao.get_referral_code_by_code(referral_code=referral_code)
    if not referral_code:
        raise NotExistReferralCode
    if referral_code.is_activate:
        raise ReferralCodeAlreadyUsed


def reg_user(**kwargs):
    """
    Method to registrate user
    :param kwargs: data with user information: firebase_uid, name
    :return: dict with user
    """
    referral_code = kwargs.pop("referral_code")
    user = user_dao.create(**kwargs)
    referral_service.registrate_user(younger_user_id=user.user_id, referral_code=referral_code)
    logging.debug(f"User {user.firebase_uid} saved to DB with id {user.user_id}")
    return user.to_dict()


def login_user(firebase_uid: str, fingerprint: str, wallet: str) -> dict:
    """
    Method to login user
    :param firebase_uid: users email
    :param fingerprint:  users fingerprint
    :param wallet: users wallet address
    :return: dict with token
    """
    user = User.query.filter(User.firebase_uid == firebase_uid).filter(User.wallet == wallet).first()
    logging.debug(f"Got from DB {firebase_uid}")

    if not user:
        logging.debug(f"User uid={firebase_uid} not found")
        raise NotAuthorized(f"User not found!")

    user_dict = user.to_dict()
    session_data = {
        "user_dict": user_dict,
        "fingerprint": fingerprint,
    }
    tokens = session_dao.create(**session_data)

    result = {
        'tokens': tokens,
        'user': user_dict
    }
    return result


def logout(data: dict):
    """
    Method to logout user
    :param data: should contain fingerprint and refresh_token
    :return: True if success
    """
    data = RefreshTokenForm.parse_obj(data)
    try:
        session_dao.delete_session(fingerprint=data.fingerprint, refresh_token=data.refresh_token)
    except NotAuthorized:
        ...
    return True


def process_2fa(data: dict):
    """
    Method to process two-factor authentication
    :param data: should contain fingerprint, refresh_token, totp_code
    :return: dict with access token, refresh token
    and users information (email, name, role, id, is_totp_active, is_email_verified
    """
    data = TwoFARefreshTokenForm.parse_obj(data)

    user_id = get_jwt()['sub'].get('id')
    totp_secret = user_dao.get_totp_secret(user_id=user_id)

    try:
        totp_utils.is_two_fa_success(
            secret=totp_secret, totp_code=data.totp_code
        )
    except ValueError:
        raise DoNotHaveAccess("TOTP mismatch")

    additional_claims = {
        "is_2fa_completed": True,
    }

    try:
        tokens, user = session_dao.refresh(
            refresh_token=data.refresh_token, fingerprint=data.fingerprint,
            is_2fa_completed=additional_claims
        )
        logging.debug(f"Change RT {data.refresh_token}->{tokens['refresh_token'][-20:]}")
    except Exception as err:
        logging.debug(f"for (RT & FP):{data.refresh_token, data.fingerprint} got an exception {err}")
        raise NotAuthorized()
    return {'tokens': tokens, "user": user}


def setup_user_secret(user_id: int):
    """
    Method to setup secret
    :param user_id:
    :return: dict with secret and link
    """
    user = User.query.get(user_id)
    if user.is_totp_active:
        raise ValueError("User has already set up the TOTP secret")
    result = security_tools.get_totp_secret(email=user.email, secret=user.totp_secret)
    user.totp_secret = result["secret"]
    db.session.commit()
    return result


def setup_totp_secret(user_id: int, data: Optional[dict]) -> dict:
    """
    Method to setup totp secret
    :param user_id:
    :param data: should contain fingerprint, refresh_token, totp_code
    :return: dict with token
    """
    user = user_dao.get_selected(id=user_id)
    if user.is_totp_active:
        raise TotpError('Your TOTP secret is already set')
    additional_claims = {
        "is_2fa_completed": True,
    }

    if not data:
        return setup_user_secret(user_id=user_id)
    else:
        try:
            security_tools.is_two_fa_success(secret=user.totp_secret, totp_code=data["totp_code"])
            validate_user_secret(user_id=user_id)
        except ValueError:
            user.is_totp_active = False
            db.session.commit()
            raise TotpError()
    tokens, user_dict = session_dao.refresh(refresh_token=data["refresh_token"], fingerprint=data["fingerprint"],
                                            is_2fa_completed=additional_claims)

    result = {
        'tokens': tokens,
        'user': user_dict
    }
    result["user"]['is_totp_active'] = True

    return result


def validate_user_secret(user_id: int):
    """
    Method to validate users secret
    :param user_id:
    :return: "Success"
    """
    user = User.query.get(user_id)
    users = db.session.query(User).filter(User.firebase_uid == user.firebase_uid).all()
    for u in users:
        u.totp_secret = user.totp_secret
        u.is_totp_active = True
    db.session.commit()
    return "Success"


def reset_user_secret(data: dict):
    """
    Method to reset totp secret
    :param data: should contain totp_code
    :return: "Reset" if success
    """
    user_id = g.user.user_id
    user = User.query.get(user_id)
    if not user:
        raise BadAPIUsage('No user in refresh token')
    try:
        security_tools.is_two_fa_success(secret=user.totp_secret, totp_code=data["totp_code"])
    except ValueError:
        raise DoNotHaveAccess('Totp mismatch')

    users = db.session.query(User).filter(User.firebase_uid == user.firebase_uid).all()
    for u in users:
        u.is_totp_active = False
        u.totp_secret = None
    db.session.commit()
    return "Reset"


def validate_recaptcha(data: dict):
    """
    Method for validation recaptcha result
    :param data: should contain secret_key and token
    :return: dict with result of validation
    """
    recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
    payload = {
        'secret': data['secret_key'],
        'response': data['token'],
        'remoteip': request.remote_addr,
    }
    response = requests.post(url=recaptcha_url, data=payload)
    result = response.json().get('success', False)
    return {"success": result}
