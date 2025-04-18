from django.urls import path
from .views import CaseInfoDetailsView,SearchCaseFilesView, FilePreviewAPIView, FavouriteFilesView,FavouriteFilesView,LatestUserFilesView


urlpatterns = [
    path('save', CaseInfoDetailsView.as_view(), name='case-data'),
    path('update/<int:pk>', CaseInfoDetailsView.as_view(), name='update-case-data'),
    path('search', SearchCaseFilesView.as_view(), name='search-case'),
    path('filePreview', FilePreviewAPIView.as_view(), name='file-preview'),
    path('files/<int:file_id>/favourite', FavouriteFilesView.as_view(), name='add-favourite'),
    path('files/<int:file_id>/unfavourite', FavouriteFilesView.as_view(), name='remove-favourite'),
    path('favourites', FavouriteFilesView.as_view(), name='user-favourites'),
    path('files/latest', LatestUserFilesView.as_view(), name='latest-user-files'),
]