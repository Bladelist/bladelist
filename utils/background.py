from datetime import datetime
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from main_site.models import Member, Bot, BotMeta
from utils.hashing import Hasher

hasher = Hasher()


def create_user(user_json):
    user_id = user_json.get("id")
    user = User.objects.create_user(username=user_id,
                                    password=hasher.get_hashed_pass(user_id),
                                    first_name=user_json.get("username"))
    Member.objects.create(id=user_id,
                          user=user,
                          avatar=user_json.get("avatar"),
                          tag=user_json.get("discriminator"),
                          )
    return user


def update_user(user, user_json):
    user.first_name = user_json.get("username")
    user.member.avatar = user_json.get("avatar")
    user.member.tag = user_json.get("discriminator")
    user.member.save()
    user.save()


@receiver(post_save, sender=Bot)
def create_bot_meta(sender, instance, created, **kwargs):
    if created:
        BotMeta.objects.create(bot=instance)
