from datetime import datetime, timezone
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from utils.background import create_user, update_user
from utils.oauth import Oauth
from utils.hashing import Hasher

oauth = Oauth()
hasher = Hasher()


def index_view(request):
    return render(request, "index.html", {"search": True, "oauth": oauth})


def bot_view(request):
    return render(request, "bots.html")


class LoginView(View):

    template_name = 'index.html'
    verified = False
    context = {"Oauth": oauth}
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
        else:
            error = "Internal Server Error. Contact Administrator"
        return render(request, self.template_name, {"error": error, "search": True})


def login_handler_view(request):
    return render(request, "login_handler.html")


def logout_view(request):
    logout(request)
    return redirect('/')
