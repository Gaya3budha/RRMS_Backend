from django.urls import path
from .views import CaseInfoDetailsView,SearchCaseFilesView, FileApprovalDetailsViewSet,FilePreviewAPIView,NotificationListView, FavouriteFilesView,FavouriteFilesView,LatestUserFilesView


urlpatterns = [
    path('save', CaseInfoDetailsView.as_view(), name='case-data'),
    path('update/<int:pk>', CaseInfoDetailsView.as_view(), name='update-case-data'),
    path('search', SearchCaseFilesView.as_view(), name='search-case'),
    path('filePreview', FilePreviewAPIView.as_view(), name='file-preview'),
    path('files/<int:file_id>/favourite', FavouriteFilesView.as_view(), name='add-favourite'),
    path('files/<int:file_id>/unfavourite', FavouriteFilesView.as_view(), name='remove-favourite'),
    path('favourites', FavouriteFilesView.as_view(), name='user-favourites'),
    path('files/latest', LatestUserFilesView.as_view(), name='latest-user-files'),
    path('notifications',NotificationListView.as_view(),name='view-notifications'),
    path('approve-file/<int:pk>', FileApprovalDetailsViewSet.as_view(), name='approve-file'),
]