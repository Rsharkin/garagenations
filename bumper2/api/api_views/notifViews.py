__author__ = 'anuj'

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import TokenAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from core.models.message import Messages
from api.serializers.notifSerializers import MessageSerializer
from api.api_views.custom_mixins import LoggingMixin
from api.permissions import MessageUserIsOwnerOrAdmin
from rest_framework.pagination import PageNumberPagination
from rest_framework_bulk import generics as bulk_generics


class MessageMixin(object):
    model = Messages
    queryset = Messages.objects.all()
    serializer_class = MessageSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('message_type', 'booking', 'label')


class MessageViewSet(LoggingMixin, MessageMixin, bulk_generics.BulkModelViewSet):
    """
    API endpoint that allows notifications to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (MessageUserIsOwnerOrAdmin, )

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        queryset = Messages.objects.all()
        if not self.request.user.groups.filter(name='OpsUser').exists():
            queryset = Messages.objects.filter(user_message__user=self.request.user).prefetch_related('user_message')
        return queryset.order_by('-created_at')

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)





