
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from .views import IndexView, BotView, LoginView, login_handler_view, logout_view, discord_login_view, AboutView, TemplateView, BotListView, AddBotView, BotEditView, discord_login_normal, ProfileView, ProfileEditView


urlpatterns = [
    path('', IndexView.as_view(), name="home"),
    path('login/', LoginView.as_view()),
    path('login/handlers/', login_handler_view),
    url(r'^bots/(?P<bot_id>[0-9]{18})/edit/', BotEditView.as_view(), name="bot_edit"),
    url(r'^bots/(?P<bot_id>[0-9]{18})', BotView.as_view(), name="bot_single"),
    url(r'^bots/', BotListView.as_view(), name="bots"),
    url(r'^logout', logout_view, name="logout"),
    url(r'^add', AddBotView.as_view(), name="add"),
    url(r'^about', AboutView.as_view(), name="about"),
    url(r'^staff/panel/', AboutView.as_view(), name="staff_panel"),
    url(r'^profile/edit/', ProfileEditView.as_view(), name="edit_profile"),
    url(r'^users/(?P<user_id>[0-9]{18})', ProfileView.as_view(), name="profile"),
    url(r'^privacy', TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    url(r'^discord/login/', discord_login_view, name="login"),
    url(r'^accounts/login/', discord_login_normal, name="normal_login")
]
