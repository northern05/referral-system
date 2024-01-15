from app import db


class Points(db.Model):
    __tablename__ = 'points'
    id = db.Column(db.Integer, primary_key=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True, unique=True)
    user = db.relationship('User', backref=db.backref("points", uselist=False))

    points_boost = db.Column(db.Float)
    deposit_points = db.Column(db.Float)
    borrowing_points = db.Column(db.Float)
    referral_points = db.Column(db.Float)

    def to_dict(self):
        dep_points = round(self.deposit_points, 2) if round(self.deposit_points, 2) > 1 else "< 1"
        bor_points = round(self.borrowing_points, 2) if round(self.borrowing_points, 2) > 1 else "< 1"
        ref_points = round(self.referral_points, 2) if round(self.referral_points, 2) > 1 else "< 1"
        total_points = self.deposit_points + self.borrowing_points + self.referral_points
        return {
            "id": self.id,
            "user_id": self.user_id,
            "points_boost": self.points_boost,
            "deposit_points": dep_points,
            "borrowing_points": bor_points,
            "referral_points": ref_points,
            "total_points": round(total_points, 2) if total_points > 1 else "< 1"
        }