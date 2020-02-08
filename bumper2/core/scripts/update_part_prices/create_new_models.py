# -*- coding: utf-8 -*-
__author__ = 'anuj'

import sys, os, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
# To use in local machine / staging just change the settings to 'bumper2.local_settings' or 'bumper2.staging_settings'
django.setup()
from core.models.master import CarModel
from django.utils import timezone
import logging

logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting create_new_models script at {}".format(cur_time))

car_file = open('models.csv')
lines = car_file.readlines()
car_file.close()

rows = []
for line in lines[1:]:
    logger.info("Processing: {}".format(line))
    line_data = line.strip('\n').strip('\r').split(',')
    rows.append(line_data)

rows.sort(key=lambda x: x[2], reverse=True)
rows.sort(key=lambda x: x[0])
prev_model = None
for row in rows:
    try:
        logger.info("Processing: {}".format(row))
        car_model_id = int(row[0])
        start_year, end_year = row[2].split('-')
        try:
            start_year = int(start_year)
        except ValueError:
            start_year = None
        try:
            end_year = int(end_year)
        except ValueError:
            end_year = None
        if car_model_id != prev_model:
            prev_model = car_model_id
            cm = CarModel.objects.get(id=car_model_id)
            cm.start_year = start_year
            cm.end_year = end_year
            cm.save()
        else:
            cm.pk = None
            cm.start_year = start_year
            cm.end_year = end_year
            cm.parent_id = prev_model
            cm.save()
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending create_new_models script at {}".format(cur_time))
