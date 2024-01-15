import logging

from flask import g
from flask import jsonify
from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from app import token_auth
from app.api import auth_ns
from app.exceptions import NotAuthorized
from app.services import auth_service
from utils import jwt_tools


@token_auth.verify_token
@jwt_required(optional=True)
def verify_token(token):
    token = request.headers['Authorization'].split(' ')[1] if request.headers.get('Authorization') else None

    user = jwt_tools.decode_jwt_to_user(token)

    # if user.is_totp_active:
    #     is_two_fa_passed = jwt_tools.get_two_fa_status_from_jwt()
    #     if not is_two_fa_passed:
    #         return False

    if not user:
        logging.debug(f"{token}")
        return False
    g.user = user
    logging.debug(f"User [{user.user_id}] {user.firebase_uid} is signed")
    return True


@token_auth.error_handler
def token_auth_error():
    raise NotAuthorized


@auth_ns.route('')
class Auth(Resource):

    def post(self):
        """Authenticate user"""
        result = auth_service.auth_user(data=request.json)
        return jsonify(result)


@auth_ns.route('/two_fa')
class Process2FA(Resource):

    @jwt_required()
    def post(self):
        """Process to verify 2fa code"""
        result = auth_service.process_2fa(data=request.json)
        return jsonify(result)


@auth_ns.route('/refresh_tokens')
class Refresh(Resource):
    def post(self):
        """Refresh tokens to auth"""
        result = auth_service.refresh_tokens(data=request.json)
        return jsonify(result)


@auth_ns.route('/logout')
class Logout(Resource):
    def post(self):
        """Logout user from system"""
        result = auth_service.logout(data=request.json)
        return jsonify(result)


@auth_ns.route('/setup_totp')
class SetupTOTP(Resource):
    @token_auth.login_required()
    @jwt_required()
    def post(self):
        """Setup TOTP secret key"""
        result = auth_service.setup_totp_secret(user_id=g.user.user_id, data=request.json if request.data else None)
        return jsonify(result)


@auth_ns.route('/reset_totp')
class ResetTOTP(Resource):
    @token_auth.login_required()
    def post(self):
        """Reset TOTP secret key"""
        status = auth_service.reset_user_secret(data=request.json)
        return jsonify({"status": status})


@auth_ns.route('/recaptcha')
class ReCaptchaValidation(Resource):

    def post(self):
        """Validate recaptcha result"""
        result = auth_service.validate_recaptcha(data=request.json)
        return jsonify(result)


@auth_ns.route('/check_registration')
class CheckRegistrationPossibility(Resource):

    def get(self):
        """Check possibility to registrate new users"""
        result = auth_service.check_registration_possibility()
        return jsonify(result)
