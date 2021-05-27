
from django.contrib import admin
from django.urls import path
from .views import index_view, bot_view, LoginView, login_handler_view, logout_view

urlpatterns = [
    path('', index_view),
    path('login/', LoginView.as_view()),
    path('login/handlers/', login_handler_view),
    path('bots', bot_view),
    path('logout', logout_view),
]
