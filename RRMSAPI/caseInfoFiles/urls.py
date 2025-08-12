from django.urls import path
from django.contrib import admin
from .views import CaseInfoDetailsView, SaveCaseTransferView,SearchCaseFilesView,CaseInfoDraftDetailsView,CaseFileUploadView,SubmitDraftAPIView,FileDetailsView,UploadApprovalDetailView,WithdrawAccessApprovalView,SendAccessApprovalReminder,SendUploadApprovalReminder,WithdrawUploadApprovalView,MarkNotificationAsReadAPIView,UploadApprovalListView,RevokeFileAccessRequestAPIView, FileApprovalDetailsViewSet,FilePreviewAPIView,FileAccessRequestListAPIView,ApproveorDenyConfidentialAPIView,NotificationListView, FavouriteFilesView,FavouriteFilesView,LatestUserFilesView

admin.site.site_header = "RRMS Super Admin Portal"
admin.site.site_title = "RRMS"
admin.site.index_title = "Master Data Dashboard"

urlpatterns = [
    path('saveDraft', CaseInfoDetailsView.as_view(), name='case-data-draft'),
    path('drafts/<int:divisionId>',CaseInfoDraftDetailsView.as_view(),name='case-drafts'),
    path('submit', SubmitDraftAPIView.as_view(), name='submit-case-draft'),
    path('<int:casedetailsId>/upload',CaseFileUploadView.as_view(),name='file-upload'),
    path('update/<int:pk>', CaseInfoDetailsView.as_view(), name='update-case-data'),
    path('search', SearchCaseFilesView.as_view(), name='search-case'),
    path('updateFileData/<int:pk>',FileDetailsView.as_view(),name='update-file-data'),
    path('filePreview', FilePreviewAPIView.as_view(), name='file-preview'),
    path('files/<int:file_id>/favourite', FavouriteFilesView.as_view(), name='add-favourite'),
    path('files/<int:file_id>/unfavourite', FavouriteFilesView.as_view(), name='remove-favourite'),
    path('favourites', FavouriteFilesView.as_view(), name='user-favourites'),
    path('files/latest', LatestUserFilesView.as_view(), name='latest-user-files'),
    path('notifications',NotificationListView.as_view(),name='view-notifications'),
    path('upload-approvals',UploadApprovalListView.as_view(),name='upload-approvals'),
    path('upload-approvals/<int:id>',UploadApprovalDetailView.as_view(),name='upload-approval-detail-view'),
    path('upload-approval/<int:approval_id>/send-reminder',SendUploadApprovalReminder.as_view(),name='send-upload-approvals'),
    path('withdraw-upload-approval/<int:approval_id>',WithdrawUploadApprovalView.as_view(),name='withdraw-approval'),
    path('approve-file', FileApprovalDetailsViewSet.as_view(), name='approve-file'),
    path('access/<int:pk>/action', ApproveorDenyConfidentialAPIView.as_view(), name='access-request-action'),
    path('requests',FileAccessRequestListAPIView.as_view(),name='get-all-file-access-request'),
    path('requests/<int:access_id>/send-reminder',SendAccessApprovalReminder.as_view(),name='send-reminder-access-request'),
    path('withdraw-access-requests/<int:access_id>',WithdrawAccessApprovalView.as_view(),name='withdraw-access-request'),
    path('revoke',RevokeFileAccessRequestAPIView.as_view(),name='revoke-access'),
    path('markasread',MarkNotificationAsReadAPIView.as_view(),name='mark-as-read'),
    path('case-transfer',SaveCaseTransferView.as_view(),name='case-transfer')
]