from pydantic import BaseModel
from typing import Optional


class UserUpdate(BaseModel):
    wallet: Optional[str]
