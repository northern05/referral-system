from typing import Optional

from pydantic import BaseModel, validator


class PurchaseData(BaseModel):
    amount: float
    payment_method: Optional[str]

    @validator('amount')
    def validate_price(cls, amount: float):
        if not amount:
            return None
        if amount < 0:
            raise ValueError("bad price")
        try:
            # if v["currency"] not in Config.AVAILABLE_CURRENCIES:
            #     raise ValueError("Bad currency")
            # v["value"] = float(v["value"])
            return int(amount * 100)
        except KeyError:
            raise ValueError("bad price")
