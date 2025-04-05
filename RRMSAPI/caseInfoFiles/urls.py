from django.urls import path
from .views import CaseInfoFileUploadView, CaseInfoFilesSearchView


urlpatterns = [
    path('save', CaseInfoFileUploadView.as_view(), name='case-data'),
    path('search', CaseInfoFilesSearchView.as_view(), name='search-case'),
]