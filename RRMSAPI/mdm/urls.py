from django.urls import path, include
from .views import  FinalReportCaseStatusViewSet, LookupByCategoryView,FileClassificationViewSet,EmailViewSet,SMTPViewSet,CorrespondenceFilesViewSet,CaseFilesViewSet,FileTypesViewSet,DepartmentViewSet, DesignationHierarchyViewSet,CaseStatusViewSet,RoleView,DivisionViewSet,DistrictMasterView, StateMasterView, UnitMasterView, DesignationViewSet
from rest_framework.routers import SimpleRouter  

router = SimpleRouter(trailing_slash=False) 
# router.register(r'roles', RoleViewSet)
# router.register(r'divisions', DivisionViewSet, basename = 'division')
router.register(r'departments', DepartmentViewSet, basename = 'departments')
router.register(r'divisions', DivisionViewSet, basename = 'division')
router.register(r'designations', DesignationViewSet, basename = 'designation')
router.register(r'designation-hierarchy',DesignationHierarchyViewSet,basename='desg-hierarchy')
router.register(r'caseStatus', CaseStatusViewSet, basename = 'case-status')
router.register(r'finalreport-caseStatus', FinalReportCaseStatusViewSet, basename = 'final-case-status')
router.register(r'fileClassification', FileClassificationViewSet, basename = 'file-classification')
router.register(r'fileTypes', FileTypesViewSet, basename = 'file-type')
router.register(r'caseFiles', CaseFilesViewSet, basename = 'case-files')
router.register(r'correspondenceFiles', CorrespondenceFilesViewSet, basename = 'corrs-files')
router.register(r'smtp', SMTPViewSet, basename = 'smtp')
router.register(r'domain',EmailViewSet,basename='domain')




urlpatterns = [
    path('', include(router.urls)),
    path('roles',RoleView.as_view(), name = 'roles'),
    path('districts/<int:stateId>', DistrictMasterView.as_view(), name='district-list'),
    path('states', StateMasterView.as_view(), name='state-list'),
    path('units/<int:districtId>', UnitMasterView.as_view(), name='unit-list'),
    path('lookup',LookupByCategoryView.as_view(),name = 'lookup')
]