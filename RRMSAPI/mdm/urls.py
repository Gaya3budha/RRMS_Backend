from django.urls import path
from .views import RolesListView, DivisionListView, DistrictListView, StateListView

urlpatterns = [
    path('roles/', RolesListView.as_view(), name='roles-list'),
    path('divisions/', DivisionListView.as_view(), name='division-list'),
    path('districts/', DistrictListView.as_view(), name='district-list'),
    path('states/', StateListView.as_view(), name='state-list')
]