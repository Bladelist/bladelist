import uuid
from django.db import models
from django.contrib.auth.models import User
from utils.oauth import Oauth
from utils.api_client import DiscordAPIClient
oauth = Oauth()
api_client = DiscordAPIClient()


class Member(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member")
    tag = models.CharField(max_length=4, default="0000")
    avatar = models.CharField(max_length=100, null=True)
    banned = models.BooleanField(default=False)
    ban_reason = models.TextField(null=True, blank=True)
    dm_channel = models.BigIntegerField(null=True, blank=True)

    @property
    def avatar_url(self):
        if self.avatar is not None:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        return "https://cdn.discordapp.com/embed/avatars/4.png"

    @property
    def verified_bots(self):
        return self.bots.filter(verified=True)

    def send_message(self, message):
        if not self.dm_channel:
            channel_id = api_client.create_dm_channel(self.id)
            if channel_id is not None:
                self.dm_channel = channel_id
                self.save()
        api_client.send_message(self.dm_channel, message)

    def send_embed(self, embed):
        if not self.dm_channel:
            channel_id = api_client.create_dm_channel(self.id)
            if channel_id is not None:
                self.dm_channel = channel_id
                self.save()
        api_client.send_embed(self.dm_channel, embed)


class MemberMeta(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="meta")
    bio = models.TextField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    discordbio = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    reddit = models.URLField(null=True, blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=15, primary_key=True)
    icon = models.CharField(max_length=25)


class Bot(models.Model):
    VERIFICATION_STATUS = (
        ("VERIFIED", "Verified"),
        ("UNVERIFIED", "Unverified"),
        ("UNDER_REVIEW", "Under Review"),
        ("REJECTED", "Rejected")
    )
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(Member, related_name="bots", on_delete=models.CASCADE)
    invite_link = models.URLField()
    votes = models.IntegerField(default=0)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default="UNVERIFIED")
    online = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    date_added = models.DateTimeField()
    server_count = models.IntegerField(default=0)
    avatar = models.CharField(max_length=100, null=True)
    short_desc = models.CharField(max_length=120, null=True)
    tags = models.ManyToManyField(Tag, related_name="bots", blank=True)
    banner_url = models.URLField(default="https://i.postimg.cc/15TN17rQ/xirprofilback.jpg")

    @property
    def rejected(self):
        return self.get_verification_status_display() == "Rejected"

    @property
    def unverified(self):
        return self.get_verification_status_display() == "Unverified"

    @property
    def avatar_url(self):
        if self.avatar is not None:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        return "https://cdn.discordapp.com/embed/avatars/4.png"


class BotMeta(models.Model):
    bot = models.OneToOneField(Bot, on_delete=models.CASCADE, related_name="meta")
    uptime = models.FloatField(default=100)
    prefix = models.CharField(max_length=10, null=True, blank=True, default="N/A")
    github = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    privacy = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    donate = models.URLField(null=True, blank=True)
    support_server = models.URLField(null=True, blank=True)
    library = models.CharField(max_length=15, null=True, blank=True, default="N/A")
    ban_reason = models.TextField(null=True, blank=True)
    shard_count = models.IntegerField(default=0, null=True)
    rejection_count = models.IntegerField(default=0)
    rejection_reason = models.TextField(null=True, blank=True)
    moderator = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    long_desc = models.TextField(null=True, blank=True)


class BotReport(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(Member, related_name="reported_bots", on_delete=models.CASCADE)
    reason = models.TextField()
    creation_date = models.DateTimeField()
    reviewed = models.BooleanField(default=False)


class Vote(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    member = models.ForeignKey(Member, related_name="voted_bots", on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, related_name="all_votes", on_delete=models.CASCADE, null=True)
    creation_time = models.DateTimeField(null=True)

