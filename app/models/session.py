from app import db


class Session(db.Model):
    __tablename__ = 'sessions'
    __table_args__ = (db.UniqueConstraint('user_id', 'fingerprint'),)

    session_id = db.Column(db.Integer, primary_key=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    user = db.relationship('User', backref=db.backref("sessions"))

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))

    refresh_token = db.Column(db.Text, nullable=False)
    fingerprint = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Session user_id={self.user_id}, created_at={self.created_at}"
