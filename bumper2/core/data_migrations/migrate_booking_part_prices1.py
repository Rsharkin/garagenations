__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from core.models.booking import *
from core import constants
from decimal import Decimal
import traceback

def update_panel_part_price(cols):
    try:
        bpp_id = cols[0]
        part_price = cols[1]
        material_price = cols[2]
        labour_price = cols[3]
        bpp = BookingPackagePanel.objects.get(id=bpp_id)
        bpp.part_price = Decimal(part_price).quantize(constants.TWO_PLACES)
        bpp.material_price = Decimal(material_price).quantize(constants.TWO_PLACES)
        bpp.labour_price = Decimal(labour_price).quantize(constants.TWO_PLACES)
        bpp.save()
    except:
        print traceback.print_exc()
        print "Error in processing row %s" % cols


f = open('/srv/www/bumper2/core/data_migrations/booking_prices_tanvi1.csv', 'r') # upto booking id 14326
for line in f:
    cols = line.strip('\n').strip().split(',')
    update_panel_part_price(cols)