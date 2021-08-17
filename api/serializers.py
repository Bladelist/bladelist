from rest_framework import serializers
from main_site.models import Bot, BotMeta, Server, ServerMeta


class BotMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotMeta
        exclude = ("id", "bot", "long_desc", "moderator", "rejection_reason", "rejection_count", "ban_reason")


class BotSerializer(serializers.ModelSerializer):
    meta = BotMetaSerializer()

    class Meta:
        model = Bot
        fields = ("id", "name", "invite_link", "votes", "short_desc", "meta")


class BotEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ["server_count"]


class BotStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bot
        fields = ["verified", "banned", "verification_status"]


class ServerMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerMeta
        fields = ("member_count", "total_invites")


class ServerSerializer(serializers.ModelSerializer):
    meta = ServerMetaSerializer()

    class Meta:
        model = Server
        fields = ("id", "name", "invite_link", "votes", "short_desc", "members_online", "is_nsfw", "meta")
