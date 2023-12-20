import pyotp


def get_current_one_time_code(secret: str) -> str:
    return pyotp.TOTP(secret).now()


def is_two_fa_success(secret: str, totp_code: str) -> bool:
    code = get_current_one_time_code(secret=secret)
    if code != totp_code:
        raise ValueError('TOTP mismatch')
    return True


def get_totp_secret(email: str, secret=None) -> dict:
    secret = pyotp.random_base32() if not secret else secret
    result = {
        "secret": secret,
        "link": pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name='Chronicle')
    }
    return result
