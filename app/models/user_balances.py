from app import db


class UserBalance(db.Model):
    __tablename__ = 'users_balance'
    id = db.Column(db.Integer, primary_key=True, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True, unique=True)
    user = db.relationship('User', backref=db.backref("users_balance", uselist=False))

    deposit_balance = db.Column(db.Float)
    borrowing_balance = db.Column(db.Float)

    def __repr__(self):
        return f"{self.user_id=}, deposit = {self.deposit_balance}, borrow = {self.borrowing_balance}"

    def to_dict(self):
        deposit = round(self.deposit_balance, 2) if round(self.deposit_balance, 2) > 1 else "< 1"
        borrowing = round(self.borrowing_balance, 2) if round(self.borrowing_balance, 2) > 1 else "< 1"
        total = self.deposit_balance + self.borrowing_balance
        return {
            "id": self.id,
            "user_id": self.user_id,
            "deposit_balance": deposit,
            "borrowing_balance": borrowing,
            "total_balance": round(total, 2) if total > 1 else "< 1"
        }