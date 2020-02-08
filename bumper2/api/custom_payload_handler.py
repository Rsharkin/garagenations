__author__ = 'anuj'

import uuid
from calendar import timegm
from datetime import datetime

from rest_framework_jwt.compat import get_username, get_username_field
from rest_framework_jwt.settings import api_settings


def jwt_payload_handler(user):
    username_field = get_username_field()
    username = get_username(user)

    payload = {
        'user_id': user.pk,
        'email': user.email,
        'username': username,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    payload[username_field] = username

    if isinstance(username, uuid.UUID):
        payload['username'] = str(username)
        payload[username_field] = str(username)

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload