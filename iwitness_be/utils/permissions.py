from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to allow access to owners or staff only.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Allow access if the user is a staff member
            return request.user.is_staff
        return False

    def has_object_permission(self, request, view, obj):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Allow access if the user is a staff member
            if request.user.is_staff:
                return True
            # Allow access if the user is the owner of the object
            return obj.user == request.user
        return False
