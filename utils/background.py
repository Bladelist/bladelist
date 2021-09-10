from datetime import datetime, timezone, timedelta
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

from main_site.models import Member, Bot, BotMeta, MemberMeta, Server, ServerMeta
from utils.hashing import Hasher
from utils.api_client import DiscordAPIClient

api_client = DiscordAPIClient()
hasher = Hasher()


def create_user(user_json, api=False):
    user_id = user_json.get("id")
    user = User.objects.create_user(username=user_id,
                                    password=hasher.get_hashed_pass(user_id),
                                    first_name=user_json.get("username"))
    member = Member.objects.create(id=user_id,
                                   user=user,
                                   avatar=user_json.get("avatar"),
                                   tag=user_json.get("discriminator"),
                                   )
    if not api:
        member.meta.access_token = user_json.get("token_data")["access_token"]
        member.meta.refresh_token = user_json.get("token_data")["refresh_token"]
        member.meta.access_token_expiry = \
            datetime.now(timezone.utc) + timedelta(seconds=int(user_json.get("token_data")["expires_in"]))
        member.meta.save()
        member.sync_servers()
    return user


def update_user(user, user_json):
    user.first_name = user_json.get("username")
    user.member.avatar = user_json.get("avatar")
    user.member.tag = user_json.get("discriminator")
    user.member.save()
    user.member.meta.access_token = user_json.get("token_data")["access_token"]
    user.member.meta.refresh_token = user_json.get("token_data")["refresh_token"]
    user.member.meta.access_token_expiry = \
        datetime.now(timezone.utc) + timedelta(seconds=int(user_json.get("token_data")["expires_in"]))
    user.member.meta.save()
    user.member.sync_servers()
    user.save()


@receiver(post_save, sender=Bot)
def create_bot_meta(sender, instance, created, **kwargs):
    if created:
        BotMeta.objects.create(bot=instance)


@receiver(post_save, sender=Server)
def create_server_meta(sender, instance, created, **kwargs):
    if created:
        ServerMeta.objects.create(server=instance)


@receiver(post_save, sender=Member)
def create_member_meta(sender, instance, created, **kwargs):
    if created:
        MemberMeta.objects.create(member=instance)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Bot)
def alert_with_webhook(sender, instance=None, created=False, **kwargs):
    if created:
        instance.owner.send_message(
            f"<:botadded:652482091971248140> Your bot {instance.name} is added and is currently awaiting verification."
        )
    elif kwargs['update_fields']:
        if "banned" in kwargs['update_fields']:
            if instance.banned:
                instance.owner.send_message(
                    f"<:botdeclined:652482092499730433> "
                    f"Your bot {instance.name} got banned for the reason: {instance.meta.ban_reason}"
                )
            else:
                instance.owner.send_message(
                    f"<:botadded:652482091971248140> "
                    f"Your bot {instance.name} is unbanned"
                )
        elif "verification_status" in kwargs["update_fields"]:
            if instance.verification_status == "REJECTED":
                instance.owner.send_message(
                    f"<:botdeclined:652482092499730433> "
                    f"Your bot {instance.name} is rejected for the reason: {instance.meta.rejection_reason}"
                )
            else:
                instance.owner.send_message(
                    f"<:botadded:652482091971248140> Your bot {instance.name} is verified and is now public."
                )