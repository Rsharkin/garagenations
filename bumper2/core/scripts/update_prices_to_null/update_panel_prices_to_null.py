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
logger.info("Starting update panel price to null script at {}".format(cur_time))


cpp_list = CarPanelPrice.objects.all()
for cpp in cpp_list:
    try:
        logger.info("Processing: {}".format(cpp.id))
        if cpp.type_of_work == 3:
            cpp.part_price = None
            cpp.save()
            logger.error("Panel Price updated: {}".format(cpp.id))
        elif cpp.type_of_work > 3 and cpp.type_of_work != 9:
            cpp.part_price = None
            cpp.material_price = None
            cpp.labour_price = None
            cpp.save()
            logger.error("Panel Price updated: {}".format(cpp.id))
    except:
        logger.exception("Error in line: {}".format(cpp.id))

cur_time = timezone.now()
logger.info("Ending update panel price to null script at {}".format(cur_time))
