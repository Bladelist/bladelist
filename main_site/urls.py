
from django.contrib import admin
from django.urls import path
from .views import index_view, bot_view

urlpatterns = [
    path('', index_view),
    path('bots', bot_view)
]
