__author__ = 'anuj'
from django.utils.timezone import now
import logging
logger = logging.getLogger(__name__)


class AllowFieldLimitingMixin(object):
    """
    A mixin for a generic APIView that will allow the serialized fields to be
    limited to a set of comma-separated values, specified via the `fields`
    query parameter.  This will only apply to GET requests.
    """
    _serializer_class_for_fields = {}

    def get_serializer_class_for_fields(self, serializer_class, fields):
        fields = fields.strip().split(',')
        fields.sort()
        fields = tuple(fields)
        if fields in self._serializer_class_for_fields:
            return self._serializer_class_for_fields[fields]
        # Doing this because a simple copy.copy() doesn't work here.
        meta = type('Meta', (serializer_class.Meta, object), {'fields': fields})
        LimitedFieldsSerializer = type('LimitedFieldsSerializer', (serializer_class,),
            {'Meta': meta})
        self._serializer_class_for_fields[fields] = LimitedFieldsSerializer
        return LimitedFieldsSerializer

    def get_serializer_class(self):
        """
        Allow the `fields` query parameter to limit the returned fields
        in list and detail views.  `fields` takes a comma-separated list of
        fields.
        """
        serializer_class = super(AllowFieldLimitingMixin, self).get_serializer_class()
        fields = self.request.query_params.get('fields')
        if self.request.method == 'GET' and fields:
            return self.get_serializer_class_for_fields(serializer_class, fields)
        return serializer_class


class LoggingMixin(object):
    """Mixin to log requests"""
    def initial(self, request, *args, **kwargs):
        """Set current time on request"""
        # get data dict
        try:
            data_dict = request.data.dict()
        except AttributeError:  # if already a dict, can't dictify
            data_dict = request.data

        # # get IP
        # ipaddr = request.META.get("HTTP_X_FORWARDED_FOR", None)
        # if ipaddr:
        #     # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
        #     ipaddr = ipaddr.split(", ")[0]
        # else:
        #     ipaddr = request.META.get("REMOTE_ADDR", "")

        # save to log


        # regular intitial, including auth check
        super(LoggingMixin, self).initial(request, *args, **kwargs)

        # add user to log after auth
        user = request.user

        logger.info("------API Request User %s" % (user))
        logger.info("------API Request %s - requested_at: %s, method:%s, query_params:%s, "
                    "data:%s, Source:%s, AppVersion:%s" % (request.path, now(),
                                            request.method, request.query_params.dict(),
                                            data_dict, request.META.get('HTTP_SOURCE'),
                                            request.META.get('HTTP_VERSION')))


class CreateListModelMixin(object):
    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(CreateListModelMixin, self).get_serializer(*args, **kwargs)