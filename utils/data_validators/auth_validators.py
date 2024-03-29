from pydantic import BaseModel, EmailStr
from typing import Optional


class AuthForm(BaseModel):
    email: Optional[EmailStr]
    idToken: str
    fingerprint: str
    referral_code: Optional[str]
    screenName: Optional[str]
    federatedId: Optional[str]
    wallet: str


class RefreshTokenForm(BaseModel):
    refresh_token: str
    fingerprint: str
    role: Optional[str]


class TwoFARefreshTokenForm(RefreshTokenForm):
    totp_code: str


class VerifyEmailForm(BaseModel):
    email: str
    fingerprint: str
