from django.urls import path
from .views import CreateUserView,UserListView

urlpatterns = [
    path('users/',UserListView.as_view(),name='user-list'), #path for fetching all the users
    path('users/create/', CreateUserView.as_view(), name='create_user')
]