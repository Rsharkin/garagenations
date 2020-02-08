"""
    Use Google map API to assign drivers to bookings.
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.booking import Booking, BookingAddress
from core.utils import _convert_to_given_timezone, make_datetime_timezone_aware_convert_to_utc, format_datetime_for_grid
import googlemaps
import logging
logger = logging.getLogger('bumper.scripts')

GOOGLE_MAP_API_KEY = "AIzaSyCZuPNa7waiT1PRkIfxDHi09FN_gNJP75A"
DRIVER_1_LOC_LAT = "12.937644"
DRIVER_1_LOC_LONG = "77.6244282"

DRIVER_2_LOC_LAT = "12.9217254"
DRIVER_2_LOC_LONG = "77.653496"

class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: CREW_SCHEDULING:: Assign Bookings to crew using google map APIs'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--only_pickup',
            action='store_true',
            dest='only_pickup',
            default=False,
            help='Process Only pickups',
        )

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: CREW_SCHEDULING:: Script started - current_time: %s" % current_time)
        gmaps = googlemaps.Client(key=GOOGLE_MAP_API_KEY)

        only_pickup = options['only_pickup']

        # pickup time in next day
        current_context_time = _convert_to_given_timezone(timezone.now(), settings.TIME_ZONE)
        date_for_tomorrow_in_current_context = current_context_time + timezone.timedelta(days=1)
        start_time = make_datetime_timezone_aware_convert_to_utc(str(date_for_tomorrow_in_current_context.date())+" 00:00:00", "+0530")
        end_time = start_time + timezone.timedelta(hours=24)

        logger.info("Script:: CREW_SCHEDULING:: start_time: %s - end_Time: %s" % (start_time, end_time))

        try:
            pickup_in_next_day_bookings = Booking.objects.select_related('user')\
                .filter(status_id__lt=9, pickup_time__range =[start_time, end_time])\
                .exclude(ops_status_id=8)

            pickup_data = []
            for booking in pickup_in_next_day_bookings:
                address = booking.booking_address.filter(type=BookingAddress.ADDRESS_TYPE_PICKUP).first()
                directions_result = None
                try:
                    origins = [
                        (DRIVER_1_LOC_LAT, DRIVER_1_LOC_LONG),
                        (DRIVER_2_LOC_LAT, DRIVER_2_LOC_LONG),
                    ]
                    directions_result = gmaps.distance_matrix(origins,
                                                              (address.address.latitude, address.address.longitude),
                                                              mode="transit",
                                                              units="metric",
                                                              arrival_time=booking.pickup_time)
                except:
                    logger.exception("Script:: CREW_SCHEDULING:: Failed To get ETA based on Google map APIS.")

                pickup_data.append({
                    'bookingId': booking.id,
                    'name': booking.user.name,
                    'phone': booking.user.phone,
                    'time': booking.pickup_time,
                    'address_lat': address.address.latitude,
                    'address_long': address.address.longitude,
                    'driver': booking.pickup_driver,
                    'directions_result': directions_result
                })

            logger.info("Script:: CREW_SCHEDULING:: pickup data: %s" % (pickup_data))

        except:
            logger.exception("Script:: CREW_SCHEDULING:: Failed to process to bookings")