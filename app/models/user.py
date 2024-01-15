from app import db


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (db.UniqueConstraint('firebase_uid', 'wallet'),)

    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))

    firebase_uid = db.Column(db.String(255))
    name = db.Column(db.String(255))
    picture = db.Column(db.String(255))

    wallet = db.Column(db.String(42), unique=True)
    twitter_id = db.Column(db.String(255))

    def __repr__(self):
        return f"{self.user_id=}"

    def to_dict(self):
        return {
            "id": self.user_id,
            "name": self.name,
            "picture": self.picture,
            "wallet": self.wallet,
            "twitter_id": self.twitter_id
        }

    @staticmethod
    def from_jwt_dict(token_sub_data: dict):
        return User(
            user_id=token_sub_data["id"],
            name=token_sub_data["name"],
            wallet=token_sub_data.get("wallet")
        )
