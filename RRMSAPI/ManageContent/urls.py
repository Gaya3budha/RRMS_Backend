from django.urls import path
from django.contrib import admin
from .views import FolderTreeAPIView

urlpatterns = [
path('folder-tree', FolderTreeAPIView.as_view())
]