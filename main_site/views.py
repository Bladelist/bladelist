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
RANDOM_SERVERS = Server.objects.filter(verified=True, banned=False, owner__banned=False).order_by("id").distinct()[:8]


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
    request.user.member.sync_servers()
    return render(request, "refresh_pages/server_select.html", {"admin_guilds": admin_guilds})


def bot_invite_counter(request, bot_id):
    try:
        bot = Bot.objects.get(id=bot_id)
        bot.meta.total_invites += 1
        bot.meta.save()
        return redirect(bot.invite_link)
    except Bot.DoesNotExist:
        return render(request, "404.html")


def server_invite_counter(request, server_id):
    try:
        server = Server.objects.get(id=server_id)
        server.meta.total_invites += 1
        server.meta.save()
        return redirect(server.invite_link)
    except Server.DoesNotExist:
        return render(request, "404.html")


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
            if request.user.member == bot.owner or request.user.member in bot.admins.all():
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
                discord_client.send_embed(bot.vote_embed(request.user.member))
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
                discord_client.send_embed(bot.vote_embed(request.user.member))
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
            if request.user.member == bot.owner or request.user.member in bot.admins.all():
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
            bots_awaiting_review = Bot.objects.filter(verification_status="UNVERIFIED",
                                                      banned=False, owner__banned=False).order_by('date_added')[:10]
            bots_under_review = Bot.objects.filter(verification_status="UNDER_REVIEW",
                                                   banned=False, owner__banned=False).order_by('date_added')[:10]
            servers_awaiting_review = Server.objects.filter(verification_status="UNVERIFIED",
                                                            banned=False, owner__banned=False
                                                            ).order_by("date_added")[:10]
            servers_under_review = Server.objects.filter(verification_status="UNDER_REVIEW",
                                                         banned=False, owner__banned=False).order_by("date_added")[:10]
            return render(request, self.template_name, {
                "bots_awaiting_review": bots_awaiting_review,
                "bots_under_review": bots_under_review,
                "servers_awaiting_review": servers_awaiting_review,
                "servers_under_review": servers_under_review

            })
        else:
            return self.http_responce_404(request)


