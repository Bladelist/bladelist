from datetime import datetime
from django.contrib.auth.models import User
from main_site.models import Member

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
                          )
    return user
