from rest_framework.permissions import BasePermission
from django.core.exceptions import ObjectDoesNotExist
from .models import Role
# from users.models import UserDivisionRole
from rest_framework import permissions

class IsSuperAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow POST, PUT, DELETE only for superusers
        return request.user and request.user.is_authenticated and request.user.is_superuser
    
class HasRequiredPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # division_id = (request.data.get('division_id') or request.query_params.get('division_id'))

        # if not division_id:
        #     return False
        
        # try:
        #     user_division_role = UserDivisionRole.objects.get(
        #         user=request.user,
        #         division_id=division_id
        #     )
        # except UserDivisionRole.DoesNotExist:
        #     return False
        
        role = request.user.role

        # if not role:
        #     return False

        user_permissions = {perm.codename for perm in role.permissions.all()}
        required_permission = self.get_required_permission(request, view)

        if not required_permission:
            return True 
        
        if required_permission in user_permissions:
            return True
        else:
            return False


    def get_required_permission(self, request, view):
        method_permission_map = {
            "GET": "view",
            "POST": "add",
            "PUT": "change",
            "PATCH": "change",
            "DELETE": "delete"
        }

        model_name = self.get_model_name(view)

        if not model_name:
            return None

        # Determine permission prefix based on HTTP method
        action_prefix = method_permission_map.get(request.method, "view")

        # Construct the required permission
        return f"{action_prefix}_{model_name}"

    def get_model_name(self, view):
        """
        Dynamically fetches the model name from:
        1. The queryset model (if available)
        2. The serializer’s Meta model (if available)
        3. The view name as a fallback
        """

        # Try to get model name from queryset
        if hasattr(view, "queryset") and view.queryset is not None:
            return view.queryset.model._meta.model_name

        # Try to get model name from serializer class
        if hasattr(view, "serializer_class") and hasattr(view.serializer_class.Meta, "model"):
            return view.serializer_class.Meta.model._meta.model_name

        view_name = view.__class__.__name__.lower()
        if view_name.endswith("view"):
            view_name = view_name[:-4]  # Remove 'view' suffix

        return view_name