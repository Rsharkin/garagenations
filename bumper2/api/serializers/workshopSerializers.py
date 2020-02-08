from rest_framework import serializers
from core.models.workshop import WorkshopResources
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from core.utils import _convert_to_given_timezone


class WorkshopResourcesSerializer(serializers.ModelSerializer):
    on_date = serializers.DateField(required=False, default=_convert_to_given_timezone(timezone.now(), settings.TIME_ZONE).date())
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    class Meta:
        model = WorkshopResources
        fields = ('__all__')

    def save(self, **kwargs):
        request = self.context.get('request')
        kwargs['updated_by'] = request.user
        super(WorkshopResourcesSerializer, self).save(**kwargs)


class GetResourcesByDateSerializer(serializers.Serializer):
    on_date = serializers.DateField(required=True)
    type_of_record = serializers.ChoiceField(required=False, choices=WorkshopResources.TYPE_OF_RECORDS,
                                             default=WorkshopResources.TYPE_OF_RECORD_DAILY)
