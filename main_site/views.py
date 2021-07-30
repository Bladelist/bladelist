from datetime import datetime, timezone
from django.http import QueryDict, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate
from utils.background import create_user, update_user
from utils.oauth import Oauth
from utils.hashing import Hasher
from utils.mixins import ResponseMixin
from .models import Bot, BotTag, Member, BotVote, BotReport, Server, ServerTag, ServerReport, ServerVote
from django.views.generic.list import ListView
from utils.api_client import DiscordAPIClient
from django.conf import settings
from django.db.models import Q
popup_oauth = Oauth()
normal_oauth = Oauth(redirect_uri=settings.AUTH_HANDLER_URL)
hasher = Hasher()
discord_client = DiscordAPIClient()
BOT_TAGS = BotTag.objects.all()
SERVER_TAGS = ServerTag.objects.all()
RANDOM_BOTS = Bot.objects.filter(verified=True, banned=False, owner__banned=False).order_by("id").distinct()[:8]


def login_handler_view(request):
    return render(request, "login_handler.html", {"handler_url": settings.AUTH_HANDLER_URL})


def discord_login_normal(request):
    return redirect(normal_oauth.discord_login_url)


def logout_view(request):
    logout(request)
    return redirect('/')


def discord_login_view(request):
    return redirect(popup_oauth.discord_login_url)


def server_refresh(request):
    admin_guilds = [
        (guild.get("id"), guild.get("name")) for guild in request.user.member.refresh_admin_servers()
        if not Server.objects.filter(id=guild.get("id")).exists()
    ]
    return render(request, "refresh_pages/server_select.html", {"admin_guilds": admin_guilds})


class BotView(View, ResponseMixin):
    template_name = "bot_page.html"
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
            return render(request, "404.html")

    def put(self, request, bot_id):
        try:
            bot = self.model.objects.get(id=bot_id)
            if request.user.member == bot.owner:
                if not bot.banned:
                    if bot.rejected:
                        bot.verification_status = "UNVERIFIED"
                        bot.meta.moderator = None
                        bot.meta.save()
                        bot.save()
                        return self.json_response_200()
                    return self.json_response_503()
                else:
                    return self.json_response_403()
            return self.json_response_401()
        except self.model.DoesNotExist:
            return self.json_response_404()


class LoginView(View):

    template_name = 'index.html'
    user_json = None
    token_json = None

    def get(self, request):
        code = request.GET.get('code')
        popup = request.GET.get('popup')
        oauth = normal_oauth
        if popup == "True":
            oauth = popup_oauth
        if code is not None:
            self.token_json = oauth.get_token_json(code)
            self.user_json = oauth.get_user_json(self.token_json.get("access_token"))
            self.user_json["token_data"] = self.token_json
            user_id = self.user_json.get("id")
            user = authenticate(username=user_id, password=hasher.get_hashed_pass(user_id))
            if user is None:
                user = create_user(self.user_json)
            else:
                update_user(user, self.user_json)
            if not user.member.banned:
                login(request, user)
            else:
                return render(request, self.template_name, {"banned": True, "search": True})
        else:
            error = "Internal Server Error"
            return render(request, self.template_name, {"error": error, "search": True})
        return IndexView.as_view()(self.request)


class IndexView(View):
    template_name = "index.html"

    def get(self, request):
        recent_bots = Bot.objects.filter(verified=True, banned=False, owner__banned=False).order_by('-date_added')[:8]
        trending_bots = Bot.objects.filter(verified=True, banned=False, owner__banned=False).order_by('-votes')[:8]
        return render(request, self.template_name,
                      {"search": True,
                       "random_bots": RANDOM_BOTS,
                       "recent_bots": recent_bots,
                       "trending_bots": trending_bots})


class AboutView(View):
    def get(self, request):
        return render(request, "about.html")


class TemplateView(View):
    template_name = "404.html"

    def get(self, request):
        return render(request, self.template_name)


class BotListView(ListView, ResponseMixin):
    template_name = "bot_list.html"
    model = Bot
    paginate_by = 40
    extra_context = {"search": True, "logo_off": True}

    def get_queryset(self):
        return self.model.objects.filter(verified=True, banned=False, owner__banned=False).order_by('-votes')

    def put(self, request):
        data = QueryDict(request.body)
        if request.user.is_authenticated:
            bot = Bot.objects.get(id=data.get("bot_id"))
            vote = BotVote.objects.filter(member=request.user.member, bot=bot).order_by("-creation_time").first()
            if vote is None:
                BotVote.objects.create(
                    member=request.user.member,
                    bot=bot,
                    creation_time=datetime.now(timezone.utc)
                )
                bot.votes += 1
                bot.save()
                return JsonResponse({"vote_count": bot.votes})
            elif (datetime.now(timezone.utc) - vote.creation_time).total_seconds() >= 43200:
                vote.delete()
                BotVote.objects.create(
                    member=request.user.member,
                    bot=bot,
                    creation_time=datetime.now(timezone.utc)
                )
                bot.votes += 1
                bot.save()
                return JsonResponse({"vote_count": bot.votes})
            else:
                return self.json_response_403()
        else:
            return self.json_response_401()


