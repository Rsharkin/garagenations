__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from django.conf import settings
from core.models.master import Package, PackagePrice
from decimal import Decimal
from django.utils import timezone
import logging
import glob

logger = logging.getLogger('bumper.scripts')

# THIS NEEDS TO BE IMPROVED BECAUSE OF NULL PRICES.

cur_time = timezone.now()
logger.info("Starting update_package_prices_v2 script at {}".format(cur_time))

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
    car_file = open(fname)
    car_type = segment_dict[fname] # change it according to filename
    car_file.next()

    for row in car_file:
        try:
            row_data = row.strip('\n').strip('\r').split(',')
            logger.info("Processing: {}".format(row_data))
            # col 5 is car panel id
            package_id = row_data[1] if not '' else None
            if not package_id:
                continue
            # col 0 is name of package
            name = row_data[0]
            # col 4 is internal flag
            internal = False if row_data[2] == 'N' else True
            part_price = Decimal('0.00')
            # col 3 is material price
            try:
                material_price = Decimal(row_data[3])
            except:
                material_price = Decimal('0.00')
            # col 4 is labour price
            try:
                labour_price = Decimal(row_data[4])
            except:
                labour_price = Decimal('0.00')

            pp = None
            if package_id:
                pp = PackagePrice.objects.filter(package_id=package_id,car_type=car_type).first()
            if pp:
                pp.part_price = part_price
                pp.material_price = material_price
                pp.labour_price = labour_price
                pp.save()
                logger.info("Car Package Price Updated: {}".format(pp.id))
            else:
                p = None
                if package_id:
                    p = Package.objects.filter(id=package_id).first()
                if p:
                    pp = PackagePrice.objects.create(package=p, car_type=car_type,
                                                   part_price=part_price,material_price=material_price,
                                                   labour_price=labour_price,price=0)
                logger.info("Car Package Price Created: {}".format(pp.id))
        except:
            logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending update_package_prices script at {}".format(cur_time))
