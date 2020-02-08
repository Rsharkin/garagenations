from rest_framework import serializers
from django.utils import six
import re
from core.managers.reportManagerConstants import REPORT_TYPES


class ReportSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=REPORT_TYPES, required=True)


class RecordingsSerializer(serializers.Serializer):
    phone_numbers = serializers.CharField(max_length=2048, required=True)


class RecordingsWithDateSerializer(serializers.Serializer):
    phone_numbers = serializers.CharField(max_length=2048, required=False)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
