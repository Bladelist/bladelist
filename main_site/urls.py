from django.urls import path
from django.conf.urls import url
from .views import (IndexView, BotView, LoginView, login_handler_view, discord_login_normal,
                    logout_view, discord_login_view, server_refresh, AboutView, ServerModerationView,
                    TemplateView, BotListView, BotAddView, BotEditView, ProfileView,
                    ProfileEditView, StaffView, BotSearchView, ServerView, ServerListView,
                    ServerAddView, ServerEditView, ServerSearchView, ServerIndexView, BotModerationView)


urlpatterns = [
    path('login/', LoginView.as_view()),
    path('login/handlers/', login_handler_view),
    url(r'^logout', logout_view, name="logout"),

    url(r'^bots/(?P<bot_id>[0-9]{18})/edit/', BotEditView.as_view(), name="bot_edit_view"),
    url(r'^bots/(?P<bot_id>[0-9]{18})', BotView.as_view(), name="bot_single"),
    url(r'^bots/search/', BotSearchView.as_view(), name="bot_search"),
    url(r'^bots/edit/', BotEditView.as_view(), name="bot_edit"),
    url(r'^bots/add', BotAddView.as_view(), name="bot_add"),
    url(r'^bots', BotListView.as_view(), name="bots"),

    url(r'^servers/(?P<server_id>[0-9]{18})/edit/', ServerEditView.as_view(), name="server_edit_view"),
    url(r'^servers/edit/', ServerEditView.as_view(), name="server_edit"),
    url(r'^servers/(?P<server_id>[0-9]{18})', ServerView.as_view(), name="server_single"),
    url(r'^servers/search/', ServerSearchView.as_view(), name="server_search"),
    url(r'^servers/add/', ServerAddView.as_view(), name="server_add"),
    url(r'^servers/refresh/', server_refresh, name="server_refresh"),
    url(r'^servers/list/', ServerListView.as_view(), name="server_list"),
    url(r'^servers', ServerIndexView.as_view(), name="servers"),

    url(r'^about', AboutView.as_view(), name="about"),
    url(r'^staff/bots/', BotModerationView.as_view(), name="bot_moderation"),
    url(r'^staff/servers/', ServerModerationView.as_view(), name="server_moderation"),
    url(r'^staff/', StaffView.as_view(), name="staff_panel"),
    url(r'^privacy', TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    url(r'^terms', TemplateView.as_view(template_name="terms.html"), name="terms"),

    url(r'^discord/login/', discord_login_view, name="login"),
    url(r'^accounts/login/', discord_login_normal, name="normal_login"),

    url(r'^profile/edit/', ProfileEditView.as_view(), name="edit_profile"),
    url(r'^users/(?P<user_id>[0-9]{18})', ProfileView.as_view(), name="profile"),

    path('', IndexView.as_view(), name="home"),
]
