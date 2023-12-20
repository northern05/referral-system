import logging

from app import db
from app.dao.referral_users_dao import referral_user_dao
from app.dao.user_dao import user_dao
from utils import smart_contract_driver
from config import Config


def get_squad(user_id: int):
    users_squad = referral_user_dao.get_squad(user_id=user_id)
    response = {"data": u.to_dict() for u in users_squad}
    return response


def calculate_points():
    users = user_dao.get_all_users()
    users_balances = {u.user_id: smart_contract_driver.get_balance(u.wallet) for u in users}
    for user in users:
        user_balance = users_balances[user.user_id]
        squad_balance = user_balance
        # check users deposit
        if not user_balance:
            logging.warning(f"User id:{user.user_id}, email: {user.email} balance is None.")
            continue
        personal_boost = 1.5 if user_balance > 100 else 1
        # calculate points
        points_sum = (1 / Config.INSPECTION_FREQUENCY) * user_balance
        users_squad = referral_user_dao.get_squad(user_id=user.user_id)
        if not users_squad:
            continue
        for user_from_squad in users_squad:
            user_from_squad_balance = users_balances[user_from_squad.user_id_referral_to]
            points_sum += ((1 / Config.INSPECTION_FREQUENCY) * user_from_squad_balance) * (
                    user_from_squad_balance.generation * 10 / 100)
            squad_balance+=user_from_squad_balance

        squad_boost = _check_users_boost(balance=squad_balance)

        user.points += (points_sum * personal_boost * squad_boost)
        db.session.commit()

    return {"ok": True}


def _check_users_boost(balance: int):
    if 100 < balance < 400:
        boost = 1.5
    elif 400 < balance < 1000:
        boost = 1.7
    elif 1000 < balance:
        boost = 2
    else:
        boost = 1
    return boost
