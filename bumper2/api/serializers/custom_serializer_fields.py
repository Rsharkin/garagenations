__author__ = 'anuj'
from rest_framework import serializers
from userSerializer import FollowupResultSerializer

class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        return getattr(self._choices, data)


class DictSerializerMethodField(serializers.DictField):
    """
    A read-only field that get its representation from calling a method on the
    parent serializer class. The method called will be of the form
    "get_{field_name}", and should take a single argument, which is the
    object being serialized.

    For example:

    class ExampleSerializer(self):
        extra_info = SerializerMethodField()

        def get_extra_info(self, obj):
            return ...  # Calculate some data to return.
    """
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super(DictSerializerMethodField, self).__init__(**kwargs)

    def bind(self, field_name, parent):
        # In order to enforce a consistent style, we error if a redundant
        # 'method_name' argument has been used. For example:
        # my_field = serializer.CharField(source='my_field')
        default_method_name = 'get_{field_name}'.format(field_name=field_name)
        assert self.method_name != default_method_name, (
            "It is redundant to specify `%s` on SerializerMethodField '%s' in "
            "serializer '%s', because it is the same as the default method name. "
            "Remove the `method_name` argument." %
            (self.method_name, field_name, parent.__class__.__name__)
        )

        # The method name should default to `get_{field_name}`.
        if self.method_name is None:
            self.method_name = default_method_name

        super(DictSerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        result = method(value)
        return super(DictSerializerMethodField, self).to_representation(result)


class CreateListModelMixin(object):

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(CreateListModelMixin, self).get_serializer(*args, **kwargs)


class ObjectUserValidator(object):
    """
    Validator that corresponds to `unique=True` on a model field.

    Should be applied to an individual field on the serializer.
    """
    def __init__(self, obj_field, obj_field_name):
        self.obj_field = obj_field
        self.obj_field_name = obj_field_name

    def set_context(self, serializer):
        # Determine if this is an update or a create operation.
        # In `__call__` we can then use that information to modify the validation behavior.
        request = serializer.context['request']
        self.user = request.user
        # self.instance = getattr(serializer, 'instance', None)

    def __call__(self, value):
        obj = value.get(self.obj_field)
        if not (self.user.groups.filter(name='OpsUser').exists() or obj.user == self.user):
            raise serializers.ValidationError('{} does not belong to user'.format(self.obj_field_name))
