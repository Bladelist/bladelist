from django.urls import path
from .views import BotManageView, ServerManageView, BotAllView
from .private_views import BotStatusEditView, ServerStatusEditView

urlpatterns = [
    path('bots/<str:bot_id>/', BotManageView.as_view(), name='bot_manage_alt'),
    path('bots/<str:bot_id>', BotManageView.as_view(), name='bot_manage'),
    path('bot/status/<int:bot_id>/', BotStatusEditView.as_view(), name='bot_status'),
    path('bots/', BotManageView.as_view(), name='bot_manage_dev'),
    path('bots/all/', BotAllView.as_view(), name='bot_manage_dev_all'),
    path('server/<str:server_id>/', ServerManageView.as_view(), name='server_view_alt'),
    path('server/<str:server_id>', ServerManageView.as_view(), name='server_view'),
    path('server/status/<int:server_id>/', ServerStatusEditView.as_view(), name='server_status'),
    # path('migrate/user/', UserMigrateView.as_view(), name='migrate_user'),
    # path('migrate/bot/', BotMigrateView.as_view(), name='migrate_bot'),
]
