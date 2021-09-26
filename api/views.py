import pytz
from datetime import datetime
from rest_framework.views import APIView
from django.http import QueryDict
from main_site.models import Bot, BotTag, Member, Server
from utils.mixins import ResponseMixin
from rest_framework.response import Response
from .serializers import BotSerializer
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from utils.background import create_user
from utils.api_client import DiscordAPIClient
from .serializers import BotStatusSerializer, ServerSerializer, BotAllSerializer, ServerStatusSerializer
discord_api = DiscordAPIClient()


class BotManageView(APIView, ResponseMixin):

    serializers = BotSerializer

    def get(self, request, bot_id=None):
        if not bot_id and request.user.is_superuser:
            serializer = BotAllSerializer(Bot.objects.all(), many=True)
            return Response(serializer.data)
        queryset = get_object_or_404(Bot, id=bot_id)
        serializer = self.serializers(queryset)
        return Response(serializer.data, status=200)

    def put(self, request, bot_id):
        queryset = get_object_or_404(Bot, id=bot_id)
        if request.user.member == queryset.owner:
            if request.data.get("server_count"):
                queryset.server_count = request.data.get("server_count")
                queryset.save()
            if request.data.get("shard_count"):
                queryset.meta.shard_count = request.data.get("shard_count")
                queryset.meta.save()
            return self.json_response_200()
        return self.json_response_403()


class UserMigrateView(APIView, ResponseMixin):

    def post(self, request):
        if request.user.is_superuser:
            data = request.data
            if User.objects.filter(username=data.get("id")).exists():
                return self.json_response_503()
            create_user(data, api=True)
            return self.json_response_201()
        return self.json_response_401()


class BotMigrateView(APIView, ResponseMixin):

    def post(self, request):
        if request.user.is_superuser:
            """
             {
                "id": ,"username": "", "owner_id": , "invite": "", "short_desc": "", "date_added": "%d%m%Y",
                "votes": , "banned": False, "verified": True, "tags": [], "support_server": "", "prefix": "",
                "github": "", "website": "", "library": "", "twitter": "", "support_server": "", "privacy": "",
                "donate": "", "long_desc": ""
             }
            """
            data = request.data
            if Bot.objects.filter(id=data.get("id")).exists():
                return self.json_response_503()
            resp = discord_api.get_bot_info(data.get("id"))
            if resp.status_code == 404:
                return self.json_response_503()
            elif resp.status_code == 200:
                resp = resp.json()
                try:
                    owner = Member.objects.get(id=data.get("owner_id"))
                    bot = Bot.objects.create(id=data.get("id"),
                                             name=resp.get("username"),
                                             owner=owner,
                                             invite_link=data.get("invite"),
                                             date_added=datetime.utcfromtimestamp(
                                                 data.get("date_added", 1622042205981)/1000
                                             ).replace(tzinfo=pytz.utc),
                                             avatar=resp.get("avatar"),
                                             short_desc=data.get("short_desc"),
                                             votes=data.get("votes"),
                                             verification_status="VERIFIED" if data.get("verified") else "UNVERIFIED",
                                             banned=data.get("banned"),
                                             verified=data.get("verified"))
                    bot.tags.set(BotTag.objects.filter(name__in=data.get('tags')))
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
                except Member.DoesNotExist:
                    return self.json_response_404()
                return self.json_response_201()
            return self.json_response_400()
        return self.json_response_401()


class BotStatusEditView(APIView, ResponseMixin):
    model = Bot
    serializer = BotStatusSerializer

    def get(self, request, bot_id):
        if request.user.is_superuser:
            queryset = get_object_or_404(self.model, id=bot_id)
            serializer = self.serializer(queryset)
            return Response(serializer.data)
        return self.json_response_401()

    def put(self, request, bot_id):
        if request.user.is_superuser:
            bot = get_object_or_404(self.model, id=bot_id)
            verification_status = request.data.get("verification_status")
            moderator_id = request.data.get("moderator_id")
            bot.meta.moderator = Member.objects.get(id=moderator_id)
            bot.meta.save()
            bot.verification_status = verification_status
            if verification_status == "VERIFIED":
                bot.verified = True
                bot.save(update_fields=["verification_status", "verified"])
            elif verification_status == "REJECTED":
                bot.meta.rejection_count += 1
                bot.meta.rejection_reason = request.data.get("reason")
                bot.meta.save()
                bot.save(update_fields=["verification_status"])
                if bot.meta.rejection_count >= 3:
                    bot.banned = True
                    bot.verified = False
                    bot.meta.ban_reason = "Got rejected 3 times."
                    bot.meta.save()
                    bot.save(update_fields=["banned", "verified"])
            elif verification_status == "BANNED":
                bot.banned = True
                bot.verified = False
                bot.meta.ban_reason = request.data.get("reason")
                bot.meta.save()
                bot.save(update_fields=["banned"])
            elif verification_status == "UNBANNED":
                bot.banned = False
                bot.verified = True
                bot.save(update_fields=["banned", "verified", "verification_status"])
            else:
                return self.json_response_400()
            return self.json_response_200()
        return self.json_response_401()


class ServerView(APIView, ResponseMixin):

    serializers = ServerSerializer

    def get(self, request, server_id):
        queryset = get_object_or_404(Server, id=server_id)
        serializer = self.serializers(queryset)
        return Response(serializer.data, status=200)


class ServerStatusEditView(APIView, ResponseMixin):
    model = Server
    serializer = ServerStatusSerializer

    def get(self, request, server_id):
        if request.user.is_superuser:
            queryset = get_object_or_404(self.model, id=server_id)
            serializer = self.serializer(queryset)
            return Response(serializer.data)
        return self.json_response_401()

    def put(self, request, server_id):
        if request.user.is_superuser:
            server = get_object_or_404(self.model, id=server_id)
            verification_status = request.data.get("verification_status")
            moderator_id = request.data.get("moderator_id")
            server.meta.moderator = Member.objects.get(id=moderator_id)
            server.meta.save()
            server.verification_status = verification_status
            if verification_status == "VERIFIED":
                server.verified = True
                server.save(update_fields=["verification_status", "verified"])
            elif verification_status == "REJECTED":
                server.meta.rejection_count += 1
                server.meta.rejection_reason = request.data.get("reason")
                server.meta.save()
                server.save(update_fields=["verification_status"])
                if server.meta.rejection_count >= 3:
                    server.banned = True
                    server.verified = False
                    server.meta.ban_reason = "Got rejected 3 times."
                    server.meta.save()
                    server.save(update_fields=["banned", "verified"])
            elif verification_status == "BANNED":
                server.banned = True
                server.verified = False
                server.meta.ban_reason = request.data.get("reason")
                server.meta.save()
                server.save(update_fields=["banned"])
            elif verification_status == "UNBANNED":
                server.banned = False
                server.verified = True
                server.save(update_fields=["banned", "verified", "verification_status"])
            else:
                return self.json_response_400()
            return self.json_response_200()
        return self.json_response_401()
