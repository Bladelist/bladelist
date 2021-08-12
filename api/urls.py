from django.urls import path
from .views import BotManageView, UserMigrateView, BotMigrateView

urlpatterns = [
    path('bot/<str:bot_id>/', BotManageView.as_view(), name='bot_manage'),
    path('migrate/user/', UserMigrateView.as_view(), name='migrate_user'),
    path('migrate/bot/', BotMigrateView.as_view(), name='migrate_bot'),
]
