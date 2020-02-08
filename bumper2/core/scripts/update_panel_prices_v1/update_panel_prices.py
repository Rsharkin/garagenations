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

logger = logging.getLogger('bumper.scripts')

# assume that this is only for "replace" type of work.
# get file data
# for each record, if panel id exist - update the prices else create new records with prices.

hatchback_file = open('hatchback.csv')
hatchback_file.next() # this is to avoid processing header
sedan_file = open('sedan.csv')
sedan_file.next()
suv_file = open('suv.csv')
suv_file.next()

type_of_work = 3 # only for replace

cur_time = timezone.now()
logger.info("Starting update_panel_prices script at {}".format(cur_time))

city_id = 1

files = [{'f':hatchback_file, 'car_type':1},{'f':sedan_file, 'car_type':2},{'f':suv_file, 'car_type':3}]

for f in files:
    car_file = f.get('f')
    car_type = f.get('car_type')
    for row in car_file:
        try:
            row_data = row.strip('\n').strip('\r').split(',')
            logger.info("Processing: {}".format(row_data))
            # col 3 is car panel id
            car_panel_id = row_data[2] if not '' else None
            # col 0 is name of panel
            name = row_data[0]
            # col 2 is internal flag
            internal = False if row_data[1] == 'N' else True
            # col 4 is part_type
            part_type = 1 if row_data[3] == 'Panel' else 2
            # col 6 is part price
            try:
                part_price = Decimal(row_data[5])
            except:
                part_price = Decimal('0.00')
            # col 7 is material price
            try:
                material_price = Decimal(row_data[6])
            except:
                material_price = Decimal('0.00')
            # col 8 is labour price
            try:
                labour_price = Decimal(row_data[7])
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
