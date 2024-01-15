import werkzeug.exceptions


class BadAPIUsage(werkzeug.exceptions.HTTPException):
    code = 400
    description = 'Bad API usage'


class ContentNotFound(werkzeug.exceptions.HTTPException):
    code = 404
    description = 'Content not found'


class BadServiceUsage(BadAPIUsage):
    pass


class NotAuthorized(werkzeug.exceptions.HTTPException):
    code = 401
    description = 'Not Authorized'


class DoNotHaveAccess(werkzeug.exceptions.HTTPException):
    code = 403
    description = 'Do Not Have Access'


class EmailNotVerified(DoNotHaveAccess):
    code = 403
    description = 'Email is not verified'


class TotpError(DoNotHaveAccess):
    code = 403
    description = 'TOTP is invalid'


class TooManyRequests(Exception):
    code = 429
    description = 'Too Many Requests'


class APIKeyExpired(werkzeug.exceptions.HTTPException):
    code = 400
    description = 'API Key Expired'


class NotExistReferralCode(werkzeug.exceptions.HTTPException):
    code = 400
    description = 'Referral code not exists!'


class ReferralCodeAlreadyUsed(werkzeug.exceptions.HTTPException):
    code = 400
    description = 'Referral code already used!'


class UserAlreadyExists(werkzeug.exceptions.HTTPException):
    code = 400
    description = 'User already exists!'
