from django.urls import path, include
from .views import  FileTypesViewSet, FileClassificationViewSet, CaseStatusViewSet, DivisionViewSet, DistrictMasterView, StateMasterView, DesignationViewSet, UnitMasterView
from rest_framework.routers import SimpleRouter  

router = SimpleRouter(trailing_slash=False) 
# router.register(r'roles', RoleViewSet)
router.register(r'divisions', DivisionViewSet)
router.register(r'designations', DesignationViewSet)
router.register(r'fileTypes', FileTypesViewSet)
router.register(r'fileClassification', FileClassificationViewSet)
router.register(r'caseStatus', CaseStatusViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('districts/<int:stateId>', DistrictMasterView.as_view(), name='district-list'),
    path('states', StateMasterView.as_view(), name='state-list'),
    path('units/<int:districtId>', UnitMasterView.as_view(), name='unit-list')
]