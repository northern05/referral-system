from sqlalchemy.sql import false

from app import db


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (db.UniqueConstraint('email', 'role', 'firebase_uid'),)

    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    created_at = db.Column(db.Integer, server_default=db.text("UNIX_TIMESTAMP()"), nullable=False)

    firebase_uid = db.Column(db.String(255))
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)

    wallet = db.Column(db.String(42), unique=True)
    points = db.Columns(db.Float)

    def __repr__(self):
        return f"{self.email=}"

    def to_dict(self):
        return {
            "id": self.user_id,
            "email": self.email,
            "name": self.name,
            "is_totp_active": self.is_totp_active,
            "is_email_verified": self.is_email_verified,
        }


    @staticmethod
    def from_jwt_dict(token_sub_data: dict):
        return User(
            user_id=token_sub_data["id"],
            email=token_sub_data["email"],
            name=token_sub_data["name"],
            is_email_verified=token_sub_data["is_email_verified"],
            is_totp_active=token_sub_data["is_totp_active"],
            role=token_sub_data.get("role"),
        )
