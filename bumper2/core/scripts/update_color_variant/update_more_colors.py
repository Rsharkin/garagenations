__author__ = 'anuj'

import sys
import os
import django
import logging
sys.path.append('/srv/www/bumper2/')
try:
    settings_file = sys.argv[1]
except IndexError:
    settings_file = 'bumper2.settings'
os.environ['DJANGO_SETTINGS_MODULE'] = settings_file
django.setup()
from core.models.master import CarModel, CarModelVariant, CarColor, CarBrand
from django.utils import timezone

logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting update_more_color_variants script at {}".format(cur_time))
fname = 'more_carcolors_1.csv'

f = open(fname)
f.next()

for row in f:
    try:
        row_data = row.strip().split(',')
        logger.info("Processing: {}".format(row_data))
        variant_str = row_data[8]
        color_str = row_data[7]
        variant_list = variant_str.split('|')
        color_list = color_str.split('|')
        try:
            brand_id = int(row_data[0])
        except:
            brand_id = None
        brand_name = row_data[1]
        try:
            model_id = int(row_data[2])
        except:
            model_id = None
        model_name = row_data[3]
        car_type = row_data[4]
        if not brand_id:
            brand, created = CarBrand.objects.get_or_create(name=brand_name)
            brand_id = brand.id
        if model_id:
            car_model = CarModel.objects.filter(id=model_id).first()
        else:
            car_model, created = CarModel.objects.get_or_create(brand_id=brand_id, name=model_name, car_type=car_type)

        if car_model:
            variant_obj_list = []
            for variant_name in variant_list:
                car_model_variant, created = CarModelVariant.objects.get_or_create(name=variant_name)
                variant_obj_list.append(car_model_variant)
            color_obj_list = []
            for color_name in color_list:
                car_color, created = CarColor.objects.get_or_create(color_name=color_name)
                color_obj_list.append(car_color)
            car_model.variants = variant_obj_list
            car_model.colors = color_obj_list
            logger.debug("Added colors and variants for brand:%s, model: %s, colors: %s, variants: %s",
                         brand_name, model_name, color_obj_list, variant_obj_list)
        else:
            logger.debug("No Model with this id exist in our system: %s", model_id)
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending update_more_color_variants script at {}".format(cur_time))
