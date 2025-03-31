from django.urls import path
from .views import RoleView, DivisionMasterView, DistrictMasterView, StateMasterView, DesignationMasterView, UnitMasterView

urlpatterns = [
    path('roles', RoleView.as_view(), name='roles-list'),
    path('divisions', DivisionMasterView.as_view(), name='division-list'),
    path('districts/<int:stateId>', DistrictMasterView.as_view(), name='district-list'),
    path('states', StateMasterView.as_view(), name='state-list'),
    path('designations', DesignationMasterView.as_view(), name='designation-list'),
    path('units/<int:districtId>', UnitMasterView.as_view(), name='unit-list')
]