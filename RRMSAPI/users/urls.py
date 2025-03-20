from django.urls import path
from .views import CreateUserView,UserListView,UpdateUserView

urlpatterns = [
    path('',UserListView.as_view(),name='user-list'), #path for fetching all the users
    path('create/', CreateUserView.as_view(), name='create_user'),
    path('update-user/<int:kgid_user>/', UpdateUserView.as_view(), name='update_user')

]