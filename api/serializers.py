from rest_framework import serializers
from main_site.models import Bot, BotMeta


class BotMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotMeta
        exclude = ("bot", "long_desc", "moderator")


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
