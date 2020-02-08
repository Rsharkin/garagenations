import json
import logging
import urllib2  # python does not have support for this. When migrating to python 3 will use urllib.request

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import ujson

from api.api_views.custom_mixins import LoggingMixin
from api.permissions import HasGroupPermission
from api.serializers.notifSerializers import SendNoticeSerializer, RequestLocationNoticeSerializer
from api.serializers.reportSerializer import ReportSerializer, RecordingsSerializer, RecordingsWithDateSerializer
from core.managers.pushNotificationManager import send_notification, request_location_of_user
from core.managers.reportEngine import ReportGridEngine
from core.managers.workshopManager import generate_workshop_schedule

logger = logging.getLogger(__name__)


class ReportViewSet(LoggingMixin,viewsets.GenericViewSet):
    """
    API endpoint for report.
    """
    authentication_classes = (JSONWebTokenAuthentication)
    # permission_classes = (UserIsOwnerOrAdminOrPost,)
    serializer_class = ReportSerializer

    @list_route(methods=['get'],authentication_classes=[JSONWebTokenAuthentication])
    def build_report(self, request):
        logger.debug('--------------- API_build_report By user(%s) request=%s' % (request.user, str(request.REQUEST)))

        serializer = ReportSerializer(data=self.request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            grid = ReportGridEngine(data.get('report_type'))
            return Response({'data': grid.get_json_without_paging(request)})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['get'], authentication_classes=[JSONWebTokenAuthentication])
    def get_ads_data(self, request):
        logger.debug('--------------- API get_ads_data request=%s' % str(request.REQUEST))

        from django.db.models import Count
        user_model = get_user_model()
        data = {
            # 'utm_source': BumperUser.objects.values_list('utm_source', flat=True).distinct(),
            'utm_source': list(user_model.objects.values('utm_source').annotate(dcount=Count('utm_source'))),
            'utm_medium': list(user_model.objects.values('utm_medium').annotate(dcount=Count('utm_medium'))),
            'utm_campaign': list(user_model.objects.values('utm_campaign').annotate(dcount=Count('utm_campaign'))),
        }
        return Response({'data': data})

    @list_route(methods=['get'], authentication_classes=[JSONWebTokenAuthentication])
    def get_recordings(self, request):
        logger.debug('--------------- API get_recordings request=%s' % str(request.REQUEST))
        serializer = RecordingsSerializer(data=self.request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            url = "https://ninjacrm.com/bumper/api/fetchCDR.php?dealer=bumper&module=0&action=getBumperCDR" \
                  "&from_date=2015-08-15&to_date=%s" % str(timezone.now().date() + timezone.timedelta(days=1))
            url += '&mobiles=%s' % data.get('phone_numbers')
            try:
                response = urllib2.urlopen(url)
                data = json.load(response)
                return Response({'recordings': data})
            except:
                logger.exception('Failed to fetch recordings.')
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'data': '', 'message': 'Failed to fetch recordings.'})

    @list_route(methods=['get'], authentication_classes=[JSONWebTokenAuthentication])
    def get_recordings_within_dates(self, request):
        logger.debug('--------------- API get_recordings_within_dates request=%s' % str(request.REQUEST))
        serializer = RecordingsWithDateSerializer(data=self.request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            url = "https://ninjacrm.com/bumper/api/fetchCDR.php?dealer=bumper&module=0&action=getBumperCDR" \
                  "&from_date=%s&to_date=%s" % (data.get('start_date'), data.get('end_date'))
            if data.get('phone_numbers'):
                url += '&mobiles=%s' % data.get('phone_numbers')
            try:
                response = urllib2.urlopen(url)
                data = json.load(response)
                return Response({'recordings': data})
            except:
                logger.exception('Failed to fetch recordings.')
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'data': '', 'message': 'Failed to fetch recordings.'})

    @list_route(methods=['get'], authentication_classes=[JSONWebTokenAuthentication])
    def get_workshop_schedule(self, request):
        logger.debug('--------------- API get_workshop_schedule request=%s' % str(request.REQUEST))
        days_to_plan_for = 7
        resources = ujson.loads(self.request.query_params["resources"])
        remove_list = []
        if "removeList" in self.request.query_params and self.request.query_params["removeList"] != 'undefined' \
                and self.request.query_params["removeList"] != '':
            remove_list = str(self.request.query_params["removeList"]).split(',')

        use_current_status = True if self.request.query_params.get("useCurrentStatus") == '1' else False
        workshop = int(self.request.query_params.get("workshop"))

        all_bookings_with_eod, \
        projected_delayed_bookings, \
        bumper_workshop_resources, \
        datewise_booking_allocation = generate_workshop_schedule(days_to_plan_for, resources, remove_list, workshop,
                                                                 use_current_status=use_current_status)
        data = {
            "all_bookings_with_eod": all_bookings_with_eod,
            "bumper_workshop_resources": bumper_workshop_resources,
            "days_to_plan_for": days_to_plan_for,
            "datewise_booking_allocation": datewise_booking_allocation,
            "projected_delayed_bookings": projected_delayed_bookings,
        }
        return Response({"data": data}, status=status.HTTP_200_OK)


class NotificationViewSet(LoggingMixin, viewsets.GenericViewSet):
    """
        API endpoint for notification.
    """
    authentication_classes = (JSONWebTokenAuthentication)
    permission_classes = [HasGroupPermission]
    required_groups = {
        'POST': ['OpsUser', 'OpsAdmin'],
    }
    serializer_class = SendNoticeSerializer

    @list_route(methods=['post'], authentication_classes=[JSONWebTokenAuthentication])
    def send_notification(self, request):
        logger.debug('--------------- API send_notification request=%s' % str(request.REQUEST))

        serializer = SendNoticeSerializer(data=self.request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            user_model = get_user_model()
            user_ids = str(data.get('user_ids', '')).split(',')
            users = user_model.objects.filter(id__in=user_ids)
            send_notification(users, data, sent_by_id=request.user.id)
            return Response({'data': 'Message Sent.'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['post'], authentication_classes=[JSONWebTokenAuthentication])
    def request_location(self, request):
        logger.debug('--------------- API request_location request=%s' % str(request.REQUEST))

        serializer = RequestLocationNoticeSerializer(data=self.request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            user_model = get_user_model()
            user_ids = str(data.get('user_ids', '')).split(',')
            users = user_model.objects.filter(id__in=user_ids)
            request_location_of_user(users, sent_by_id=request.user.id)
            return Response({'data': 'Request Sent.'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)