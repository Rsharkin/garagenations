__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.master import CarBrand, CarModel, CarModelVersion
from django.db import connections

cursor = connections['bumperv1'].cursor()
#cursor1 = connections['bumperv1'].cursor()
#cursor2 = connections['bumperv1'].cursor()

cursor.execute("SELECT id,name,active,logo from core_carbrand")
cb_list=[]
for brand_row in cursor.fetchall():
    cb_list.append(CarBrand(id=brand_row[0],name=brand_row[1],active=brand_row[2],logo=brand_row[3]))

CarBrand.objects.bulk_create(cb_list)

cursor.execute("SELECT id,name,active,start_year,end_year,photo,car_type,brand_id from core_carmodel")
model_list=[]
for model_row in cursor.fetchall():
    model_list.append(CarModel(id=model_row[0],name=model_row[1],active=model_row[2],brand_id=model_row[7],start_year=model_row[3],end_year=model_row[4],photo=model_row[5],car_type=model_row[6]))

CarModel.objects.bulk_create(model_list)

cmv_list=[]
cursor.execute("SELECT id,cc,fuel,gear,seating_capacity,active,car_model_id from core_carmodelversion")
for cmv_row in cursor.fetchall():
    cmv_list.append(CarModelVersion(id=cmv_row[0],car_model_id=cmv_row[6],cc=cmv_row[1],fuel=cmv_row[2],gear=cmv_row[3],
                                                 seating_capacity=cmv_row[4],active=cmv_row[5]))

CarModelVersion.objects.bulk_create(cmv_list)