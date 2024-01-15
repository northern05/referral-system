import logging

import aiohttp
import asyncio
import base64
import time
import requests
from itertools import cycle

from config import Config


class InjectiveDriver:

    def __init__(self, config):
        self.rpc_endpoint = config.INJECTIVE.RPC_ENDPOINT
        self.contract = config.INJECTIVE.CONTRACT
        self.borrow_multiplier = config.INJECTIVE.BORROW_MULTIPLIER
        self.supported_denoms = self.get_supported_denoms()
        self.semaphore = asyncio.Semaphore(100)

    async def query_contract_state_async(self, session, query: str) -> dict | str:
        headers = {"Accept": "application/json"}
        url = f"{self.rpc_endpoint}/cosmwasm/wasm/v1/contract/{self.contract}/smart/{query}"
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return await response.text()
            else:
                return (await response.json()).get('data')

    async def fetch_balance_and_borrow_async(self, session, wallet_address: str, denom: str) -> tuple:
        deposit_query = '{"get_deposit": {"address": "%s", "denom": "%s"}}' % (wallet_address, denom)
        encoded_deposit_query = base64.b64encode(deposit_query.encode(encoding="utf-8")).decode()

        borrowing_query = '{"get_user_borrowing_info": {"address": "%s", "denom": "%s"}}' % (wallet_address, denom)
        encoded_borrowing_query = base64.b64encode(borrowing_query.encode(encoding="utf-8")).decode()

        deposit_result, borrowing_result = await asyncio.gather(
            self.query_contract_state_async(session, encoded_deposit_query),
            self.query_contract_state_async(session, encoded_borrowing_query)
        )

        if isinstance(deposit_result, str):
            logging.critical(f"Error query: {deposit_query}")
            print(f"Error query: {deposit_query}")
        if isinstance(borrowing_result, str):
            logging.critical(f"Error query: {borrowing_result}")
            print(f"Error query: {borrowing_result}")

        return (
            int(deposit_result.get('balance')) / 10 ** int(self.supported_denoms[denom]),
            int(borrowing_result.get('borrowed_amount')) / 10 ** int(self.supported_denoms[denom])
        )

    async def get_total_balance_async(self, user_wallet_addresses: dict, prices: dict) -> dict:
        user_balance = {}

        async with aiohttp.ClientSession() as session:
            async with self.semaphore:
                for user_id, wallet_address in user_wallet_addresses.items():
                    user_balance[user_id] = {"deposit": 0, "borrow": 0, "total_balance": 0}
                    tasks = [
                        self.fetch_balance_and_borrow_async(
                            session=session,
                            wallet_address=wallet_address,
                            denom=denom)
                        for denom, decimal in self.supported_denoms.items()
                    ]

                    results = await asyncio.gather(*tasks)

                    for (deposit, borrow), (denom, decimal) in zip(results, self.supported_denoms.items()):
                        deposit_balance_inj = deposit * prices[denom]
                        borrow_balance_inj = borrow * prices[denom]

                        user_balance[user_id]["deposit"] += deposit_balance_inj
                        user_balance[user_id]["borrow"] += borrow_balance_inj
                        user_balance[user_id]["total_balance"] += deposit_balance_inj + borrow_balance_inj

        return user_balance

    def get_prices_sync(self):
        inj_price_query = '{"get_price": {"denom": "inj"}}'
        encoded_message = base64.b64encode(inj_price_query.encode(encoding="utf-8")).decode()
        inj_price = int(self.query_contract_state_sync(encoded_message))

        response = {}
        for denom in list(self.supported_denoms):
            price_query = '{"get_price": {"denom": "%s"}}' % denom
            encoded_message = base64.b64encode(price_query.encode(encoding="utf-8")).decode()
            price_result = self.query_contract_state_sync(encoded_message)
            response[denom] = int(price_result) / inj_price

        return response

    def get_supported_denoms(self):
        supported_tokens_query = '{"get_supported_tokens": {}}'
        encoded_message = base64.b64encode(supported_tokens_query.encode(encoding="utf-8")).decode()
        supported_tokens_result = self.query_contract_state_sync(encoded_message)
        return {d.get("denom"): d.get("decimals") for d in supported_tokens_result.get("supported_tokens")}

    def query_contract_state_sync(self, query: str):
        headers = {"Accept": "application/json"}
        url = f"{self.rpc_endpoint}/cosmwasm/wasm/v1/contract/{self.contract}/smart/{query}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return response.text
        else:
            return response.json().get('data')

    def chunk_dict_with_users(self,users_dict: dict, chunk_size: int):
        keys = list(users_dict.keys())
        values = list(users_dict.values())

        for i in range(0, len(keys), chunk_size):
            yield {keys[j]: values[j] for j in range(i, min(i + chunk_size, len(keys)))}


if __name__ == "__main__":
    start = time.time()
    injective_driver = InjectiveDriver(Config)
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
    di = {}
    for i in range(5000):
        di[i] = next(cycled)

    print(len(di))
    chunked = injective_driver.chunk_dict_with_users(users_dict=di, chunk_size=500)
    prices = injective_driver.get_prices_sync()

    for ch in chunked:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if str(e).startswith('There is no current event loop in thread'):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                raise
        print(loop.run_until_complete(injective_driver.get_total_balance_async(ch, prices)))

    end = time.time()
    print("the time of execution: ", (end - start))
