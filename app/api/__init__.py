from flask_restx import Api
from flask_restx import Namespace

general_ns = Namespace('General data', description='...')
base_ns = Namespace('Base', description='Base API endpoint')
auth_ns = Namespace('Auth', description='Auth API endpoint')

from app.api.core import auth

api = Api(title='Referral', version='0.0.1', doc='/doc')

api.add_namespace(base_ns, path='/')
api.add_namespace(general_ns, path='/api/v1/')
api.add_namespace(auth_ns, path='/api/v1/auth')