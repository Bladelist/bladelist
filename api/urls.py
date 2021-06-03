from django.urls import path
from .views import BotManageView

urlpatterns = [
    path('bot/<str:bot_id>/', BotManageView.as_view(), name='bot_manage'),
]
