import sqlalchemy_filters

from app import db
from app import exceptions
from app.dao.base_dao import BaseDAO
from app.models import User


class UserDAO(BaseDAO):

    @staticmethod
    def apply_filter_sort_pagination(
            query,
            filter_spec: list,
            sort_spec: list,
            pagination_spec: tuple = None,
    ):
        query = sqlalchemy_filters.apply_filters(
            query=query, filter_spec=filter_spec
        )
        query = sqlalchemy_filters.apply_sort(
            query=query, sort_spec=sort_spec,
        )
        pagination = None
        # if not all_flag:
        if pagination_spec:
            query, pagination = sqlalchemy_filters.apply_pagination(
                query=query, page_number=pagination_spec[0], page_size=pagination_spec[1]
            )
        return query, pagination

    def check_existing_user(self, email: str, firebase_uid: str):
        return db.session.query(self.model) \
            .filter(User.email == email) \
            .filter(User.firebase_uid == firebase_uid) \
            .first()

    def get_all_users(self):
        return db.session.query(self.model).all()

    def get_by_email(self, email: str):
        user = db.session.query(User) \
            .filter(User.email == email) \
            .first()
        if not user:
            raise exceptions.ContentNotFound

        return user

    def get_totp_secret(self, user_id):
        totp_secret = db.session.query(User.totp_secret) \
            .filter_by(user_id=user_id) \
            .first()[0]
        return totp_secret


user_dao = UserDAO(User)
