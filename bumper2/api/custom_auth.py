import base64
import datetime

from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions, HTTP_HEADER_ENCODING
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from core.models.booking import Booking


def encode(key, string):
    encoded_chars = []
    for i in xrange(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.urlsafe_b64encode(encoded_string)


def decode(key, string):
    decoded_chars = []
    string = base64.urlsafe_b64decode(string)
    for i in xrange(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(abs(ord(string[i]) - ord(key_c) % 256))
        decoded_chars.append(encoded_c)
    decoded_string = "".join(decoded_chars)
    return decoded_string


def get_booking_token(booking):
    # expiry time can be configurable but that is for later.
    #expiry_time = datetime.datetime.now() + datetime.timedelta(days=7)
    #exp_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")
    return encode(settings.BOOKING_TOKEN_SECRET, str(booking.id))


def get_booking_id_from_token(token):
    try:
        decoded_str = decode(settings.BOOKING_TOKEN_SECRET, str(token))
        #decoded_list = decoded_str.split('|')
        #exp_str = decoded_list[1]
        #expiry_time = datetime.datetime.strptime(exp_str, "%Y-%m-%d %H:%M:%S")
        #if expiry_time > datetime.datetime.now():
        #    return decoded_list[0]
        #else:
        #    return None
        return int(decoded_str)
    except Exception as e:
        return None


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, text_type):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class BookingAuthentication(authentication.BaseAuthentication):
    keyword = 'Bumper'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        booking_id = get_booking_id_from_token(key)
        try:
            booking = Booking.objects.get(id=booking_id)
            # booking will be available in request.auth
            return (booking.user, booking)
        except Booking.DoesNotExist:
            return None
