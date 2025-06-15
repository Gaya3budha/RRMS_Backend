from mdm.models import Department, Division
from collections import defaultdict
from django.db.models import Q

def user_access_scope(user):
    
    designations = user.designation.all()

    allowed_divisions = Division.objects.filter(
        designation__in=designations
    ).values_list("divisionId", flat=True).distinct()

    allowed_departments = Department.objects.filter(
        Q(designation__in=designations) | Q(division__pk__in=allowed_divisions)
    ).values_list("departmentId", flat=True).distinct()

    return  list(allowed_departments), list(allowed_divisions)

def nested_dict(): return defaultdict(nested_dict)
