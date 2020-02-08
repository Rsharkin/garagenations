__author__ = 'anuj'

from rest_framework import serializers
from core.models.message import MessageUser, Messages
from core.constants import NOTICE_TYPES
from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin


class MessageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageUser
        fields = '__all__'


class MessageSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    user_message = MessageUserSerializer(many=True,required=False)
    class Meta:
        model = Messages
        fields = '__all__'
        list_serializer_class = BulkListSerializer

    def update(self, instance, validated_data):
        user_messages = validated_data.pop('user_message',[])
        user = validated_data.pop('user')
        for attr, value in validated_data.items():
            if not isinstance(value, (list,dict)):
                setattr(instance, attr, value)
        for user_message in user_messages:
            MessageUser.objects.filter(message=instance, user=user).update(**user_message)
        return instance


class SendNoticeSerializer(serializers.Serializer):
    user_ids = serializers.CharField(required=True)
    notice_type = serializers.ChoiceField(choices=NOTICE_TYPES, required=True)
    label = serializers.ChoiceField(choices=Messages.LABEL_TYPES, required=True)
    title = serializers.CharField(max_length=32, required=True)
    message = serializers.CharField(max_length=256, required=True)


class RequestLocationNoticeSerializer(serializers.Serializer):
    user_ids = serializers.CharField(required=True)
