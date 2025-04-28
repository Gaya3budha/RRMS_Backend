from rest_framework.permissions import BasePermission
from users.models import UserDivisionRole
class HasCustomPermission(BasePermission):
    def has_permission(self, request, view):
        required_permission = getattr(view, 'required_permission', None)
        print("HasCustomPermission",required_permission)
        
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # if not hasattr(user, 'role') or not user.role:
        #     return False

        if not required_permission:
            return True 
        
        division_id = (request.data.get('division_id') or request.query_params.get('division_id'))

        divsions_roles=UserDivisionRole.objects.get(user = user,division_id=division_id)
        print("divsions_roles",divsions_roles)
        return divsions_roles.role.permissions.filter(codename=required_permission).exists()

class FileDetailsPermission(BasePermission):
    def has_object_permission(self,request,view,obj):
        if request.user.role_id == 4:
            return True
        if obj.is_approved:
            return True
        
        return obj.uploaded_by == request.user