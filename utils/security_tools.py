import base64
import hashlib
import logging
import os
import random
import string

import pyotp
import six


def generate_api_key():
    seed = os.urandom(256)
    hashed_seed = hashlib.sha256(seed).hexdigest()
    api_key_base64_encoded = base64.b64encode(
        six.b(hashed_seed),
        six.b(random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD']))
    ).rstrip(b'==')
    return api_key_base64_encoded.decode()


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def get_current_one_time_code(secret: str) -> str:
    return pyotp.TOTP(secret).now()


def is_two_fa_success(secret: str, totp_code: str) -> bool:
    code = get_current_one_time_code(secret=secret)
    if code != totp_code:
        logging.debug("Not match totp code")
        raise ValueError()
    return True


def get_totp_secret(email: str, secret=None) -> dict:
    secret = pyotp.random_base32() if not secret else secret
    result = {
        "secret": secret,
        "link": pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name='Mawari')
    }
    return result
