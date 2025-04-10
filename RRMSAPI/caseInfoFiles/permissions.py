from rest_framework.permissions import BasePermission

class HasCustomPermission(BasePermission):
    def has_permission(self, request, view):
        required_permission = getattr(view, 'required_permission', None)
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not hasattr(user, 'role') or not user.role:
            return False

        if not required_permission:
            return True 

        return user.role.permissions.filter(codename=required_permission).exists()
