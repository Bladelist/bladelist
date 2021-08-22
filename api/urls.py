from django.urls import path
from .views import BotManageView, UserMigrateView, BotMigrateView, BotStatusEditView, ServerView

urlpatterns = [
    path('bot/<str:bot_id>/', BotManageView.as_view(), name='bot_manage'),
    path('bot/status/<int:bot_id>/', BotStatusEditView.as_view(), name='bot_status'),
    path('bots/', BotManageView.as_view(), name='bot_manage_dev'),
    path('server/<str:server_id>/', ServerView.as_view(), name='server_view'),
    path('migrate/user/', UserMigrateView.as_view(), name='migrate_user'),
    path('migrate/bot/', BotMigrateView.as_view(), name='migrate_bot'),
]
