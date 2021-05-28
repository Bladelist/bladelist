
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from .views import IndexView, bot_view, LoginView, login_handler_view, logout_view, discord_login_view, AboutView

urlpatterns = [
    path('', IndexView.as_view(), name="home"),
    path('login/', LoginView.as_view()),
    path('login/handlers/', login_handler_view),
    path('bots', bot_view),
    url(r'^logout', logout_view, name="logout"),
    url(r'^about', AboutView.as_view(), name="about"),
    url(r'^discord/login/', discord_login_view, name="login")
]
