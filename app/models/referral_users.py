from app import db

class ReferralUser(db.Model):
    __tablename__ = 'referral_users'
    referral_user_id = db.Column(db.Integer, primary_key=True, unique=True)

    user_id_referral_from = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user_from = db.relationship('User', foreign_keys=[user_id_referral_from])

    user_id_referral_to = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user_to = db.relationship('User', foreign_keys=[user_id_referral_to])

    referral_code_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))
    generation = db.Column(db.Integer)