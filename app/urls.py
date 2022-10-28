from django.urls import path
from .views import UserViewList

urlpatterns = [
    path("", UserViewList.as_view(), name="user-list")
]

app_name = 'app'
