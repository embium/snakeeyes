from urllib.parse import urljoin

from config.settings import SECRET_KEY
from itsdangerous import URLSafeTimedSerializer

from flask import request


def safe_next_url(target):
    """
    Ensure a relative URL path is on the same domain as this host.
    This protects against the 'Open redirect vulnerability'.

    :param target: Relative url (typically supplied by Flask-Login)
    :type target: str
    :return: str
    """
    return urljoin(request.host_url, target)


def sign_token(data):
    """
    Sign and create a token that can be used for things such as resetting
    a password or other tasks that involve a one off token.
    :return: Data
    """
    serializer = URLSafeTimedSerializer(SECRET_KEY)

    return serializer.dumps(data)


def verify_token(token, ex=3600):
    """
    Obtain a user from de-serializing a signed token.

    :param token: Signed token.
    :type token: str
    :param expiration: Seconds until it expires, defaults to 1 hour
    :type expiration: int
    :return: Data or None
    """
    serializer = URLSafeTimedSerializer(SECRET_KEY)

    try:
        return serializer.loads(token, max_age=ex)
    except Exception:
        return None