class BotAddView(LoginRequiredMixin, View):
    template_name = "bot_add.html"
    context = {}

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        data = request.POST
        bot_id = data.get("id")
        if int(bot_id) <= 9223372036854775807:
            if not Bot.objects.filter(id=bot_id).exists():
                self.context["tags"] = BOT_TAGS
                resp = discord_client.get_bot_info(bot_id)
                if resp.status_code == 404:
                    self.context["error"] = "Bot account does not exists!"
                elif resp.status_code == 200:
                    resp = resp.json()
                    bot = Bot.objects.create(id=bot_id,
                                             name=resp.get("username"),
                                             owner=request.user.member,
                                             invite_link=data.get("invite"),
                                             date_added=datetime.now(timezone.utc),
                                             avatar=resp.get("avatar"),
                                             short_desc=data.get("short_desc"))
                    bot.tags.set(BotTag.objects.filter(name__in=data.getlist('tags')))
                    bot.meta.support_server = data.get("support_server")
                    bot.meta.prefix = data.get("prefix")
                    bot.meta.github = data.get("github")
                    bot.meta.website = data.get("website")
                    bot.meta.library = data.get("library")
                    bot.meta.twitter = data.get("twitter")
                    bot.meta.support_server = data.get("support_server")
                    bot.meta.privacy = data.get("privacy")
                    bot.meta.donate = data.get("donate")
                    bot.meta.long_desc = data.get("long_desc")
                    bot.meta.save()
                    request.user.member.send_message(
                        "<:botadded:652482091971248140> Your bot is added and is currently awaiting verification."
                    )
                    self.context["success"] = "Bot added successfully!"
                    self.context["member"] = request.user.member
                    return render(request, "profile_page.html", self.context)
                else:
                    self.context["error"] = "Internal Server Error"
            else:
                self.context["error"] = "Bot record Exists. Please add a new bot."
        else:
            self.context["error"] = "Enter a valid Bot Id"
        return render(request, self.template_name, self.context)


class BotEditView(LoginRequiredMixin, View, ResponseMixin):
    template_name = "bot_edit.html"
    context = {}

    def get(self, request, bot_id):
        bot = Bot.objects.get(id=bot_id)
        return render(request, self.template_name, {"bot": bot, "tags": BOT_TAGS})

    def post(self, request):
        data = request.POST
        bot_id = data.get("id")
        if bot_id is not None:
            bot = Bot.objects.get(id=bot_id)
            if request.user.member == bot.owner:
                bot.invite_link = data.get("invite")
                bot.short_desc = data.get("short_desc")
                bot.save()
                bot.tags.set(BotTag.objects.filter(name__in=data.getlist('tags')))
                bot.meta.support_server = data.get("support_server")
                bot.meta.prefix = data.get("prefix")
                bot.meta.github = data.get("github")
                bot.meta.website = data.get("website")
                bot.meta.library = data.get("library")
                bot.meta.twitter = data.get("twitter")
                bot.meta.donate = data.get("donate")
                bot.meta.support_server = data.get("support_server")
                bot.meta.privacy = data.get("privacy")
                bot.meta.long_desc = data.get("long_desc")
                bot.meta.save()
                return render(request, self.template_name,
                              {"bot": bot, "tags": BOT_TAGS, "success": "Bot edited successfully!"})
        else:
            return ProfileView.as_view(self.request, {"error": "Internal Server error"})

    def put(self, request):
        if request.user.is_authenticated:
            data = QueryDict(request.body)
            bot_id = data.get("bot_id")
            if BotReport.objects.filter(bot_id=bot_id, reporter=self.request.user.member, reviewed=False).exists():
                return self.json_response_403()
            BotReport.objects.create(
                bot_id=bot_id,
                reporter=request.user.member,
                reason=data.get("reason"),
                creation_date=datetime.now(timezone.utc)
            )
            return self.json_response_200()
        return self.json_response_401()

    def delete(self, request):
        if request.user.is_authenticated:
            bot_id = request.GET.get("bot_id")
            try:
                bot = Bot.objects.get(id=bot_id)
                if bot.owner == request.user.member:
                    bot.delete()
                    return self.json_response_200()
            except Bot.DoesNotExist:
                return self.json_response_404()
        return self.json_response_401()


