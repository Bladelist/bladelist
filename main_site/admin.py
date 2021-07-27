from django.contrib import admin
from .models import Member, Bot, BotMeta, BotTag, MemberMeta, BotVote, BotReport

admin.site.register(Member)
admin.site.register(Bot)
admin.site.register(BotMeta)
admin.site.register(BotTag)
admin.site.register(MemberMeta)
admin.site.register(BotVote)
admin.site.register(BotReport)