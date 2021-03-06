__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.master import CarPanelPrice, CarPanel
from decimal import Decimal
from django.utils import timezone
import logging
import glob

logger = logging.getLogger('bumper.scripts')

# assume that this is only for "replace" type of work.
# get file data
# for each record, if panel id exist - update the prices else create new records with prices.

cur_time = timezone.now()
logger.info("Starting update_panel_prices_v2 script at {}".format(cur_time))

city_id = 1

segment_dict = {
    'h1.csv': 5,
    'h2.csv': 6,
    'h3.csv': 7,
    's1.csv': 8,
    's2.csv': 9,
    's3.csv': 10,
    'v1.csv': 11,
    'v2.csv': 12,
    'v3.csv': 13,
    'lux.csv': 4,
    'SUV': 13 # All remaining SUV were V3.
}

for fname in glob.glob("*.csv"):
    if fname in ('carmodeldata.csv', 'h1_old.csv'):
        continue

    car_file = open(fname)
    car_type = segment_dict[fname] # change it according to filename
    car_file.next()
    car_file.next()

    for row in car_file:
        try:
            row_data = row.strip('\n').strip('\r').split(',')
            logger.info("Processing: {}".format(row_data))
            # col 5 is car panel id
            car_panel_id = row_data[5] if not '' else None
            # col 0 is name of panel
            name = row_data[0]
            # col 4 is internal flag
            internal = False if row_data[4] == 'N' else True
            # col 6 is part_type
            part_type = 1 if row_data[6] == 'Panel' else 2
            # col 6 is part price
            scratch = row_data[1]
            dent = row_data[2]
            replace = row_data[3]
            for i in range(3):
                if i == 0:
                    if not scratch or scratch == 'NA':
                        continue
                    material_index = 7
                    labour_index = 8
                    type_of_work = 1
                elif i == 1:
                    if not dent or dent == 'NA':
                        continue
                    material_index = 9
                    labour_index = 10
                    type_of_work = 2
                else:
                    if not replace or replace == 'NA':
                        continue
                    material_index = 11
                    labour_index = 12
                    type_of_work = 3

                part_price = Decimal('0.00')
                # col 7 is material price
                try:
                    material_price = Decimal(row_data[material_index])
                except:
                    material_price = Decimal('0.00')
                # col 8 is labour price
                try:
                    labour_price = Decimal(row_data[labour_index])
                except:
                    labour_price = Decimal('0.00')

                cpp = None
                if car_panel_id:
                    cpp = CarPanelPrice.objects.filter(car_panel_id=car_panel_id,car_type=car_type,type_of_work=type_of_work).first()
                if cpp:
                    cpp.part_price = part_price
                    cpp.material_price = material_price
                    cpp.labour_price = labour_price
                    cpp.save()
                    logger.info("Car Panel Price Updated: {}".format(cpp.id))
                else:
                    cp = None
                    if car_panel_id:
                        cp = CarPanel.objects.filter(id=car_panel_id).first()
                    if not cp:
                        cp = CarPanel.objects.create(name=name,part_type=part_type,
                                                     photo='d6c8411f-4e79-4d6f-9bda-53278fcd0b52.png',
                                                     big_photo='d6c8411f-4e79-4d6f-9bda-53278fcd0b52.png',
                                                     internal=internal)
                        logger.info("Car Panel Created: {}".format(cp.id))
                    cpp = CarPanelPrice.objects.create(car_panel=cp, car_type=car_type,type_of_work=type_of_work,
                                                       internal=internal,part_price=part_price,material_price=material_price,
                                                       labour_price=labour_price,active=True,city_id=1,price=0)
                    logger.info("Car Panel Price Created: {}".format(cpp.id))
        except:
            logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending update_panel_prices script at {}".format(cur_time))
