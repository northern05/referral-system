from app.dao.referral_code_dao import referral_code_dao
from app.dao.referral_users_dao import referral_user_dao
from app import exceptions


def registrate_user(younger_user_id: int, referral_code: str):
    ref_code = referral_code_dao.get_referral_code_by_code(referral_code=referral_code)
    if not ref_code:
        raise exceptions.NotExistReferralCode
    middle_user_id = ref_code.user_id

    referral_user_dao.create(
        user_id_referral_from=middle_user_id,
        user_id_referral_to=younger_user_id,
        generation=1,
    )

    older_users = referral_user_dao.get_older_users(middle_user_id=middle_user_id)
    for older_user in older_users:
        referral_user_dao.create(
            user_id_referral_from=older_user.user_id_referral_from,
            user_id_referral_to=younger_user_id,
            generation=(older_user.generation + 1),
        )

    return {"ok": True}
