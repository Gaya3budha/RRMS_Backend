from django.urls import path
from .views import CaseInfoFileUploadView


urlpatterns = [
    path('save/', CaseInfoFileUploadView.as_view(), name='case-data'),
]