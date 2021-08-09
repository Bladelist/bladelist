from rest_framework.views import APIView
from main_site.models import Bot
from utils.mixins import ResponseMixin
from rest_framework.response import Response
from .serializers import BotSerializer
from rest_framework.generics import get_object_or_404
from django.contrib.auth.models import User
from utils.background import create_user
from utils.api_client import DiscordAPIClient

discord_api = DiscordAPIClient()


class BotManageView(APIView, ResponseMixin):

    serializers = BotSerializer

    def get(self, request, bot_id):
        queryset = get_object_or_404(Bot, id=bot_id)
        serializer = self.serializers(queryset, context={'request': request})
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
