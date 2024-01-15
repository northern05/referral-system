from app.models import ReferralUser
from app.dao.base_dao import BaseDAO
from app import db


class ReferralUserDAO(BaseDAO):

    def get_older_users(self, middle_user_id: int):
        return db.session.query(self.model) \
            .filter(self.model.user_id_referral_to == middle_user_id) \
            .all()

    def get_squad_by_user(self, user_id: int):
        return db.session.query(self.model) \
            .filter(ReferralUser.user_id_referral_from == user_id) \
            .filter(ReferralUser.generation <= 2) \
            .all()


referral_user_dao = ReferralUserDAO(ReferralUser)