class ProfileView(LoginRequiredMixin, View):
    template_name = "profile_page.html"

    def get(self, request, user_id=None):
        if not user_id:
            return render(request, self.template_name, {"member": request.user.member})
        try:
            member = Member.objects.get(id=user_id)
            return render(request, self.template_name, {"member": member})
        except User.DoesNotExist:
            return render(request, "404.html")


class ProfileEditView(LoginRequiredMixin, View):
    template_name = "profile_edit.html"
    fields = ["website", "bio", "reddit", "github", "twitter", "facebook", "discordbio"]

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        meta = request.user.member.meta
        for field in self.fields:
            value = request.POST.get(field)
            if value is not None:
                setattr(meta, field, value)
        meta.save()
        return render(request, self.template_name, {"success": "Profile edited successfully!"})


class StaffView(View, ResponseMixin):
    template_name = "staff.html"
    context = {}

    def get(self, request):
        if request.user.is_staff:
            awaiting_review = Bot.objects.filter(verification_status="UNVERIFIED",
                                                 banned=False).order_by('date_added')[:10]
            under_review = Bot.objects.filter(verification_status="UNDER_REVIEW",
                                              banned=False).order_by('date_added')[:10]
            return render(request, self.template_name, {
                "bots_awaiting_review": awaiting_review,
                "bots_under_review": under_review
            })
        else:
            return self.http_responce_404(request)

    def post(self, request):
        if request.user.is_staff:
            if not Bot.objects.filter(meta__moderator=request.user.member, verification_status="UNDER_REVIEW").exists():
                bot_id = request.POST.get("bot_id")
                try:
                    bot = Bot.objects.get(id=bot_id)
                    if bot.meta.moderator and bot.meta.moderator != request.user.member:
                        return self.json_response_503()
                    else:
                        bot.verification_status = "UNDER_REVIEW"
                        bot.meta.moderator = request.user.member
                        bot.save()
                        bot.meta.save()
                        awaiting_review = Bot.objects.filter(verification_status="UNVERIFIED",
                                                             banned=False).order_by('date_added')[:10]
                        under_review = Bot.objects.filter(verification_status="UNDER_REVIEW",
                                                          banned=False).order_by('date_added')[:10]
                        return render(request, "refresh_pages/queue.html", {
                            "bots_awaiting_review": awaiting_review,
                            "bots_under_review": under_review
                        })
                except Bot.DoesNotExist:
                    return self.json_response_404()
            return self.json_response_403()
        return self.json_response_401()

    def put(self, request):
        if request.user.is_staff:
            data = QueryDict(request.body)
            try:
                bot = Bot.objects.get(id=data.get("bot_id"))
                if data.get("action") == "verify":
                    bot.verified = True
                    bot.verification_status = "VERIFIED"
                    bot.save()
                    bot.owner.send_message(
                        "<:botadded:652482091971248140> Your bot is now verified and is now public."
                    )
                elif data.get("action") == "reject":
                    bot.meta.rejection_count += 1
                    bot.owner.send_message(f"Your bot got rejected for reason: {data.get('rejection_reason')}")
                    if bot.meta.rejection_count == 3:
                        bot.banned = True
                        bot.verified = False
                        bot.save()
                        bot.meta.ban_reason = "Got rejected 3 times."
                        bot.owner.send_message(
                            f"<:botdeclined:652482092499730433> "
                            f"Your bot got shadow banned since it got rejected 3 times."
                        )
                    bot.verification_status = "REJECTED"
                    bot.save()
                    bot.meta.rejection_reason = data.get("rejection_reason")
                    bot.meta.save()
                elif data.get("action") == "ban":
                    bot.banned = True
                    bot.verified = False
                    bot.meta.ban_reason = data.get("ban_reason")
                    bot.meta.save()
                    bot.save()
                    bot.owner.send_message(
                        f"<:botdeclined:652482092499730433> "
                        f"Your bot got banned for the reason: {data.get('ban_reason')}"
                    )
                else:
                    return self.json_response_500()
                awaiting_review = Bot.objects.filter(verification_status="UNVERIFIED",
                                                     banned=False).order_by('date_added')[:10]
                under_review = Bot.objects.filter(verification_status="UNDER_REVIEW",
                                                  banned=False).order_by('date_added')[:10]
                return render(request, "refresh_pages/queue.html", {
                    "bots_awaiting_review": awaiting_review,
                    "bots_under_review": under_review
                })
            except Bot.DoesNotExist:
                return self.json_response_404()
        else:
            return self.json_response_401()


