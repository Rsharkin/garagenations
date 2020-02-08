__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.master import PackagePrice
from decimal import Decimal
from django.utils import timezone
import logging
import glob

logger = logging.getLogger('bumper.scripts')

# assume that this is only for "replace" type of work.
# get file data
# for each record, if panel id exist - update the prices else create new records with prices.

cur_time = timezone.now()
logger.info("Starting update_pacakge_price script at {}".format(cur_time))

car_file = open('carmodeldata.csv')
segment_dict = {
    1:[5,6,7],
    2:[8,9,10,11],
    3:[12,13]
}

pp_list = PackagePrice.objects.all()
for pp in pp_list:
    try:
        logger.info("Processing: {}".format(pp.id))
        new_car_types = segment_dict.get(pp.car_type,[])
        for car_type in new_car_types:
            pp.pk = None
            pp.car_type = car_type
            pp.save()
            logger.error("Package Price added: {}".format(pp.id))
    except:
        logger.exception("Error in line: {}".format(pp.id))

cur_time = timezone.now()
logger.info("Ending update_package_price script at {}".format(cur_time))
