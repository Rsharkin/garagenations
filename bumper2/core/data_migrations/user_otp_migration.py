__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.users import BumperUser
from django.db import connections

cursor = connections['bumperv1'].cursor()

cursor.execute("SELECT id,username,is_otp_validated from core_bumperuser")
for user_row in cursor.fetchall():
    try:
        user = BumperUser.objects.filter(phone=user_row[1]).first()
        print "--------------------%s-%s" % (user_row[1],user_row[2])
        if user_row[2] and user:
            user.is_otp_validated = True
            user.save()
    except django.db.utils.IntegrityError as exc:
        print "Integrity error %s" % str(exc)