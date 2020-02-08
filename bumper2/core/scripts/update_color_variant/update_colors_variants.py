__author__ = 'anuj'

import sys
import os
import django
import logging
import ast
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from core.models.master import CarModel, CarModelVariant, CarColor
from django.utils import timezone

logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting update_color_variants script at {}".format(cur_time))
fname = 'car_colors_variants.csv'

f = open(fname)
f.next()

for row in f:
    try:
        row_data = row.strip().split(';')
        logger.info("Processing: {}".format(row_data))
        variant_list = ast.literal_eval(ast.literal_eval(row_data[6]))
        color_list = ast.literal_eval(ast.literal_eval(row_data[7]))
        brand = row_data[0]
        model_name = row_data[2]
        model_name = model_name.replace(brand+" ", "")
        car_models = CarModel.objects.filter(name=model_name)
        if car_models:
            variant_obj_list = []
            for variant in variant_list:
                if variant.get('variant'):
                    car_model_variant, created = CarModelVariant.objects.get_or_create(name=variant.get('variant'))
                    variant_obj_list.append(car_model_variant)
            color_obj_list = []
            for color in color_list:
                if color.get('color'):
                    car_color, created = CarColor.objects.get_or_create(color_name=color.get('color'))
                    color_obj_list.append(car_color)
            for car_model in car_models:
                car_model.variants = variant_obj_list
                car_model.colors = color_obj_list
            logger.debug("Added colors and variants for model: %s, colors: %s, variants: %s",
                         model_name, color_obj_list, variant_obj_list)
        else:
            logger.debug("No Model with this name exist in our system: %s", model_name)
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending update_color_variants script at {}".format(cur_time))
