from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import FolderTreeAPIView,MoveFilesAPIView,ArchiveFileAPIView,MergeStudentAPIView,UnArchiveFileAPIView,FolderTreeFullAPIView,CopyFilesAPIView,ArchiveFullTreeAPIView

urlpatterns = [
path('folder-tree', FolderTreeAPIView.as_view()),
path('move-files', MoveFilesAPIView.as_view()),
path('archive-files', ArchiveFileAPIView.as_view()),
path('folder-tree-view',FolderTreeFullAPIView.as_view()),
path('copy-files',CopyFilesAPIView.as_view()),
path('archive',ArchiveFullTreeAPIView.as_view()),
path('unarchive',UnArchiveFileAPIView.as_view()),
path('merge',MergeStudentAPIView.as_view())
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)