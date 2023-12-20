from app.models import ReferralCode
from app.dao.base_dao import BaseDAO
from app import db
from datetime import datetime


class ReferralCodeDAO(BaseDAO):

    def get_referral_code_by_code(self, referral_code: str):
        return db.session.query(self.model) \
            .filter(self.model.referral_code == referral_code) \
            .filter(self.model.expired_at < datetime.now())\
            .filter(self.model.is_activate == False) \
            .first()


referral_code_dao = ReferralCodeDAO(ReferralCode)
