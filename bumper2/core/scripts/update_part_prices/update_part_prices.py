# -*- coding: utf-8 -*-
__author__ = 'deepakraj'

import sys, os, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
# To use in local machine / staging just change the settings to 'bumper2.local_settings' or 'bumper2.staging_settings'
django.setup()
from django.conf import settings
from core.models.master import CarModel, CarPanelPrice
from django.db.models import Q
from decimal import Decimal
from django.utils import timezone
import logging
import glob

logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting update_part_prices.py script at {}".format(cur_time))

for fname in glob.glob("*.csv"):
    if fname in ['models.csv']:
        continue
    car_file = open(fname)

    first_line = car_file.readline()  # It will take out the first line from the car_file
    line_data = first_line.strip('\n').strip('\r').split(',')
    car_id = line_data[1]
    logger.info("car_id : %s", car_id)
    car_file.next()
    try:
        car_model = CarModel.objects.get(id=car_id)
        logger.info("car_model: %s" % car_model)
    except:
        logger.exception("No car model found: {}".format(car_id))

    for row in car_file:
        try:
            row_data = row.strip('\n').strip('\r').split(',')
            logger.info("Processing: {}".format(row_data))
            # col 0 is Part ID or Panel ID is same.
            part_id_bumper = row_data[0]
            # col 1 is Part Name
            part_name = row_data[1]
            # col 3 is the Part Price
            try:
                part_price = Decimal(row_data[3])
            except:
                logger.debug("No part price - car_id: %s, Part id : %s, Part name : %s"
                             % (car_id, part_id_bumper, part_name))
                continue

            cpp = None
            # this will give detail of the car with the id.
            car_type = car_model.car_type
            logger.info("car_type: %s" % car_type)

            # Concept is to fetch the cpp with (carmodel or car_type) & car_panel_id & type_of_work
            cpp = CarPanelPrice.objects.filter((Q(car_model=car_model) | Q(car_type=car_type) |
                                                Q(car_model=car_model.parent))
                                               & Q(car_panel_id=part_id_bumper)
                                               & Q(type_of_work=CarPanelPrice.TYPE_OF_WORK_REPLACE)
                                               ).select_related('car_model__parent').order_by('car_type',
                                                                                              'car_model__parent_id',
                                                                                              'car_model_id').first()
            if cpp:
                logger.debug("working on - car_id: %s, Part id : %s, Part name : %s, cpp_id: %s"
                             % (car_id, part_id_bumper, part_name, cpp.id))
                if cpp.car_model_id != car_model.id:
                    cpp.pk = None
                    cpp.car_type = None
                    cpp.car_model = car_model
                cpp.part_price = part_price
                cpp.save()
                logger.info("saved part price for cpp(replace): {cpp_id} successfully".format(cpp_id=cpp.id))

            cpp = CarPanelPrice.objects.filter((Q(car_model=car_model) | Q(car_type=car_type) |
                                                Q(car_model=car_model.parent))
                                               & Q(car_panel_id=part_id_bumper)
                                               & Q(type_of_work=CarPanelPrice.TYPE_OF_WORK_REPLACE_FBB)
                                               ).select_related('car_model__parent').order_by('car_type',
                                                                                              'car_model__parent_id',
                                                                                              'car_model').first()
            if cpp:
                logger.debug("working on - car_id: %s, Part id : %s, Part name : %s, cpp_id: %s"
                             % (car_id, part_id_bumper, part_name, cpp.id))
                if cpp.car_model_id != car_model.id:
                    cpp.pk = None
                    cpp.car_type = None
                    cpp.car_model = car_model
                cpp.part_price = part_price
                cpp.save()
                logger.info("saved part price for cpp (replace fbb): {cpp_id} successfully".format(cpp_id=cpp.id))
        except:
            logger.exception("Error in line: {}".format(row))
    car_file.close()

cur_time = timezone.now()
logger.info("Ending update_part_prices script at {}".format(cur_time))
