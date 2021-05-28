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
from django.views.generic.list import ListView

oauth = Oauth()
hasher = Hasher()


def login_handler_view(request):
    return render(request, "login_handler.html")


def logout_view(request):
    logout(request)
    return redirect('/')


def discord_login_view(request):
    return redirect(oauth.discord_login_url)


class BotView(View):
    template_name = "bot.html"
    model = Bot

    def get(self, request, bot_id):
        try:
            bot = self.model.objects.get(id=bot_id)
            if bot.banned or not bot.verified:
                if request.user.is_authenticated:
                    if request.user.member == bot.owner or request.user.is_staff:
                        return render(request, self.template_name, {"bot": bot})
                return render(request, "404.html")
            return render(request, self.template_name, {"bot": bot})
        except self.model.DoesNotExist:
            return render(request, "404.html", {"search": True})


class LoginView(View):

    template_name = 'index.html'
    user_json = None
    access_token = None

    def get(self, request):
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
        random_bots = Bot.objects.filter(verified=True, banned=False).order_by("id").distinct()[:8]
        bot_count = Bot.objects.count()
        recent_bots = Bot.objects.filter(verified=True, banned=False).order_by('-date_added')[:8]
        trending_bots = Bot.objects.filter(verified=True, banned=False).order_by('-votes')[:8]
        return render(request, self.template_name,
                      {"search": True,
                       "random_bots": random_bots,
                       "recent_bots": recent_bots,
                       "trending_bots": trending_bots,
                       "bot_count": bot_count})


class AboutView(View):
    def get(self, request):
        return render(request, "about.html")


class TemplateView(View):
    template_name = "404.html"

    def get(self, request):
        return render(request, self.template_name)


class BotListView(ListView):
    template_name = "bots.html"
    model = Bot
    paginate_by = 40

    def get_queryset(self):
        return self.model.objects.filter(verified=True, banned=False).order_by('-votes')


class AddBotView(LoginRequiredMixin, View):
    template_name = "add.html"

    def get(self, request):
        return render(request, self.template_name)