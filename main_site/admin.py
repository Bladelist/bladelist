from django.contrib import admin
from .models import Member, Bot, BotMeta, Tag, MemberMeta, Vote

admin.site.register(Member)
admin.site.register(Bot)
admin.site.register(BotMeta)
admin.site.register(Tag)
admin.site.register(MemberMeta)
admin.site.register(Vote)