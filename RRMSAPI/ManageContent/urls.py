from django.urls import path
from .views import FolderTreeAPIView,MoveFilesAPIView

urlpatterns = [
path('folder-tree', FolderTreeAPIView.as_view()),
path('move-files', MoveFilesAPIView.as_view())
]