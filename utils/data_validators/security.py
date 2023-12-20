from typing import Optional

from pydantic import BaseModel, validator

from app.exceptions import TotpError


class TOTPVerify(BaseModel):
    totp_code: str

    @validator('totp_code')
    def check_code_format(cls, v):
        if not v.isnumeric or len(v) != 6:
            raise TotpError
        return v


class OptionalTOTPVerify(BaseModel):
    totp_code: Optional[str]

    @validator('totp_code')
    def check_code_format(cls, v):
        if v and (not v.isnumeric or len(v) != 6):
            raise TotpError
        return v
