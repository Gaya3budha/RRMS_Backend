from django.urls import path
from .views import CreateUserView,UserListView,UpdateUserView,UserDivisionRoleCreateAPIView,CustomTokenObtainPairView,GetDivisionrAdminsView, GetLoggedInUsersView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('',UserListView.as_view(),name='user-list'), #path for fetching all the users
    path('create', CreateUserView.as_view(), name='create_user'),
    path('update-user/<int:kgid_user>', UpdateUserView.as_view(), name='update_user'),
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('currentUsers',GetLoggedInUsersView.as_view(), name = 'logged-in-users'),
    path('getcmoradmins/<int:role_id>', GetDivisionrAdminsView.as_view(),name = 'cm-admins'),
    path('adddivision',UserDivisionRoleCreateAPIView.as_view(), name = 'update-divisions')
]