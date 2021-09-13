import uuid
from datetime import datetime, timezone, timedelta
from django.db import models
from django.contrib.auth.models import User
from utils.oauth import Oauth
from utils.embedhandler import EmbedHandler
from utils.api_client import DiscordAPIClient
from rest_framework.authtoken.models import Token

oauth = Oauth()
embed_handler = EmbedHandler()
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
    def has_bots(self):
        return self.bots.first()

    @property
    def has_servers(self):
        return self.servers.first()

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

    @property
    def api_token(self):
        return Token.objects.get(user=self.user)

    @property
    def web_url(self):
        return f"https://bladelist.gg/users/{self.id}"

    def refresh_access_token(self):
        token_json = oauth.refresh_access_token(self.meta.refresh_token)
        self.meta.access_token = token_json.get("access_token")
        self.meta.refresh_token = token_json.get("refresh_token")
        self.meta.access_token_expiry = \
            datetime.now(timezone.utc) + timedelta(seconds=int(token_json.get("expires_in")))
        self.meta.save()

    def refresh_admin_servers(self):
        if self.meta.access_token:
            if self.meta.access_token_expiry > datetime.now(timezone.utc):
                self.refresh_access_token()
            admin_servers = [
                guild for guild in oauth.get_guild_info_json(self.meta.access_token) if int(guild.get("permissions")) & 8
                ]
            self.meta.admin_servers = admin_servers
            self.meta.save()
            return admin_servers
        return

    def get_admin_server_data(self, server_id):
        for server in self.meta.admin_servers:
            if server.get("id") == server_id:
                return server

    def sync_servers(self):
        for server in self.refresh_admin_servers():
            try:
                server_obj = Server.objects.get(id=server["id"])
                if self not in server_obj.admins.all():
                    server_obj.admins.add(self)
                if server["owner"] and server_obj.owner != self:
                    server_obj.owner = self
                    server_obj.save()
            except Server.DoesNotExist:
                pass


class MemberMeta(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="meta")
    bio = models.TextField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    discordbio = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    reddit = models.URLField(null=True, blank=True)
    access_token = models.CharField(max_length=32, null=True, blank=True)
    refresh_token = models.CharField(max_length=32, null=True, blank=True)
    access_token_expiry = models.DateTimeField(null=True, blank=True)
    admin_servers = models.JSONField(null=True, blank=True)


class BotTag(models.Model):
    name = models.CharField(max_length=15, primary_key=True)
    icon = models.CharField(max_length=25)


class ServerTag(models.Model):
    name = models.CharField(max_length=25, primary_key=True)
    icon = models.CharField(max_length=30)


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
    server_count = models.IntegerField(default=0, null=True)
    avatar = models.CharField(max_length=100, null=True)
    short_desc = models.CharField(max_length=120, null=True)
    tags = models.ManyToManyField(BotTag, related_name="bots", blank=True)
    banner_url = models.URLField(default="https://i.postimg.cc/15TN17rQ/xirprofilback.jpg")
    admins = models.ManyToManyField(Member, related_name="admin_bots")

    @property
    def rejected(self):
        return self.get_verification_status_display() == "Rejected"

    @property
    def unverified(self):
        return self.get_verification_status_display() == "Unverified"

    @property
    def verification_attempt(self):
        return self.meta.rejection_count + 1

    @property
    def avatar_url(self):
        if self.avatar is not None:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        return "https://cdn.discordapp.com/embed/avatars/4.png"

    @property
    def web_url(self):
        return f"https://bladelist.gg/bots/{self.id}"

    def embed(self, status):
        return embed_handler.bot_verification(self, status)


class BotMeta(models.Model):
    bot = models.OneToOneField(Bot, on_delete=models.CASCADE, related_name="meta")
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
    moderator = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    long_desc = models.TextField(null=True, blank=True)
    total_invites = models.IntegerField(default=0, null=True)


class BotReport(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(Member, related_name="reported_bots", on_delete=models.CASCADE)
    reason = models.TextField()
    creation_date = models.DateTimeField()
    reviewed = models.BooleanField(default=False)


class BotVote(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    member = models.ForeignKey(Member, related_name="voted_bots", on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, related_name="all_votes", on_delete=models.CASCADE, null=True)
    creation_time = models.DateTimeField(null=True)


class Server(models.Model):
    VERIFICATION_STATUS = (
        ("VERIFIED", "Verified"),
        ("UNVERIFIED", "Unverified"),
        ("UNDER_REVIEW", "Under Review"),
        ("REJECTED", "Rejected")
    )
    id = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(Member, related_name="servers", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    invite_link = models.URLField()
    votes = models.IntegerField(default=0)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default="UNVERIFIED")
    verified = models.BooleanField(default=False)
    date_added = models.DateTimeField()
    is_nsfw = models.BooleanField(default=False)
    members_online = models.IntegerField(default=0, null=True)
    icon = models.CharField(max_length=100, null=True)
    short_desc = models.CharField(max_length=120, null=True)
    tags = models.ManyToManyField(ServerTag, related_name="attached_servers", blank=True)
    banner_url = models.URLField(default="https://i.postimg.cc/15TN17rQ/xirprofilback.jpg")
    banned = models.BooleanField(default=False)
    admins = models.ManyToManyField(Member, related_name="admin_servers")

    @property
    def icon_url(self):
        return f"https://cdn.discordapp.com/icons/{self.id}/{self.icon}.png"

    @property
    def verification_attempt(self):
        return self.meta.rejection_count + 1

    @property
    def rejected(self):
        return self.get_verification_status_display() == "Rejected"

    @property
    def unverified(self):
        return self.get_verification_status_display() == "Unverified"


class ServerMeta(models.Model):
    server = models.OneToOneField(Server, on_delete=models.CASCADE, related_name="meta")
    long_desc = models.TextField(null=True, blank=True)
    ban_reason = models.TextField(null=True, blank=True)
    member_count = models.IntegerField(default=0, null=True)
    rejection_count = models.IntegerField(default=0)
    rejection_reason = models.TextField(null=True, blank=True)
    moderator = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    total_invites = models.IntegerField(default=0, null=True)


class ServerVote(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    member = models.ForeignKey(Member, related_name="voted_servers", on_delete=models.CASCADE)
    server = models.ForeignKey(Server, related_name="all_votes", on_delete=models.CASCADE, null=True)
    creation_time = models.DateTimeField(null=True)


class ServerReport(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(Member, related_name="reported_servers", on_delete=models.CASCADE)
    reason = models.TextField()
    creation_date = models.DateTimeField()
    reviewed = models.BooleanField(default=False)
    reviewer = models.ForeignKey(Member, null=True, related_name="reports_reviewed", on_delete=models.SET_NULL)
