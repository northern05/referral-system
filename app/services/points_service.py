import logging
import asyncio
import time

from app.dao.referral_users_dao import referral_user_dao
from app.dao.user_dao import user_dao
from app.dao.points_dao import points_dao
from app.dao.user_balance_dao import user_balance_dao
from app import db
from app import inj_driver
from app import celery
from celery import group
from config import Config
from itertools import cycle


def poll_points_reward():
    denoms_prices = inj_driver.get_prices_sync()
    users = user_dao.get_all_users()
    chunk_size = 100
    chunk_number = int(len(users) / chunk_size + 1)
    for i in range(chunk_number):
        users_chunk = {u.user_id: u.wallet for u in users[i * chunk_size: (i + 1) * chunk_size]}
        check_balances.apply_async((users_chunk, denoms_prices), link=calculate_points.s())
        #calculate_points.delay(users_chunk)


@celery.task()
def check_balances(users_wallets: dict, prices: dict):
    print(users_wallets)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise
    users_balances = loop.run_until_complete(inj_driver.get_total_balance_async(users_wallets, prices))
    for user_id, balance in users_balances.items():
        users_balance = user_balance_dao.get_balance_by_user(user_id=user_id)
        users_balance.deposit_balance = balance["deposit"]
        users_balance.borrowing = balance["borrow"]

        db.session.commit()

    logging.info("Updating balances completed!")
    return users_balances


@celery.task()
def calculate_points(users: dict):
    users = user_dao.get_users_over_ids(users_ids=list(users))
    for user in users:
        # check users deposit
        user_balance = user_balance_dao.get_balance_by_user(user_id=user.user_id)
        logging.info(f"User {user.user_id}, name = {user.name}, balance = {user_balance}")

        users_squad = referral_user_dao.get_squad_by_user(user_id=user.user_id)
        squad_balances, tot_squad_balance = user_balance_dao.get_squad_balance_over_each_user(
            users_ids=[u.user_id_referral_to for u in users_squad]
        )
        total_squad_balance = user_balance.deposit_balance + user_balance.borrowing_balance + tot_squad_balance
        # calculate points
        points_boost = _check_users_boost(total_squad_balance)
        deposit_points = (1 / Config.INSPECTION_FREQUENCY) * user_balance.deposit_balance * points_boost
        borrow_points = (1 / Config.INSPECTION_FREQUENCY) * user_balance.borrowing_balance * Config.INJECTIVE.BORROW_MULTIPLIER * points_boost
        referral_points = 0
        for user_from_squad in users_squad:
            # get balance user from squad
            user_from_squad_balance = squad_balances[user_from_squad.user_id_referral_to]
            multiplier = 20 / 100 if user_from_squad.generation == 1 else 10 / 100
            referral_points += (1 / Config.INSPECTION_FREQUENCY) * \
                               (user_from_squad_balance["deposit_balance"] + user_from_squad_balance[
                                   "borrowing_balance"] * Config.INJECTIVE.BORROW_MULTIPLIER) * \
                               points_boost * \
                               multiplier
        logging.info(
            f"User {user.user_id}, name = {user.name}, "
            f"deposit_points = {deposit_points}, "
            f"borrowing_points = {borrow_points}, "
            f"referral_points = {referral_points}"
        )

        points = points_dao.get_points_by_user(user_id=user.user_id)
        points.points_boost = points_boost
        points.deposit_points += deposit_points
        points.borrowing_points += borrow_points
        points.referral_points += referral_points

        db.session.commit()

    logging.info("Calculating completed!")


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


@celery.task()
def test():
    start = time.time()
    print("====================STARTING TEST========================================")
    addresses = ["inj17c77rwup9tdvt3vx33duvgeyrjeauyd0te0fnt",
                 "inj1nyg7ren9qud4cwjt9t4svqvjvs9pavmg2mg2th",
                 "inj1dxxhh48dr6u33ckfgvzgn9a6ky5dayda3lm9ry",
                 "inj1epvsv5cd7t2zylm38n7d6zqg2vy6f7ppdnkx9p",
                 "inj1fkjdvj6ykhvu4eku7ccte80r0yegkjma7c2k76",
                 "inj1qlwvl0r5s72zlge5u6yq7wvulu8lwp8wryuemy",
                 "inj1nqza8ujsk4d7xu9u55nr76wsmksjw2nnnfvrwm",
                 "inj12xe5l0ua3z0tztr4jq2z4rxskhyvf292wec92s"
                 ]
    cycled = cycle(addresses)
    data = {}
    for i in range(1000):
        data[i] = next(cycled)
    denoms_prices = inj_driver.get_prices_sync()

    chunk_size = 100
    chunk_number = int(len(denoms_prices) / chunk_size + 1)
    for i in range(chunk_number):
        users_chunk = {k: v for k, v in data.items()[i * chunk_size: (i + 1) * chunk_size]}
        result = group(get_balance.s(users_chunk, denoms_prices, start)).apply_async()

    end = time.time()
    print("====================ENDING TEST========================================")
    print("THE TIME IS: ", (end - start))


@celery.task()
def get_balance(chunk: dict, prices, start):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith('There is no current event loop in thread'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise
    res = loop.run_until_complete(inj_driver.get_total_balance_async(chunk, prices))
    end = time.time()
    print("THE TIME IS: ", (end - start))
    return res
