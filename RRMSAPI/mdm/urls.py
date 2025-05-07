from django.urls import path, include
from .views import  LookupByCategoryView,FileTypesViewSet, FileClassificationViewSet, CaseStatusViewSet, DivisionViewSet, RoleView,DistrictMasterView, StateMasterView, DesignationViewSet, UnitMasterView
from rest_framework.routers import SimpleRouter  

router = SimpleRouter(trailing_slash=False) 
# router.register(r'roles', RoleViewSet)
router.register(r'divisions', DivisionViewSet, basename = 'division')
router.register(r'designations', DesignationViewSet, basename = 'designation')
router.register(r'fileTypes', FileTypesViewSet, basename = 'file-type')
router.register(r'fileClassification', FileClassificationViewSet, basename = 'file-classification')
router.register(r'caseStatus', CaseStatusViewSet, basename = 'case-status')

urlpatterns = [
    path('', include(router.urls)),
    path('roles',RoleView.as_view(), name = 'roles'),
    path('districts/<int:stateId>', DistrictMasterView.as_view(), name='district-list'),
    path('states', StateMasterView.as_view(), name='state-list'),
    path('units/<int:districtId>', UnitMasterView.as_view(), name='unit-list'),
    path('lookup',LookupByCategoryView.as_view(),name = 'lookup')
]