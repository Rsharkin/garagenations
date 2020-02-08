__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.master import State,City
from django.db import connections

cursor = connections['bumperv1'].cursor()
#cursor1 = connections['bumperv1'].cursor()

cursor.execute("SELECT id,name,active from core_state")
state_list = []
for state_row in cursor.fetchall():
    state_list.append(State(id=state_row[0],name=state_row[1],active=state_row[2]))
    print "--------------------%s" % state_row[1]

State.objects.bulk_create(state_list)

cursor.execute("SELECT id,name,active,state_id from core_city")
city_list = []
for city_row in cursor.fetchall():
    city_list.append(City(id=city_row[0],name=city_row[1],active=city_row[2],state_id=city_row[3]))

City.objects.bulk_create(city_list)