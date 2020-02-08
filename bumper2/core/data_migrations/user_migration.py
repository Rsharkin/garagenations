__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.users import BumperUser, UserCar, UserDevices, UserCredit
from django.db import connections

cursor = connections['bumperv1'].cursor()
cursor1 = connections['bumperv1'].cursor()

cursor.execute("SELECT id,name,email,username,city_id,utm_source,utm_medium,utm_campaign,designation,company_name,date_joined from core_bumperuser")
for user_row in cursor.fetchall():
    try:
        user = BumperUser.objects.create_user(name=user_row[1],email=user_row[2],phone=user_row[3],city_id=user_row[4],
                                              utm_source=user_row[5],utm_medium=user_row[6],utm_campaign=user_row[7],
                                              designation=user_row[8],company_name=user_row[9],date_joined=user_row[10])
        print "--------------------%s-%s" % (user_row[1],user_row[3])

        cursor1.execute("SELECT id,active,car_model_id,registration_number,purchased_on,color from core_usercar where user_id=%s" % user_row[0])
        uc_list = []
        for usercar_row in cursor1.fetchall():
            uc_list.append(UserCar(active=usercar_row[1],car_model_id=usercar_row[2],registration_number=usercar_row[3],
                                   purchased_on=usercar_row[4],color=usercar_row[5],user=user))

        UserCar.objects.bulk_create(uc_list)

        ud_list = []
        cursor1.execute("SELECT id,app_version,is_dev,gcm_device_id,apns_device_id,device_id,device_info,device_os_version from core_userdevices where user_id=%s" % (user_row[0]))
        for ud_row in cursor1.fetchall():
            ud_list.append(UserDevices(app_version=ud_row[1],is_dev=ud_row[2],gcm_device_id=ud_row[3],apns_device_id=ud_row[4],
                                       device_id=ud_row[5],device_info=ud_row[6],device_os_version=ud_row[7],user=user))

        UserDevices.objects.bulk_create(ud_list)

        cursor1.execute("SELECT id,referral_amount from core_referralcode where user_id=%s" % user_row[0])
        for rc_row in cursor1.fetchall():
            UserCredit.objects.create(user=user,credit=rc_row[1])
    except django.db.utils.IntegrityError as exc:
        print "Integrity error %s" % str(exc)