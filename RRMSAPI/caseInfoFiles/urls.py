from django.urls import path
from .views import CaseInfoDetailsView,SearchCaseFilesView, FilePreviewAPIView


urlpatterns = [
    path('save', CaseInfoDetailsView.as_view(), name='case-data'),
    path('search', SearchCaseFilesView.as_view(), name='search-case'),
    path('filePreview', FilePreviewAPIView.as_view(), name='file-preview'),
]