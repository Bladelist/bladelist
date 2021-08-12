from django.urls import path
from .views import BotManageView, UserMigrateView

urlpatterns = [
    path('bot/<str:bot_id>/', BotManageView.as_view(), name='bot_manage'),
    path('migrate/user/', UserMigrateView.as_view(), name='migrate_user'),
    path('migrate/bot/', UserMigrateView.as_view(), name='migrate_user'),
]
