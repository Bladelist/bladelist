import uuid
from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=100, null=True)
    banned = models.BooleanField(default=False)
    ban_reason = models.TextField(null=True, blank=True)


class Tag(models.Model):
    name = models.CharField(max_length=15, primary_key=True)
    icon = models.CharField(max_length=25)


class Bot(models.Model):
    VERIFICATION_STATUS = (
        ("VERIFIED", "Verified"),
        ("UNVERIFIED", "Unverified"),
        ("REJECTED", "Rejected")
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(Member, related_name="bots", on_delete=models.CASCADE)
    invite_link = models.URLField()
    votes = models.IntegerField(default=0)
    verification_status = models.CharField(choices=VERIFICATION_STATUS, default="UNVERIFIED")
    online = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    date_added = models.DateTimeField()


class BotMeta(models.Model):
    bot = models.OneToOneField(Bot, on_delete=models.CASCADE, related_name="meta")
    uptime = models.FloatField(default=100)
    prefix = models.CharField(max_length=10, null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    privacy = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    library = models.CharField(null=True, blank=True)
    ban_reason = models.TextField(null=True, blank=True)
    server_count = models.IntegerField(default=0, null=True)
    rejection_count = models.IntegerField(default=0)
    rejection_reason = models.TextField(null=True, blank=True)
    moderator = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)


class BotReport(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(Member, related_name="reported_bots", on_delete=models.CASCADE)
    reason = models.TextField()
    creation_date = models.DateTimeField()
    reviewed = models.BooleanField(default=False)
