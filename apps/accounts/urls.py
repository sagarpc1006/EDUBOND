from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import connect, login, people_list, profile, register, send_otp

urlpatterns = [
    path("send-otp/", send_otp, name="send_otp"),
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", profile, name="profile"),
    path("people/", people_list, name="people_list"),
    path("connect/<int:user_id>/", connect, name="connect"),
]
