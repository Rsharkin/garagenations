# -*- coding: utf-8 -*-
__author__ = 'deepakraj'

import sys, os, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.staging_settings'
# To use in local machine / staging just change the settings to 'bumper2.local_settings' or 'bumper2.staging_settings'
django.setup()
from django.conf import settings
from core.models.master import CarModel
from decimal import Decimal
from django.utils import timezone
import logging
import glob

logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting update_carmodel_with_years.py script at {}".format(cur_time))


import csv
import os.path
if os.path.isfile("temp1.csv"):
    print "exists"
else:
    print "not exists and create one."
    with open('temp1.csv', 'wb') as myfile_new:
        wr = csv.writer(myfile_new, quoting=csv.QUOTE_ALL)




with open('All Car Models with Years-Table 1.csv', 'r+') as car_file:
    csv_headings = next(car_file)
    csv_headings_data = csv_headings.strip('\n').strip('\r').split(',')
    myfile=open('temp1.csv', 'wb')
    writer1 = csv.writer(myfile)
    writer1.writerow(csv_headings_data)

    for line,row in enumerate(car_file):
        try:
            row_data = row.strip('\n').strip('\r').split(',')
            logger.info("Processing: {}".format(row_data))
            #  Col0 is car_id
            car_id = row_data[0]
            #  Col1 is Model Year
            car_model_year_from_excel = str(row_data[2])

            car_model = CarModel.objects.get(id=car_id)
            car_model_year_from_server = str(car_model.start_year) + " - " + str(car_model.end_year)

            pass_yes_value = None
            if car_model_year_from_excel == car_model_year_from_server:
                pass_yes_value = "YES"
            else:
                pass_yes_value = "NO"

            row_data[3]=car_model_year_from_server
            row_data[4]=pass_yes_value

            writer1.writerow(row_data)
        except:
            logger.exception("Error in line: {}".format(row))
    car_file.close()
    myfile.close()



with open('temp1.csv', 'r+') as new_car_file:
    new_car_file.next()
    temparray = []
    for new_row in new_car_file:
        try:
            new_row_data = new_row.strip('\n').strip('\r').split(',')
            temparray.append(new_row_data)

            car_id = row_data[0]

            start_year_at_excel = row_data[2]
        except:
            logger.exception("Error in line: {}".format(row))

    values = set(map(lambda x: x[1], temparray))
    newlist = [[y for y in temparray if y[1] == x] for x in values]

    if newlist:
        for singleGroup in newlist:
            if len(singleGroup) > 1:
                latest_car = singleGroup[-1]
                car_id = latest_car[0]
                year_of_made_for_latest_car = latest_car[2].split(" - ", 1)
                car_model = CarModel.objects.get(id=car_id)
                car_model.start_year = year_of_made_for_latest_car[0]
                if year_of_made_for_latest_car[1] == "None":
                    year_of_made_for_latest_car[1] = None
                else:
                    pass
                car_model.end_year = year_of_made_for_latest_car[1]
                car_model.save()

                list_without_latest_car = singleGroup[:-1]
                if len(list_without_latest_car)>1:
                    for each_element in list_without_latest_car:
                        duplicate_car_model = car_model
                        duplicate_car_model.id = None
                        year_from_excel_for_car_more_than_1 = each_element[2].split(" - ", 1)

                        duplicate_car_model.start_year = year_from_excel_for_car_more_than_1[0]
                        if year_from_excel_for_car_more_than_1[1] == "None":
                            year_from_excel_for_car_more_than_1[1] = None
                        else:
                            pass

                        duplicate_car_model.parent_id = car_id
                        duplicate_car_model.end_year = year_from_excel_for_car_more_than_1[1]
                        duplicate_car_model.save()
                else:
                    #clone the existing car and set the id to none it will create a dummy car
                    duplicate_car_model = car_model
                    duplicate_car_model.id = None
                    year_from_excel_for_car = list_without_latest_car[0][2].split(" - ", 1)

                    duplicate_car_model.start_year = year_from_excel_for_car[0]
                    if year_from_excel_for_car[1] == "None":
                        year_from_excel_for_car[1] = None
                    else:
                        pass
                    duplicate_car_model.parent_id = car_id
                    duplicate_car_model.end_year = year_from_excel_for_car[1]
                    duplicate_car_model.save()
            else:
                singleCar = singleGroup[0]
                car_id = singleCar[0]
                year_of_made_on_single_car = singleCar[2].split(" - ", 1)
                car_model_single = CarModel.objects.get(id=car_id)
                car_model_single.start_year = year_of_made_on_single_car[0]
                if year_of_made_on_single_car[1] == "None":
                    year_of_made_on_single_car[1] = None
                else:
                    pass
                car_model_single.end_year = year_of_made_on_single_car[1]
                car_model_single.save()
    new_car_file.close()


cur_time = timezone.now()
logger.info("Ending update_carmodel_with_years.py script at {}".format(cur_time))