class BotModerationView(LoginRequiredMixin, View, ResponseMixin):

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
                        bot.meta.save()
                        bot.save()
                        awaiting_review = Bot.objects.filter(verification_status="UNVERIFIED",
                                                             banned=False).order_by('date_added')[:10]
                        under_review = Bot.objects.filter(verification_status="UNDER_REVIEW",
                                                          banned=False).order_by('date_added')[:10]
                        return render(request, "refresh_pages/bot_queue.html", {
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
                if bot.meta.moderator != request.user.member:
                    bot.meta.moderator = request.user.member
                    bot.meta.save()
                if data.get("action") == "verify":
                    bot.verified = True
                    bot.verification_status = "VERIFIED"
                    bot.save(update_fields=["verification_status", "verified"])
                elif data.get("action") == "reject":
                    bot.meta.rejection_count += 1
                    bot.verification_status = "REJECTED"
                    bot.meta.rejection_reason = data.get("rejection_reason")
                    bot.meta.save()
                    bot.save(update_fields=["verification_status"])
                    if bot.meta.rejection_count >= 3:
                        bot.banned = True
                        bot.verified = False
                        bot.meta.ban_reason = "Got rejected 3 times."
                        bot.meta.save()
                        bot.save(update_fields=["banned", "verified"])
                elif data.get("action") == "ban":
                    bot.banned = True
                    bot.verified = False
                    bot.meta.ban_reason = data.get("ban_reason")
                    bot.meta.save()
                    bot.save(update_fields=["banned", "verified"])
                elif data.get("action") == "unban":
                    bot.banned = False
                    bot.verification_status = "VERIFIED"
                    bot.verified = True
                    bot.meta.save()
                    bot.save(update_fields=["banned", "verified", "verification_status"])
                else:
                    return self.json_response_500()
                awaiting_review = Bot.objects.filter(verification_status="UNVERIFIED",
                                                     banned=False).order_by('date_added')[:10]
                under_review = Bot.objects.filter(verification_status="UNDER_REVIEW",
                                                  banned=False).order_by('date_added')[:10]
                return render(request, "refresh_pages/bot_queue.html", {
                    "bots_awaiting_review": awaiting_review,
                    "bots_under_review": under_review
                })
            except Bot.DoesNotExist:
                return self.json_response_404()
        else:
            return self.json_response_401()


class ServerModerationView(LoginRequiredMixin, View, ResponseMixin):

    def post(self, request):
        if request.user.is_staff:
            if not Server.objects.filter(
                    meta__moderator=request.user.member, verification_status="UNDER_REVIEW"
            ).exists():
                server_id = request.POST.get("server_id")
                try:
                    server = Server.objects.get(id=server_id)
                    if server.meta.moderator and server.meta.moderator != request.user.member:
                        return self.json_response_503()
                    else:
                        server.verification_status = "UNDER_REVIEW"
                        server.meta.moderator = request.user.member
                        server.save()
                        server.meta.save()
                        awaiting_review = Server.objects.filter(verification_status="UNVERIFIED",
                                                                banned=False, owner__banned=False
                                                                ).order_by('date_added')[:10]
                        under_review = Server.objects.filter(verification_status="UNDER_REVIEW",
                                                             banned=False, owner__banned=False
                                                             ).order_by('date_added')[:10]
                        return render(request, "refresh_pages/server_queue.html", {
                            "servers_awaiting_review": awaiting_review,
                            "servers_under_review": under_review
                        })
                except Server.DoesNotExist:
                    return self.json_response_404()
            return self.json_response_403()
        return self.json_response_401()

    def put(self, request):
        if request.user.is_staff:
            data = QueryDict(request.body)
            try:
                server = Server.objects.get(id=data.get("server_id"))
                if server.meta.moderator != request.user.member:
                    server.meta.moderator = request.user.member
                    server.meta.save()
                if data.get("action") == "verify":
                    server.verified = True
                    server.verification_status = "VERIFIED"
                    server.save(update_fields=["verification_status", "verified"])
                elif data.get("action") == "reject":
                    server.meta.rejection_count += 1
                    server.verification_status = "REJECTED"
                    server.meta.rejection_reason = data.get("rejection_reason")
                    server.meta.save()
                    server.save(update_fields=["verification_status"])
                    if server.meta.rejection_count >= 3:
                        server.banned = True
                        server.verified = False
                        server.meta.ban_reason = "Got rejected 3 times."
                        server.meta.save()
                        server.save(update_fields=["banned", "verified"])
                elif data.get("action") == "ban":
                    server.banned = True
                    server.verified = False
                    server.meta.ban_reason = data.get("ban_reason")
                    server.meta.save()
                    server.save(update_fields=["banned", "verified"])
                elif data.get("action") == "unban":
                    server.banned = False
                    server.verified = True
                    server.verification_status = "VERIFIED"
                    server.save(update_fields=["verification_status", "banned", "verified"])
                else:
                    return self.json_response_500()
                awaiting_review = Server.objects.filter(verification_status="UNVERIFIED",
                                                        banned=False).order_by('date_added')[:10]
                under_review = Server.objects.filter(verification_status="UNDER_REVIEW",
                                                     banned=False).order_by('date_added')[:10]
                return render(request, "refresh_pages/server_queue.html", {
                    "servers_awaiting_review": awaiting_review,
                    "servers_under_review": under_review
                })
            except Server.DoesNotExist:
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
            return Bot.objects.filter(tags__name__contains=tag,
                                      owner__banned=False,
                                      verified=True,
                                      banned=False
                                      ).order_by("-votes")
        if query:
            if query.isdigit():
                return Bot.objects.filter(
                    id__exact=query,
                    verified=True,
                    banned=False,
                    owner__banned=False
                ).order_by("-votes")
            else:
                return Bot.objects.filter(
                    Q(name__contains=query) | Q(tags__name__contains=query),
                    banned=False, owner__banned=False, verified=True
                ).order_by("-votes")


class ServerIndexView(View, ResponseMixin):
    template_name = "server_index.html"

    def get(self, request):
        recent_servers = Server.objects.filter(
            verified=True, banned=False, owner__banned=False).order_by('-date_added')[:8]
        trending_servers = Server.objects.filter(
            verified=True, banned=False, owner__banned=False).order_by('-votes')[:8]
        return render(request, self.template_name,
                      {"random_servers": RANDOM_SERVERS,
                       "recent_servers": recent_servers,
                       "trending_servers": trending_servers,
                       "tags": SERVER_TAGS})

    def put(self, request):
        data = QueryDict(request.body)
        if request.user.is_authenticated:
            server = Server.objects.get(id=data.get("server_id"))
            vote = ServerVote.objects.filter(
                member=request.user.member, server=server
            ).order_by("-creation_time").first()
            if vote is None:
                ServerVote.objects.create(
                    member=request.user.member,
                    server=server,
                    creation_time=datetime.now(timezone.utc)
                )
                server.votes += 1
                server.save()
                discord_client.send_embed(server.vote_embed(request.user.member))
                return JsonResponse({"vote_count": server.votes})
            elif (datetime.now(timezone.utc) - vote.creation_time).total_seconds() >= 43200:
                vote.delete()
                ServerVote.objects.create(
                    member=request.user.member,
                    server=server,
                    creation_time=datetime.now(timezone.utc)
                )
                server.votes += 1
                server.save()
                discord_client.send_embed(server.vote_embed(request.user.member))
                return JsonResponse({"vote_count": server.votes})
            else:
                return self.json_response_403()
        else:
            return self.json_response_401()


class ServerListView(ListView, ResponseMixin):
    template_name = "server_list.html"
    model = Server
    paginate_by = 40
    extra_context = {"search": True, "logo_off": True}

    def get_queryset(self):
        return self.model.objects.filter(verified=True, owner__banned=False, banned=False).order_by('-votes')


class ServerView(View, ResponseMixin):
    template_name = "server_page.html"
    model = Server

    def get(self, request, server_id):
        try:
            server = self.model.objects.get(id=server_id)
            if server.banned or not server.verified:
                if request.user.is_authenticated:
                    if request.user.member in server.admins.all() or request.user.is_staff:
                        return render(request, self.template_name, {"server": server, "search_off": True})
                return render(request, "404.html")
            return render(request, self.template_name, {"server": server, "search_off": True})
        except self.model.DoesNotExist:
            return render(request, "404.html")

    def put(self, request, server_id):
        try:
            server = self.model.objects.get(id=server_id)
            if request.user.member == server.owner:
                if not server.banned:
                    if server.rejected:
                        server.verification_status = "UNVERIFIED"
                        server.meta.moderator = None
                        server.meta.save()
                        server.save()
                        return self.json_response_200()
                    return self.json_response_503()
                else:
                    return self.json_response_403()
            return self.json_response_401()
        except self.model.DoesNotExist:
            return self.json_response_404()
        
        
class ServerSearchView(ListView):
    paginate_by = 16
    template_name = "server_list.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        tag = self.request.GET.get("tag")
        if tag:
            return Server.objects.filter(tags__name__contains=tag,
                                         verified=True,
                                         banned=False,
                                         owner__banned=False
                                         ).order_by("-votes")
        if query:
            if query.isdigit():
                return Server.objects.filter(
                    id__exact=query,
                    verified=True,
                    banned=False,
                    owner__banned=False
                ).order_by("-votes")
            else:
                return Server.objects.filter(
                    Q(name__contains=query) | Q(tags__name__contains=query),
                    banned=False, owner__banned=False, verified=True
                ).order_by("-votes")


class ServerAddView(LoginRequiredMixin, View):
    template_name = "server_add.html"
    context = {"search_off": True, "logo_off": True}

    def get(self, request):
        if not request.user.member.meta.admin_servers:
            if request.user.member.refresh_admin_servers() is None:
                logout(request)
                return redirect("/accounts/login/")
        admin_guilds = [
            (guild.get("id"), guild.get("name")) for guild in request.user.member.meta.admin_servers
            if not Server.objects.filter(id=guild.get("id")).exists()
        ]
        return render(request, self.template_name, {"admin_guilds": admin_guilds, "tags": SERVER_TAGS,
                                                    "search_off": True, "logo_off": True})

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
        server.admins.add(request.user.member)
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
    context = {"search_off": True, "logo_off": True}

    def get(self, request, server_id):
        server = Server.objects.get(id=server_id)
        if request.user.member in server.admins.all():
            self.context["server"] = server
            self.context['tags'] = SERVER_TAGS
            return render(request, self.template_name, self.context)

    def post(self, request, server_id):
        data = request.POST
        if server_id is not None:
            server = Server.objects.get(id=server_id)
            if server:
                if request.user.member in server.admins.all():
                    server.invite_link = data.get("invite")
                    server.short_desc = data.get("short_desc")
                    server.save()
                    server.tags.set(ServerTag.objects.filter(name__in=data.getlist('server_tags')))
                    server.meta.long_desc = data.get("long_desc")
                    server.meta.save()
                    self.context["server"] = server
                    self.context["tags"] = SERVER_TAGS
                    self.context["success"] = "Server edited successfully!"
                    return render(request, self.template_name, self.context)
            else:
                return ProfileView.as_view(self.request, {"error": "Server not found"})
        else:
            return ProfileView.as_view(self.request, {"error": "Internal Server error"})

    def put(self, request):
        if request.user.is_authenticated:
            data = QueryDict(request.body)
            server_id = data.get("server_id")
            if ServerReport.objects.filter(
                    server_id=server_id, reporter=self.request.user.member, reviewed=False
            ).exists():
                return self.json_response_403()
            ServerReport.objects.create(
                server_id=server_id,
                reporter=request.user.member,
                reason=data.get("reason"),
                creation_date=datetime.now(timezone.utc)
            )
            return self.json_response_200()
        return self.json_response_401()

    def delete(self, request):
        if request.user.is_authenticated:
            server_id = request.GET.get("server_id")
            try:
                server = Server.objects.get(id=server_id)
                if request.user.member in server.admins.all():
                    server.delete()
                    return self.json_response_200()
            except Server.DoesNotExist:
                return self.json_response_404()
        return self.json_response_401()
