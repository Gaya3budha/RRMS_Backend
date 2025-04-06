from django.urls import path
from .views import CaseInfoFileUploadView, CaseInfoFilesSearchView, FilePreviewAPIView


urlpatterns = [
    path('save', CaseInfoFileUploadView.as_view(), name='case-data'),
    path('search', CaseInfoFilesSearchView.as_view(), name='search-case'),
    path('filePreview', FilePreviewAPIView.as_view(), name='file-preview'),
]