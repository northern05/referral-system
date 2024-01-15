from app.models import ReferralCode
from app.dao.base_dao import BaseDAO
from app import db


class ReferralCodeDAO(BaseDAO):

    def get_referral_code_by_code(self, referral_code: str):
        return db.session.query(self.model) \
            .filter(self.model.referral_code == referral_code) \
            .first()

    def get_referral_code_by_user(self, user_id: int):
        return db.session.query(self.model) \
            .filter(ReferralCode.user_id == user_id) \
            .all()


referral_code_dao = ReferralCodeDAO(ReferralCode)
