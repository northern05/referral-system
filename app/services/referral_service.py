from app.dao.referral_code_dao import referral_code_dao
from app.dao.referral_users_dao import referral_user_dao
from app.dao.user_dao import user_dao
from app.dao.points_dao import points_dao
from app.dao.user_balance_dao import user_balance_dao
from app import exceptions
from app import inj_driver
from app import db
import random
import string


def registrate_user(younger_user_id: int, referral_code: str):
    ref_code = referral_code_dao.get_referral_code_by_code(referral_code=referral_code)
    if not ref_code:
        raise exceptions.NotExistReferralCode
    middle_user_id = ref_code.user_id

    referral_user_dao.create(
        user_id_referral_from=middle_user_id,
        user_id_referral_to=younger_user_id,
        referral_code_id=ref_code.code_id,
        generation=1,
    )

    older_users = referral_user_dao.get_older_users(middle_user_id=middle_user_id)
    for older_user in older_users:
        referral_user_dao.create(
            user_id_referral_from=older_user.user_id_referral_from,
            user_id_referral_to=younger_user_id,
            referral_code_id=ref_code.code_id,
            generation=(older_user.generation + 1),
        )

    ref_code.is_activate = True
    db.session.commit()

    points_dao.create(
        user_id=younger_user_id,
        points_boost= 1,
        deposit_points = 0,
        borrowing_points = 0,
        referral_points = 0,
    )
    user_balance_dao.create(
        user_id=younger_user_id,
        deposit_balance= 0,
        borrowing_balance= 0
    )
    return {"ok": True}


def create_code(user_id: int):
    referral_codes = referral_code_dao.get_referral_code_by_user(user_id=user_id)
    if referral_codes:
        raise exceptions.BadAPIUsage("All referral codes created")
    user = user_dao.get_selected(id=user_id)
    user_balance = inj_driver.get_total_balance(wallet_address=user.wallet)
    codes_count = 8 if user_balance['total_balance'] > 100 else 4
    codes = []
    for i in range(codes_count):
        code = referral_code_dao.create(
            user_id=user_id,
            referral_code=_generate_code()
        )
        codes.append(code.to_dict())
    return {"data": codes}


def get_codes(user_id: int):
    codes_count = 0
    user_balance = user_balance_dao.get_balance_by_user(user_id=user_id)
    total_user_balance = user_balance.deposit_balance + user_balance.borrowing_balance
    referral_codes = referral_code_dao.get_referral_code_by_user(user_id=user_id)
    all_ref_codes = [c.to_dict() for c in referral_codes]
    not_active_codes = [c.to_dict() for c in referral_codes if not c.is_activate]
    if total_user_balance > 100 and len(all_ref_codes) >= 8:
        return {"data": not_active_codes}
    elif total_user_balance < 100 and len(all_ref_codes) >= 4:
        return {"data": not_active_codes}
    elif total_user_balance > 100 and len(all_ref_codes) < 8:
        if len(all_ref_codes) == 4:
            codes_count = 4
        elif len(all_ref_codes) == 0:
            codes_count = 8
    elif total_user_balance < 100:
        codes_count = 4
    for i in range(codes_count):
        code = referral_code_dao.create(
            user_id=user_id,
            referral_code=_generate_code()
        )
        not_active_codes.append(code.to_dict())
    return {"data": not_active_codes}


def check_code(code: str):
    referral_code = referral_code_dao.get_referral_code_by_code(referral_code=code)
    if not referral_code:
        raise exceptions.NotExistReferralCode
    if referral_code.is_activate:
        raise exceptions.ReferralCodeAlreadyUsed
    else:
        return {"ok": True}


def _generate_code(length=5, existing_codes=None):
    if existing_codes is None:
        existing_codes = set()
    characters = string.ascii_letters + string.digits
    while True:
        referral_code = ''.join(random.choice(characters) for _ in range(length))
        if referral_code not in existing_codes:
            existing_codes.add(referral_code)
            return referral_code


def get_balance(address: str):
    balance = inj_driver.get_total_balance(wallet_address=address)
    return {"balance": balance}
