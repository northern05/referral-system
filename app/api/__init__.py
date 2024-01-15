from flask_restx import Api
from flask_restx import Namespace

general_ns = Namespace('General data', description='...')
base_ns = Namespace('Base', description='Base API endpoint')
auth_ns = Namespace('Auth', description='Auth API endpoint')
user_ns = Namespace('User', description='Users API endpoint')
referral_code_ns = Namespace('Referral code', description='Referral codes API endpoints')

from app.api.core import auth
from app.api import users
from app.api import referral_codes

api = Api(title='Referral', version='0.0.1', doc='/doc')

api.add_namespace(base_ns, path='/')
api.add_namespace(auth_ns, path='/api/v1/referral/auth')
api.add_namespace(user_ns, path='/api/v1/referral/users')
api.add_namespace(referral_code_ns, path='/api/v1/referral/codes')
