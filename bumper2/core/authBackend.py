from core.models.users import BumperUser
from django.contrib.auth.backends import ModelBackend
from django.db import OperationalError


class AuthBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
       try:
          return BumperUser.objects.get(pk=user_id)
       except BumperUser.DoesNotExist:
          return None

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = BumperUser.objects.get(
                # Q(email=username) | Q(phone=username)
                ops_phone=username
            )
        except BumperUser.DoesNotExist:
            return None
        except OperationalError:
            return None

        return user if user.check_password(password) else None