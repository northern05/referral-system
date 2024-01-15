from app.models import UserBalance
from app.dao.base_dao import BaseDAO
from app import db
from sqlalchemy import func


class UserBalanceDAO(BaseDAO):

    def get_balance_by_user(self, user_id: int):
        return db.session.query(self.model) \
            .filter(UserBalance.user_id == user_id) \
            .first()

    @staticmethod
    def get_squad_balance(users_ids: list):
        return db.session.query(
            func.sum(UserBalance.deposit_balance + UserBalance.borrowing_balance).label("total_balance")) \
            .filter(UserBalance.user_id.in_(users_ids)) \
            .first()

    def get_squad_balance_over_each_user(self, users_ids: list):
        total_squad_balance = 0
        result = {}
        query = db.session.query(self.model) \
            .filter(UserBalance.user_id.in_(users_ids)) \
            .all()

        for q in query:
            result[q.user_id] = {
                "deposit_balance": q.deposit_balance,
                "borrowing_balance": q.borrowing_balance,
                "total_balance": q.deposit_balance + q.borrowing_balance
            }
            total_squad_balance+= q.deposit_balance + q.borrowing_balance
        return result, total_squad_balance


user_balance_dao = UserBalanceDAO(UserBalance)
