__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.master import CarModel
from decimal import Decimal
from django.utils import timezone
import logging
import glob

logger = logging.getLogger('bumper.scripts')

# assume that this is only for "replace" type of work.
# get file data
# for each record, if panel id exist - update the prices else create new records with prices.

cur_time = timezone.now()
logger.info("Starting update_car_types script at {}".format(cur_time))

car_file = open('carmodeldata.csv')
segment_dict = {
    'H1': 5,
    'H2': 6,
    'H3': 7,
    'S1': 8,
    'S2': 9,
    'S3': 10,
    'V1': 11,
    'V2': 12,
    'V3': 13,
    'LUXURY': 4,
    'SUV': 13 # All remaining SUV were V3.
}
for row in car_file:
    try:
        row_data = row.strip('\n').strip('\r').split(',')
        logger.info("Processing: {}".format(row_data))
        # col 0 is car model id
        car_model_id = row_data[0] if not '' else None
        # col 1 is old_car_type
        old_car_type = row_data[1]
        # col 4 is segment
        segment = row_data[4]
        new_car_type = segment_dict[segment]
        cm = CarModel.objects.filter(id=car_model_id).first()
        if cm:
            cm.car_type = new_car_type
            cm.save()
            logger.info("Car Model Updated: {}".format(cm.id))
        else:
            logger.error("Car Model Not Found: {}".format(car_model_id))
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending update_car_types script at {}".format(cur_time))
