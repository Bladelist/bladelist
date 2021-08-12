from django.urls import path
from .views import BotManageView, UserMigrateView, BotMigrateView, BotStatusEditView

urlpatterns = [
    path('bot/<str:bot_id>/', BotManageView.as_view(), name='bot_manage'),
    path('migrate/user/', UserMigrateView.as_view(), name='migrate_user'),
    path('migrate/bot/', BotMigrateView.as_view(), name='migrate_bot'),
    path('bot/status/<int:bot_id>/', BotStatusEditView.as_view(), name='bot_status'),
]
