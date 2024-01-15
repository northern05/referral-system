from flask import jsonify, request
from flask_restx import Resource

from app import token_auth
from app.api import user_ns
from app.services import user_service, points_service
from flask import g


@user_ns.route('/squad')
class UsersSquadAPI(Resource):

    @token_auth.login_required()
    def get(self):
        result = user_service.get_squad(user_id=g.user.user_id)
        return jsonify(result)


@user_ns.route('')
class UserAPI(Resource):

    @token_auth.login_required()
    def get(self):
        result = user_service.get_self_info(user_id=g.user.user_id)
        return jsonify(result)

    @token_auth.login_required()
    def put(self):
        data = request.json
        result = user_service.update_user(user_id=g.user.user_id, data=data)
        return jsonify(result)


@user_ns.route('/leaderboard')
class LeaderboardAPI(Resource):

    def get(self):
        result = user_service.get_leaderboard()
        return jsonify(result)


@user_ns.route('/poll_points')
class UsersSquadAPI(Resource):

    def post(self):
        points_service.poll_points_reward()
        return jsonify({"ok": True})


@user_ns.route('/test')
class UsersSquadAPI(Resource):

    def post(self):
        points_service.test.delay()
        return jsonify({"ok": True})