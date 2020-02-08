from rest_framework import permissions
from django.contrib.auth.models import Group


def is_in_group(user, group_name):
    """
        returns true if the user is in that group.
    """
    return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()


class HasGroupPermission(permissions.BasePermission):
    """
        Ensure user is in required groups.
    """

    def has_permission(self, request, view):
        # Get a mapping of methods -> required group.
        # to be provided in view definition
        required_groups_mapping = getattr(view, 'required_groups', {})

        # Determine the required groups for this particular request method.
        # view should have mapping like 'POST': ['admin'],
        required_groups = required_groups_mapping.get(request.method, [])

        # Return True if the user has any of the required groups.
        return any([is_in_group(request.user, group_name) for group_name in required_groups])


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsOwnerAndIsAuthenticated(permissions.BasePermission):
    """
        Allows access only to authenticated user and user is also the owner.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj == request.user


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.user == request.user


class UserIsOwnerOrAdminOrPost(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST']:
            return True
        return request.user and request.user.is_authenticated()

    def check_object_permission(self, user, obj):
        return (user and user.is_authenticated() and
          (user.groups.filter(name='OpsUser').exists() or obj == user))

    def has_object_permission(self, request, view, obj):
        if request.method in ['POST']:
            return True
        return self.check_object_permission(request.user, obj)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def check_object_permission(self, user, obj):
        return (user and user.is_authenticated() and
          (user.groups.filter(name='OpsUser').exists() or obj.user == user))

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)


class BookingIsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def check_object_permission(self, user, obj):
        return (user and user.is_authenticated() and
          (user.groups.filter(name='OpsUser').exists() or obj.booking.user == user))

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)


class BookingPackageIsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def check_object_permission(self, request, obj):
        user = request.user
        return (user and user.is_authenticated() and
          (user.groups.filter(name='OpsUser').exists() or obj.booking_package.booking.user == user))
            # if request.method in ['PATCH','PUT']:
            #     return obj.panel.editable
            # else:
            #     return True

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request, obj)


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return is_in_group(request.user, 'OpsUser')


class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def check_object_permission(self, user, obj):
        return (user and user.is_authenticated() and
                user.groups.filter(name='Driver').exists() and
                (obj.pickup_driver == user or obj.drop_driver == user))

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)


class IsBookingDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def check_object_permission(self, user, obj):
        return (user and user.is_authenticated() and
                user.groups.filter(name='Driver').exists() and
                (obj.booking.pickup_driver == user or obj.booking.drop_driver == user))

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)


class MessageUserIsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def check_object_permission(self, user, obj):
        return (user and user.is_authenticated() and
          (user.groups.filter(name='OpsUser').exists() or obj.user_message.filter(user=user).count()>0))

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)


class IsPostOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST']:
            return True
        return request.user and request.user.is_authenticated()

    def check_object_permission(self, user):
        return (user and user.is_authenticated() and
          user.groups.filter(name='OpsUser').exists())

    def has_object_permission(self, request, view, obj):
        if request.method in ['POST']:
            return True
        return self.check_object_permission(request.user)


class IsWorkshopExecutive(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated() and request.user.groups.filter(
                                                  name__in=['WorkshopExecutive',
                                                            'WorkshopAssistantManager',
                                                            'WorkshopManager']).exists()


class IsScratchFinder(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated() and request.user.groups.filter(
                                                                                name='ScratchFinder').exists()


class PermissionOneOf(permissions.BasePermission):
    def has_permission(self, request, view):
        permissions_list = getattr(view, 'permissions_list', [])
        for permission in permissions_list:
            if permission().has_permission(request, view):
                return True
        return False
