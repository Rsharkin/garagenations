__author__ = 'anuj'

import sys, os, django
import logging
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from core.models.master import ChecklistCategory, ChecklistItem
from django.utils import timezone
from django.db.models import Max


logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting update_checklist script at {}".format(cur_time))
fname = 'checklists.csv'

f = open(fname)
f.next()

for row in f:
    try:
        row_data = row.strip('\n').strip('\r').split(',')
        logger.info("Processing: {}".format(row_data))
        category = row_data[2].strip()
        cc = ChecklistCategory.objects.filter(category=category).first()
        max_order = ChecklistItem.objects.filter(category=cc).aggregate(Max('order_num'))
        item_name = row_data[1].strip()
        item_id = row_data[0].strip()
        ci = None
        if item_id:
            ci = ChecklistItem.objects.filter(id=item_id).first()
        if not ci:
            ci = ChecklistItem.objects.get(id=1)
            ci.order_num = max_order['order_num__max'] + 1
            ci.pk = None
        ci.name = item_name
        ci.active = True
        ci.category = cc
        if row_data[3].strip() == '1':
            ci.active = False
        ci.save()
        logger.info("Checklist Item added/updated :%s", ci.id)
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending update_checklist script at {}".format(cur_time))
