from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.exc_handler import ConflictError
from core.models.common import Address, Media
from core.managers import bookingManager


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('__all__')

    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        super(AddressSerializer, self).__init__(*args, **kwargs)

        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        new_fields = kwargs.pop('new_fields', None)
        change_serializer = kwargs.pop('change_serializer', None)
        if change_serializer:
            for key,value in change_serializer.iteritems():
                self.fields[key] = value
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if remove_fields:
            # for multiple fields in a list
            for field_name in remove_fields:
                self.fields.pop(field_name)
        elif new_fields:
            existing = set(self.fields.keys())
            allowed = set(new_fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ConflictAwareModelSerializer(DynamicFieldsModelSerializer):
    conflict = False

    def run_validators(self, value):
        """
        Test the given value against all the validators on the field,
        and either raise a `ValidationError` or simply return.
        """
        errors = []
        for validator in self.validators:
            if hasattr(validator, 'set_context'):
                validator.set_context(self)

            try:
                validator(value)
            except serializers.ValidationError as exc:
                # If the validation error contains a mapping of fields to
                # errors then simply raise it immediately rather than
                # attempting to accumulate a list of errors.
                if isinstance(exc.detail, dict):
                    raise
                if isinstance(validator, UniqueTogetherValidator):
                    self.conflict = True
                errors.extend(exc.detail)
            except serializers.DjangoValidationError as exc:
                errors.extend(exc.messages)
        if errors:
            raise serializers.ValidationError(errors)

    def is_valid(self, raise_exception=False):
        assert not hasattr(self, 'restore_object'), (
            'Serializer `%s.%s` has old-style version 2 `.restore_object()` '
            'that is no longer compatible with REST framework 3. '
            'Use the new-style `.create()` and `.update()` methods instead.' %
            (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )

        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except serializers.ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            if self.conflict:
                raise ConflictError(self.errors)
            raise serializers.ValidationError(self.errors)

        return not bool(self._errors)


class MediaSerializer(DynamicFieldsModelSerializer):
    image_name = serializers.CharField(required=True, write_only=True)
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('__all__')
        extra_kwargs = {'file': {'required': False}}

    def get_media_url(self, obj):
        request = self.context['request']
        return bookingManager.get_media_url(request, obj)
