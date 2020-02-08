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

h1 = open('h1.csv')
h1.next() # this is to avoid processing header
h1.next() # this is to avoid processing header

type_of_work = 3 # only for replace

cur_time = timezone.now()
logger.info("Starting add panels script at {}".format(cur_time))

city_id = 1

for row in h1:
    try:
        row_data = row.strip('\n').strip('\r').split(',')
        logger.info("Processing: {}".format(row_data))
        # col 3 is car panel id
        car_panel_id = row_data[5] if not '' else None
        # col 0 is name of panel
        name = row_data[0]
        # col 4 is part_type
        part_type = 1 if row_data[6] == 'Panel' else 2
        # col 6 is part price
        if not car_panel_id:
            cp = CarPanel.objects.create(name=name,part_type=part_type,
                                         photo='d6c8411f-4e79-4d6f-9bda-53278fcd0b52.png',
                                         big_photo='d6c8411f-4e79-4d6f-9bda-53278fcd0b52.png',
                                         internal=True)
            logger.info("Car Panel Created: {}".format(cp.id))
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending add panels script at {}".format(cur_time))
