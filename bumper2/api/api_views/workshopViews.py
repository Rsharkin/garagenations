from django.contrib.auth import get_user_model, authenticate
import logging
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import TokenAuthentication
from api.api_views.custom_mixins import LoggingMixin
from api.permissions import (IsAdminUser, IsWorkshopExecutive, PermissionOneOf)
from core.models.workshop import WorkshopResources
from api.serializers import workshopSerializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
logger = logging.getLogger(__name__)


class WorkshopResourcesViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
        API to update resources present in workshop
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (PermissionOneOf,)
    permissions_list = [IsWorkshopExecutive, IsAdminUser]
    queryset = WorkshopResources.objects.all()
    serializer_class = workshopSerializers.WorkshopResourcesSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('type_of_record',)

    @list_route(methods=['get'])
    def get_resources_by_date(self, request):
        """
            get pickup slots
        """
        serializer = workshopSerializers.GetResourcesByDateSerializer(data=request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            if data['type_of_record'] == WorkshopResources.TYPE_OF_RECORD_DAILY:
                details = WorkshopResources.objects.filter(on_date=data['on_date'],
                                                           type_of_record=data['type_of_record'])
            else:
                details = WorkshopResources.objects.filter(on_date__lte=data['on_date'],
                                                           type_of_record=data['type_of_record'])

            data = []
            for item in details:
                data.append(workshopSerializers.WorkshopResourcesSerializer(item).data)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)