from django.urls import path
from .views import RolesListView, DivisionListView, DistrictListView, StateListView, DesignationListView, UnitListView

urlpatterns = [
    path('roles/', RolesListView.as_view(), name='roles-list'),
    path('divisions/', DivisionListView.as_view(), name='division-list'),
    path('districts/<int:stateId>', DistrictListView.as_view(), name='district-list'),
    path('states/', StateListView.as_view(), name='state-list'),
    path('designations/', DesignationListView.as_view(), name='designation-list'),
    path('units/<int:districtId>', UnitListView.as_view(), name='unit-list')
]