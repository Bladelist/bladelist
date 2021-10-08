
from rest_framework.views import APIView
from main_site.models import Bot, Server
from utils.mixins import ResponseMixin
from rest_framework.response import Response
from .serializers import BotSerializer
from rest_framework.generics import get_object_or_404

from utils.api_client import DiscordAPIClient
from .serializers import ServerSerializer
discord_api = DiscordAPIClient()


class BotManageView(APIView, ResponseMixin):

    """
        USE: For owners to update the bot server_count and shard_count in regular intervals
        TYPE: GET, PUT
        DATA {"server_count": int, "shard_count": int}
    """

    serializers = BotSerializer

    def get(self, request, bot_id):
        # if not bot_id and request.user.is_superuser:
        #     serializer = BotAllSerializer(Bot.objects.all(), many=True)
        #     return Response(serializer.data)
        queryset = get_object_or_404(Bot, id=bot_id)
        serializer = self.serializers(queryset)
        return Response(serializer.data, status=200)

    def post(self, request, bot_id):
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


class ServerManageView(APIView, ResponseMixin):

    """
        USE: For bot to update the server member_count and members_online in regular intervals
        TYPE: GET, PUT
        DATA {"members_online": int, "member_count": int}
    """

    serializers = ServerSerializer

    def get(self, request, server_id):
        queryset = get_object_or_404(Server, id=server_id)
        serializer = self.serializers(queryset)
        return Response(serializer.data, status=200)

    def put(self, request, server_id):
        queryset = get_object_or_404(Server, id=server_id)
        if request.user.is_superuser:
            if request.data.get("members_online"):
                queryset.members_online = request.data.get("members_online")
                queryset.save()
            if request.data.get("member_count"):
                queryset.meta.member_count = request.data.get("member_count")
                queryset.meta.save()
            return self.json_response_200()
        return self.json_response_401()

