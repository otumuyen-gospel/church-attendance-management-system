from rest_framework.permissions import BasePermission

class IsInGroup(BasePermission):
    """
    Custom permission to check if the user is in a specific group.
    """
    def has_permission(self, request, view):
         # Define the required group name(s) for the view
        required_groups = getattr(view, 'required_groups', None)

        if required_groups is None:
                # No specific group required for this view, allow access
                return True

        if request.user and request.user.is_authenticated:
                return any(request.user.groups.filter(name=group_name).exists() for group_name in required_groups)
        return False