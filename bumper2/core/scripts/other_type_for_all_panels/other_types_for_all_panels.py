__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.master import CarPanel, CarPanelPrice
from decimal import Decimal
from django.utils import timezone
import logging
import glob

logger = logging.getLogger('bumper.scripts')

# assume that this is only for "replace" type of work.
# get file data
# for each record, if panel id exist - update the prices else create new records with prices.

cur_time = timezone.now()
logger.info("Starting other types for all panels to null script at {}".format(cur_time))

car_types = [4,5,6,7,8,9,10,11,12,13]
type_of_works = [5,6,7]

cp_list = CarPanel.objects.filter(part_type=1)
for cp in cp_list:
    try:
        logger.info("Processing: {}".format(cp.id))
        for car_type in car_types:
            for type_of_work in type_of_works:
                cpp = CarPanelPrice.objects.filter(car_panel=cp, type_of_work=type_of_work, car_type=car_type).first()
                if not cpp:
                    cpp = CarPanelPrice.objects.create(car_panel=cp, car_type=car_type, type_of_work=type_of_work,
                                                       internal=True, editable=True, part_price=0,
                                                       material_price=None,
                                                       labour_price=None, active=True, city_id=1, price=0)

                    logger.error("Car Panel Price created: id-{}, type_of_work - {}, car_type - {}".format(cpp.id,
                                                                                                           cpp.type_of_work,
                                                                                                           cpp.car_type))
    except:
        logger.exception("Error in line: {}".format(cp.id))

cur_time = timezone.now()
logger.info("Ending update panel price to null script at {}".format(cur_time))
