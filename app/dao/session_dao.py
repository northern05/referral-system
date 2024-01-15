import logging
import time

import flask_jwt_extended
import jwt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token

from app import db
from app import exceptions
from app.dao.base_dao import BaseDAO
from app.models import Session, User


class SessionDAO(BaseDAO):

    def get_by_refresh_token(self, refresh_token: str) -> Session:
        session = db.session.query(self.model) \
            .filter_by(refresh_token=refresh_token) \
            .first()
        if not session:
            raise exceptions.ContentNotFound("Session not found")

        return session

    def refresh(self, refresh_token: str, fingerprint: str, is_2fa_completed: bool = False):
        filter_spec = [
            {"model": "Session", "field": "fingerprint", "op": "==", "value": fingerprint},
            {"model": "Session", "field": "refresh_token", "op": "==", "value": refresh_token},
        ]
        session = session_dao.get_selected(filter_spec=filter_spec, is_raiseable=False)
        if not session:
            logging.debug(f"No session find - [fp={fingerprint}, rt[:-8]= {refresh_token[-8:]} ]")
            raise exceptions.NotAuthorized(f'No session find')
        try:
            decoded_token = flask_jwt_extended.decode_token(refresh_token)
        except jwt.ExpiredSignatureError:
            raise exceptions.NotAuthorized('Session is expired')
        except exceptions.ContentNotFound:
            raise exceptions.NotAuthorized('User not exists')

        user_dict = decoded_token['sub']
        is_2fa_completed = decoded_token.get("is_2fa_completed") if not is_2fa_completed else is_2fa_completed
        additional_claims = {"is_2fa_completed": is_2fa_completed}

        if user_dict["id"] != session.user_id:
            session_dao.delete_session(fingerprint=fingerprint, refresh_token=refresh_token)
            db.session.commit()
            raise exceptions.NotAuthorized('All sessions was dropped')

        user = User.query.get(user_dict["id"])
        if user.is_totp_active and not is_2fa_completed:
            raise exceptions.DoNotHaveAccess('You have to complete 2fa')

        access_token = create_access_token(identity=user_dict, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user_dict, additional_claims=additional_claims)
        session.updated_at = int(time.time())
        session.refresh_token = refresh_token
        db.session.commit()

        return {'access_token': access_token, 'refresh_token': refresh_token}, user.to_dict()

    def delete_session(
            self,
            fingerprint: str,
            refresh_token: str
    ):
        intent = self.model.query \
            .filter(Session.fingerprint == fingerprint) \
            .filter(Session.refresh_token == refresh_token) \
            .first()
        if not intent:
            raise exceptions.NotAuthorized()

        db.session.delete(intent)
        db.session.commit()
        return True

    def create(self, user_dict: dict, fingerprint: str, additional_claims: dict = None) -> dict:

        session = db.session.query(Session) \
            .filter_by(fingerprint=fingerprint) \
            .filter_by(user_id=user_dict["id"]) \
            .first()

        access_token = create_access_token(identity=user_dict, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user_dict, additional_claims=additional_claims)

        if not session:
            session = Session(user_id=user_dict["id"], refresh_token=refresh_token, fingerprint=fingerprint)
            db.session.add(session)

        session.refresh_token = refresh_token
        db.session.commit()

        return {'access_token': access_token, 'refresh_token': refresh_token}


session_dao = SessionDAO(Session)
