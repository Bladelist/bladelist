import random
from datetime import datetime, timezone
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from utils.background import create_user, update_user
from utils.oauth import Oauth
from utils.hashing import Hasher
from .models import Bot

oauth = Oauth()
hasher = Hasher()


def bot_view(request):
    return render(request, "bots.html")


class LoginView(View):

    template_name = 'index.html'
    user_json = None
    access_token = None

    def get(self, request):
        user = None
        error = None
        code = request.GET.get('code')
        if code is not None:
            self.access_token = oauth.get_access_token(code)
            self.user_json = oauth.get_user_json(self.access_token)
            user_id = self.user_json.get("id")
            user = authenticate(username=user_id, password=hasher.get_hashed_pass(user_id))
            if user is None:
                user = create_user(self.user_json)
            else:
                update_user(user, self.user_json)
            if not user.member.banned:
                login(request, user)
            else:
                error = "Your are banned from accessing the site."
                return render(request, self.template_name, {"error": error, "search": True})
        else:
            error = "Internal Server Error"
            return render(request, self.template_name, {"error": error, "search": True})
        return IndexView.as_view()(self.request)


class IndexView(View):
    template_name = "index.html"

    def get(self, request):
        random_bots = Bot.objects.order_by("?").distinct()[:8]
        bot_count = Bot.objects.count()
        recent_bots = Bot.objects.order_by('-date_added')[:8]
        trending_bots = Bot.objects.order_by('-votes')[:8]
        return render(request, self.template_name,
                      {"search": True,
                       "random_bots": random_bots,
                       "recent_bots": recent_bots,
                       "trending_bots": trending_bots,
                       "oauth": oauth,
                       "bot_count": bot_count})


def login_handler_view(request):
    return render(request, "login_handler.html")


def logout_view(request):
    logout(request)
    return redirect('/')


def discord_login_view(request):
    return redirect(oauth.discord_login_url)


class AboutView(View):
    def get(self, request):
        return render(request, "about.html")