__author__ = 'anuj'

import sys, os, django
import logging
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from core.models.master import CarPanel
from django.utils import timezone


logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting update_panels script at {}".format(cur_time))
fname = 'carpanel.csv'

f = open(fname, 'rU')
f.next()

for row in f:
    try:
        row_data = row.strip('\n').strip('\r').split(',')
        logger.info("Processing: {}".format(row_data))
        sort_order = row_data[7].strip()
        car_panel_id = row_data[0].strip()
        if sort_order and car_panel_id:
            try:
                sort_order = int(sort_order)
                cp = CarPanel.objects.filter(id=car_panel_id).first()
                cp.sort_order = sort_order
                cp.save()
                logger.info("CarPanel updated :%s", cp.id)
            except ValueError:
                logger.info("sort order is not an int")
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending update_panels script at {}".format(cur_time))
