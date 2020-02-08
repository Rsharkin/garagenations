__author__ = 'anuj'

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions, status
from rest_framework.compat import set_rollback
from rest_framework.response import Response

from django.utils.encoding import force_text


import logging
logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    """
    Logging exceptions.
    """

    request = context.get('request')

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (dict)):
            data = exc.detail
        elif isinstance(exc.detail, (list)):
            data = {'detail': ', '.join(exc.detail)}
        else:
            data = {'detail': exc.detail}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    elif isinstance(exc, Http404):
        msg = _('Not found.')
        data = {'detail': six.text_type(msg)}

        set_rollback()
        logger.exception("----------- API Exception 404: User: {}, data: {}, source: {}, full_path: {}".format(
                                                                        request.user,
                                                                        request._full_data,
                                                                        request.META.get('HTTP_SOURCE'),
                                                                        request.get_full_path()))
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, PermissionDenied):
        msg = _('Permission denied.')
        data = {'detail': six.text_type(msg)}

        set_rollback()
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    # Note: Unhandled exceptions will raise a 500 error.
    logger.exception("----------- API Exception: User: {}, data: {}, source: {}, full_path: {}".format(
                                                                        request.user,
                                                                        request._full_data,
                                                                        request.META.get('HTTP_SOURCE'),
                                                                        request.get_full_path()))
    return None


class ConflictError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, detail):
        # For validation errors the 'detail' key is always required.
        # The details should always be coerced to a list if not already.
        if not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]
        self.detail = detail

    def __str__(self):
        return six.text_type(self.detail)