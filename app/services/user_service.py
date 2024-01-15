from app.dao.referral_users_dao import referral_user_dao
from app.dao.user_dao import user_dao
from app.dao.points_dao import points_dao
from app.dao.user_balance_dao import user_balance_dao
from utils.data_validators import UserUpdate


def get_self_info(user_id: int):
    user = user_dao.get_selected(id=user_id)
    points = points_dao.get_points_by_user(user_id=user_id)
    users_rank = user_dao.get_users_rank(user_id=user_id)
    users_balance = None
    if user.wallet:
        users_balance = user_balance_dao.get_balance_by_user(user_id=user_id)
    return {**user.to_dict(), **points.to_dict(), "rank": users_rank, "balance": users_balance.to_dict()}


def update_user(user_id: int, data: dict):
    new_data = UserUpdate.parse_obj(data)
    user_dao.update(id=user_id, new_data=new_data.dict())
    return {"ok": True}


def get_squad(user_id: int):
    result = []
    user_balance = user_balance_dao.get_balance_by_user(user_id=user_id)
    squad_balance = user_balance.deposit_balance + user_balance.borrowing_balance
    users_squad = referral_user_dao.get_squad_by_user(user_id=user_id)
    for u in users_squad:
        user_balance = user_balance_dao.get_balance_by_user(user_id=u.user_id_referral_to)
        squad_balance += user_balance.deposit_balance + user_balance.borrowing_balance
        if u.generation < 2:
            result.append({**u.user_to.to_dict(), **user_balance.to_dict()})
    goal, boost = _check_squad_goals(balance=squad_balance)
    response = {"data": result,
                "goals": {"goal": goal, "boost": boost,
                          "balance": round(squad_balance, 2) if squad_balance > 1 else "< 1"}}
    return response


def _check_squad_goals(balance: float):
    if balance < 100:
        goal = 100
        boost = 1.5
    elif 100 < balance < 400:
        goal = 400
        boost = 1.7
    elif 400 < balance < 1000:
        goal = 1000
        boost = 2
    else:
        goal = "completed"
        boost = "max"
    return goal, boost


def get_leaderboard():
    result = []
    leaderboard = user_dao.get_leaderboard()
    for u in leaderboard:
        result.append({
            "user_id": u.user_id,
            "wallet": u.wallet,
            "total_points": round(u.total_points, 2),
            "deposit_points": round(u.deposit_points, 2),
            "borrowing_points": round(u.borrowing_points, 2),
            "referral_points": round(u.referral_points, 2),
            "rank": u.rank
        })
    return {"data": result}
