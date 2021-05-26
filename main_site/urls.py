
from django.contrib import admin
from django.urls import path
from .views import index_view

urlpatterns = [
    path('', index_view),
]
