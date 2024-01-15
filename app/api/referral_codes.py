from flask import jsonify, request
from flask_restx import Resource

from app import token_auth
from app.api import referral_code_ns
from app.services import referral_service
from flask import g


@referral_code_ns.route('')
class UsersSquadAPI(Resource):

    @token_auth.login_required()
    def get(self):
        result = referral_service.get_codes(user_id=g.user.user_id)
        return jsonify(result)

    @token_auth.login_required()
    def post(self):
        result = referral_service.create_code(user_id=g.user.user_id)
        return jsonify(result)


@referral_code_ns.route('/check_code')
class CheckCodeAPI(Resource):

    def post(self):
        result = referral_service.check_code(code=request.args.get('code'))
        return jsonify(result)


@referral_code_ns.route('/check_inj_balance')
class CheckBalanceAPI(Resource):

    def get(self):
        result = referral_service.get_balance(address=request.args.get('address'))
        return jsonify(result)
