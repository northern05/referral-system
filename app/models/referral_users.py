from app import db

class ReferralUser(db.Model):
    __tablename__ = 'referral_users'
    __table_args__ = (db.UniqueConstraint('email', 'firebase_uid'),)

    user_id_referral_from = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user_from = db.relationship('User', foreign_keys=[user_id_referral_from])

    user_id_referral_to = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user_to = db.relationship('User', foreign_keys=[user_id_referral_to])

    created_at = db.Column(db.Integer, server_default=db.text("UNIX_TIMESTAMP()"), nullable=False)
    generation = db.Column(db.Integer)