class BotSearchView(ListView):
    paginate_by = 16
    template_name = "bot_search.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        tag = self.request.GET.get("tag")
        if tag:
            return Bot.objects.filter(tags__name__contains=tag).order_by("-votes")
        if query:
            if query.isdigit():
                return Bot.objects.filter(
                    id__exact=query
                ).order_by("-votes")
            else:
                return Bot.objects.filter(
                    Q(name__contains=query) | Q(tags__name__contains=query),
                    banned=False, owner__banned=False
                ).order_by("-votes")


class ServerListView(ListView, ResponseMixin):
    template_name = "server_list.html"
    model = Server
    paginate_by = 40
    extra_context = {"search": True, "logo_off": True}

    def get_queryset(self):
        return self.model.objects.filter(verified=True, owner__banned=False).order_by('-votes')


class ServerView(View, ResponseMixin):
    template_name = "server_page.html"
    model = Server

    def get(self, request, bot_id):
        try:
            server = self.model.objects.get(id=bot_id)
            if server.banned or not server.verified:
                if request.user.is_authenticated:
                    if request.user.member == server.owner or request.user.is_staff:
                        return render(request, self.template_name, {"server": server})
                return render(request, "404.html")
            return render(request, self.template_name, {"server": server})
        except self.model.DoesNotExist:
            return render(request, "404.html")


class ServerSearchView(ListView):
    paginate_by = 16
    template_name = "server_search.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        tag = self.request.GET.get("tag")
        if tag:
            return Server.objects.filter(tags__name__contains=tag).order_by("-votes")
        if query:
            if query.isdigit():
                return Server.objects.filter(
                    id__exact=query
                ).order_by("-votes")
            else:
                return Server.objects.filter(
                    Q(name__contains=query) | Q(tags__name__contains=query),
                    banned=False, owner__banned=False
                ).order_by("-votes")


class ServerAddView(LoginRequiredMixin, View):
    template_name = "server_add.html"
    context = {}

    def get(self, request):
        if not request.user.member.meta.admin_servers:
            request.user.member.refresh_admin_servers()
        admin_guilds = [
            (guild.get("id"), guild.get("name")) for guild in request.user.member.meta.admin_servers
            if not Server.objects.filter(id=guild.get("id")).exists()
        ]
        return render(request, self.template_name, {"admin_guilds": admin_guilds, "tags": SERVER_TAGS})

    def post(self, request):
        data = request.POST
        server_id = data.get("server_id")
        server_data = request.user.member.get_admin_server_data(server_id)
        server = Server.objects.create(id=server_id,
                                       name=server_data.get("name"),
                                       owner=request.user.member,
                                       invite_link=data.get("invite"),
                                       date_added=datetime.now(timezone.utc),
                                       icon=server_data.get("icon"),
                                       short_desc=data.get("short_desc"),
                                       is_nsfw=data.get('nsfw') == 'checkedValue'
                                       )
        server.tags.set(ServerTag.objects.filter(name__in=data.getlist('server_tags')))
        server.meta.long_desc = data.get("long_desc")
        server.meta.save()
        request.user.member.send_message(
            "<:botadded:652482091971248140> Your server is added and is currently awaiting verification."
        )
        self.context["success"] = "Server added successfully!"
        self.context["member"] = request.user.member
        return render(request, "profile_page.html", self.context)


class ServerEditView(View, ResponseMixin):
    template_name = "server_edit.html"

    def get(self, request, server_id):
        server = Server.objects.get(id=server_id)
        return render(request, self.template_name, {"server": server, "tags": SERVER_TAGS})

    def post(self, request):
        data = request.POST
        server_id = data.get("server_id")
        if server_id is not None:
            server = Server.objects.get(id=server_id)
            if request.user.member == server.owner or request.user.member in server.admins.all():
                server.invite_link = data.get("invite")
                server.short_desc = data.get("short_desc")
                server.save()
                server.tags.set(BotTag.objects.filter(name__in=data.getlist('tags')))
                server.meta.long_desc = data.get("long_desc")
                server.meta.save()
                return render(request, self.template_name,
                              {"bot": server, "tags": BOT_TAGS, "success": "Server edited successfully!"})
        else:
            return ProfileView.as_view(self.request, {"error": "Internal Server error"})