# -*- coding: utf-8 -*-
__author__ = 'deepakraj'

import sys, os, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.staging_settings'
# To use in local machine / staging just change the settings to 'bumper2.local_settings' or 'bumper2.staging_settings'
django.setup()
from core.models.master import CarPanelPrice, CarPanel
from django.utils import timezone
import logging
import decimal
from core import constants

logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting updating_new_type_of_work script at {}".format(cur_time))


def update_pricing_for_new_type_of_work(type_of_work_new, amount):
    cpp_dent_list = CarPanelPrice.objects.filter(type_of_work=CarPanelPrice.TYPE_OF_WORK_DENT,
                                                 car_panel__part_type=CarPanel.PART_PANEL)
    for cpp_dent_obj in cpp_dent_list:
        if type_of_work_new == CarPanelPrice.TYPE_OF_WORK_TEAR:
            if cpp_dent_obj.car_panel_id == 4 or cpp_dent_obj.car_panel_id == 5:
                amount = 600
            else:
                amount = 1800
        cpp_new_tow_obj = CarPanelPrice.objects.filter(type_of_work=type_of_work_new,
                                                       car_type=cpp_dent_obj.car_type,
                                                       car_panel_id=cpp_dent_obj.car_panel_id,
                                                       car_model_id=cpp_dent_obj.car_model_id,
                                                       city_id=cpp_dent_obj.city_id).first()
        if not cpp_new_tow_obj:
            logger.info("{} type of work not found with dent id {}".format(type_of_work_new, cpp_dent_obj.id))
            cpp_new_tow_obj = cpp_dent_obj
            cpp_new_tow_obj.pk = None
            cpp_new_tow_obj.type_of_work = type_of_work_new
        else:
            logger.info("{} type of work found with dent id {}, new_id: {}".format(type_of_work_new,
                                                                                   cpp_dent_obj.id,
                                                                                   cpp_new_tow_obj.id))
            cpp_new_tow_obj.labour_price = cpp_dent_obj.labour_price
            cpp_new_tow_obj.material_price = cpp_dent_obj.material_price
        update_price_val_fn(cpp_new_tow_obj, amount)


def update_price_val_fn(model_obj, amount_var):
    if model_obj.labour_price:
        model_obj.part_price = model_obj.part_price
        model_obj.material_price = (model_obj.material_price + (amount_var * decimal.Decimal(0.3))).\
            quantize(constants.TWO_PLACES)
        model_obj.labour_price =  (model_obj.labour_price + (amount_var * decimal.Decimal(0.7))).\
            quantize(constants.TWO_PLACES)
        model_obj.editable = False
        model_obj.show_savings = False
    else:
        logger.info("ERROR: price is 0 for the {} type of work".format(model_obj.type_of_work))
        model_obj.editable = True
    model_obj.internal = True
    model_obj.save()

cur_time = timezone.now()
logger.info("Ending updating_new_type_of_work script at {}".format(cur_time))

update_pricing_for_new_type_of_work(CarPanelPrice.TYPE_OF_WORK_CRUMPLED_PANEL, 1200)
update_pricing_for_new_type_of_work(CarPanelPrice.TYPE_OF_WORK_RUSTED_PANEL, 1800)
update_pricing_for_new_type_of_work(CarPanelPrice.TYPE_OF_WORK_TEAR, 600)
