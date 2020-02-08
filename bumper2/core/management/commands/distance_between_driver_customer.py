"""
    Use Google map API to find distance between the driver_location and booking_address.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from core.models.booking import Booking, BookingAddress
import googlemaps
import logging
import csv
from django.db.models import Prefetch

logger = logging.getLogger('bumper.scripts')


def get_gmaps_distance(source, destination):
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAP_API_KEY_FOR_DISTANCE_MATRIX)
    try:
        logger.info("source: %s destination: %s" % (source, destination))
        directions_result = gmaps.distance_matrix(source, destination,
                                                  mode="driving")
        logger.info("directions_result_distance: %s" % directions_result)
        return directions_result
    except Exception as e:
        logger.exception("Failed To get distance on Google map", e)


class Command(BaseCommand):
    can_import_settings = True

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('days', type=int)

    def handle(self, *args, **options):
        number_of_days = options['days']
        logger.info("number_of_days: %s" % number_of_days)
        current_time = timezone.now()
        logger.info("Script started - current_time: %s" % current_time)

        with open('pickup_drop_distance_report.csv', 'w') as csvfile:
            fieldnames = ['BOOKING ID', 'PICKUP CREW','PICKUP DISTANCE', 'DROP CREW','DROP DISTANCE']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            time_interval = timezone.now() - timedelta(days=number_of_days)  # use timezone
            booking_pickup_addresses = BookingAddress.objects.filter(type=1)
            booking_drop_addresses = BookingAddress.objects.filter(type=2)
            booking_obj_list = Booking.objects.select_related('pickup_driver', 'drop_driver') \
                .prefetch_related(
                Prefetch('booking_address', queryset=booking_pickup_addresses, to_attr='pick_address'),
                Prefetch('booking_address', queryset=booking_drop_addresses, to_attr='drop_address'),
                'booking_address__address') \
                .filter(status_id__gte=9, created_at__gte=time_interval).exclude(status_id=24)

            for booking_obj in booking_obj_list:
                try:
                    pickup_address = booking_obj.pick_address
                    if pickup_address:
                        cust_pickup_loc = (pickup_address[0].address.latitude,
                                           pickup_address[0].address.longitude)
                        driver_pickup_update_history = booking_obj.history.filter(status_id=6).order_by(
                            'updated_at').first()
                        if driver_pickup_update_history:
                            driver_pickup_update_loc = (driver_pickup_update_history.latitude,
                                                        driver_pickup_update_history.longitude)
                            if all(driver_pickup_update_loc + cust_pickup_loc):
                                directions_result = get_gmaps_distance(driver_pickup_update_loc, cust_pickup_loc)
                                logger.info("Pickup Direction result: %s" % directions_result)
                                if directions_result:
                                    writer.writerow(
                                        {'BOOKING ID': booking_obj.id, 'PICKUP CREW': booking_obj.pickup_driver.name,
                                         'PICKUP DISTANCE':
                                             directions_result['rows'][0]['elements'][0]['distance'][
                                                 'text']})

                    drop_address = booking_obj.drop_address
                    if drop_address:
                        cust_drop_loc = (drop_address[0].address.latitude,
                                         drop_address[0].address.longitude)
                        driver_drop_update_history = booking_obj.history.filter(status_id=21).order_by(
                            'updated_at').first()
                        if driver_drop_update_history:
                            driver_drop_update_loc = (driver_drop_update_history.latitude,
                                                      driver_drop_update_history.longitude)
                            if all(driver_drop_update_loc + cust_drop_loc):
                                directions_result = get_gmaps_distance(driver_drop_update_loc, cust_drop_loc)
                                logger.info("Drop Direction result: %s" % directions_result)
                                if directions_result:
                                    writer.writerow(
                                        {'BOOKING ID': booking_obj.id, 'DROP CREW': booking_obj.drop_driver.name,
                                         'DROP DISTANCE':
                                             directions_result['rows'][0]['elements'][0]['distance'][
                                                 'text']})
                except:
                    logger.exception("Failed at this booking_id:%s to fetch the distance" % booking_obj.id)
        logger.info("Script ended")
        csvfile.close()
