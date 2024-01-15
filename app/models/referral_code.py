from app import db


class ReferralCode(db.Model):
    __tablename__ = 'referral_codes'
    code_id = db.Column(db.Integer, primary_key=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user = db.relationship('User', backref=db.backref("referral_codes", uselist=False))

    referral_code = db.Column(db.Text)
    is_activate = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))
    # expired_at = db.Column(db.Integer, server_default=db.text("UNIX_TIMESTAMP()"))

    def to_dict(self):
        return {
            "referral_code": self.referral_code,
            "is_activate": self.is_activate,
            "created_at": self.created_at,
            # "expired_at": self.expired_at,
        }
