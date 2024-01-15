import sqlalchemy_filters
from sqlalchemy import func

from app import db
from app import exceptions
from app.dao.base_dao import BaseDAO
from app.models import User
from app.models import Points
from app.models import ReferralUser
from app.models import ReferralCode


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

    def check_existing_user(self, firebase_uid: str, wallet: str):
        return db.session.query(self.model) \
            .join(ReferralUser, ReferralUser.user_id_referral_to == self.model.user_id) \
            .join(ReferralCode, ReferralCode.code_id == ReferralUser.referral_code_id) \
            .filter(User.firebase_uid == firebase_uid) \
            .filter(User.wallet == wallet) \
            .filter(ReferralCode.is_activate == True) \
            .first()

    def get_all_users(self):
        return db.session.query(self.model).all()

    def get_users_rank(self, user_id: int):
        sq = db.session.query(
            User.user_id,
            func.coalesce(func.sum(Points.deposit_points + Points.borrowing_points + Points.referral_points), 0).label(
                "total_points")
        ) \
            .join(Points, Points.user_id == User.user_id) \
            .group_by(User.user_id) \
            .subquery()

        rank_query = db.session.query(
            sq.c.user_id.label("user_id"),
            sq.c.total_points.label("total_points"),
            func.rank().over(order_by=sq.c.total_points.desc()).label("rank")) \
            .subquery()

        main_query = db.session.query(rank_query).filter(rank_query.c.user_id == user_id).first()
        return main_query.rank

    def get_leaderboard(self):
        sq = db.session.query(
            User.user_id,
            User.wallet,
            func.sum(Points.deposit_points).label("deposit_points"),
            func.sum(Points.borrowing_points).label("borrowing_points"),
            func.sum(Points.referral_points).label("referral_points"),
            func.coalesce(func.sum(Points.deposit_points + Points.borrowing_points + Points.referral_points), 0).label(
                "total_points")
        ) \
            .join(Points, Points.user_id == User.user_id) \
            .group_by(User.user_id) \
            .subquery()

        rank_query = db.session.query(
            sq.c.user_id.label("user_id"),
            sq.c.wallet.label("wallet"),
            sq.c.total_points.label("total_points"),
            sq.c.deposit_points,
            sq.c.borrowing_points,
            sq.c.referral_points,
            func.rank().over(order_by=sq.c.total_points.desc()).label("rank"))
        return rank_query

    def get_users_over_ids(self, users_ids: list):
        return db.session.query(self.model).filter(User.user_id.in_(users_ids)).all()


user_dao = UserDAO(User)
