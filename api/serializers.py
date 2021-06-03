from rest_framework import serializers
from main_site.models import Bot, BotMeta


class BotMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotMeta
        exclude = ("bot", "ban_reason", "rejection_count", "rejection_reason", "moderator")


class BotSerializer(serializers.ModelSerializer):
    meta = BotMetaSerializer()

    class Meta:
        model = Bot
        fields = ("id", "name", "invite_link", "votes", "short_desc", "meta")


class BotEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ["server_count"]
