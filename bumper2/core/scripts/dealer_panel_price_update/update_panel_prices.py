__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.master import CarPanelPrice, CarPanel, CarModel
from decimal import Decimal
from django.utils import timezone
import logging
import glob

logger = logging.getLogger('bumper.scripts')

# assume that this is only for "replace" type of work.
# get file data
# for each record, if panel id exist - update the prices else create new records with prices.

cur_time = timezone.now()
logger.info("Starting dealer_panel_price_update script at {}".format(cur_time))
fname = 'dealer_pricing.csv'

car_file = open(fname)
car_file.next()

for row in car_file:
    try:
        row_data = row.strip('\n').strip('\r').split(',')
        logger.info("Processing: {}".format(row_data))
        # col 1 is car panel id
        car_panel_id = row_data[1] if not '' else None
        if not car_panel_id:
            continue
        # col 0 is model id
        car_model_id = row_data[0]

        scratch = row_data[3]
        dent = row_data[4]
        replace = row_data[5]
        part_price = Decimal('0.00')
        material_price = Decimal('0.00')
        labour_price = Decimal('0.00')
        for i in range(3):
            if i == 0:
                if not scratch or scratch == 'NA':
                    continue
                try:
                    lab_mat_price = Decimal(scratch)
                except:
                    lab_mat_price = Decimal('0.00')
                type_of_work = 1
            elif i == 1:
                if not dent or dent == 'NA':
                    continue
                try:
                    lab_mat_price = Decimal(dent)
                except:
                    lab_mat_price = Decimal('0.00')
                type_of_work = 2
            else:
                if not replace or replace == 'NA':
                    continue
                try:
                    lab_mat_price = Decimal(dent)
                except:
                    lab_mat_price = Decimal('0.00')
                try:
                    part_price = Decimal(dent)
                except:
                    part_price = Decimal('0.00')
                type_of_work = 3

            material_price = lab_mat_price * Decimal('0.3')
            labour_price = lab_mat_price * Decimal('0.7')

            cm = CarModel.objects.filter(id=car_model_id).first()
            if cm:
                cpp = None
                if car_panel_id:
                    cpp = CarPanelPrice.objects.filter(car_panel_id=car_panel_id, car_model=cm,
                                                       type_of_work=type_of_work).first()
                if not cpp:
                    cpp = CarPanelPrice.objects.filter(car_panel_id=car_panel_id,car_type=cm.car_type,
                                                   type_of_work=type_of_work).first()
                    if cpp:
                        cpp.pk = None

                if cpp:
                    cpp.car_model = cm
                    cpp.car_type = None
                    cpp.dealer_part_price = part_price
                    cpp.dealer_material_price = material_price
                    cpp.dealer_labour_price = labour_price
                    cpp.show_savings = True
                    cpp.save()
                    logger.info("Car Panel Price Updated: {}".format(cpp.id))
                else:
                    logger.error("Car Panel Price not found: {}".format(row_data))
            else:
                logger.error("Car Model ID not found: {}".format(car_model_id))
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending dealer_panel_price_update script at {}".format(cur_time))
