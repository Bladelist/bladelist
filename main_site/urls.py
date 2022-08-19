from django.urls import path, re_path
from .views import (IndexView, LoginView, ServerModerationView, BotAddView, support_server_invite,
                    ProfileEditView, StaffView, BotSearchView, ServerView, ServerListView, BotView,
                    ServerAddView, ServerEditView, ServerSearchView, ServerIndexView, BotModerationView,
                    TemplateView, BotListView, BotEditView, ProfileView, discord_login_view, logout_view,
                    bot_invite_counter, server_invite_counter, server_refresh, login_handler_view, discord_login_normal)


urlpatterns = [
    path('login/', LoginView.as_view()),
    path('join/', support_server_invite, name="join_support_server"),
    path('login/handlers/', login_handler_view, name="login_handler"),
    re_path(r'^logout', logout_view, name="logout"),

    re_path(r'^bots/(?P<bot_id>[0-9]{18,19})/invite/', bot_invite_counter, name="bot_invite"),
    re_path(r'^bots/(?P<bot_id>[0-9]{18,19})/edit/', BotEditView.as_view(), name="bot_edit_view"),
    re_path(r'^bots/(?P<bot_id>[0-9]{18,19})', BotView.as_view(), name="bot_single"),
    re_path(r'^bots/requirements/', TemplateView.as_view(template_name="requirements.html"), name="bot_search"),
    re_path(r'^bots/search/', BotSearchView.as_view(), name="bot_search"),
    re_path(r'^bots/edit/', BotEditView.as_view(), name="bot_edit"),
    re_path(r'^bots/add', BotAddView.as_view(), name="bot_add"),
    re_path(r'^bots', BotListView.as_view(), name="bots"),

    re_path(r'^servers/(?P<server_id>[0-9]{18,19})/invite/', server_invite_counter, name="server_invite"),
    re_path(r'^servers/(?P<server_id>[0-9]{18,19})/edit/', ServerEditView.as_view(), name="server_edit_view"),
    re_path(r'^servers/edit/', ServerEditView.as_view(), name="server_edit"),
    re_path(r'^servers/(?P<server_id>[0-9]{18,19})', ServerView.as_view(), name="server_single"),
    re_path(r'^servers/search/', ServerSearchView.as_view(), name="server_search"),
    re_path(r'^servers/add/', ServerAddView.as_view(), name="server_add"),
    re_path(r'^servers/refresh/', server_refresh, name="server_refresh"),
    re_path(r'^servers/list/', ServerListView.as_view(), name="server_list"),
    re_path(r'^servers', ServerIndexView.as_view(), name="servers"),

    re_path(r'^about', TemplateView.as_view(template_name="about.html"), name="about"),
    re_path(r'^staff/bots/', BotModerationView.as_view(), name="bot_moderation"),
    re_path(r'^staff/servers/', ServerModerationView.as_view(), name="server_moderation"),
    re_path(r'^staff/', StaffView.as_view(), name="staff_panel"),
    re_path(r'^privacy', TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    re_path(r'^terms', TemplateView.as_view(template_name="terms.html"), name="terms"),

    re_path(r'^discord/login/', discord_login_view, name="login"),
    re_path(r'^accounts/login/', discord_login_normal, name="normal_login"),

    re_path(r'^profile/edit/', ProfileEditView.as_view(), name="edit_profile"),
    re_path(r'^users/(?P<user_id>[0-9]{18,19})', ProfileView.as_view(), name="profile"),

    path('', IndexView.as_view(), name="home"),
]
