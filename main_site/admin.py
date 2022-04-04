from django.contrib import admin
from .models import (
    Member, Bot, BotMeta, BotTag, MemberMeta, BotVote, BotReport,
    Server, ServerVote, ServerTag, ServerReport, ServerMeta
)


class BotFilter(admin.ModelAdmin):
    list_display = ("name", "date_added", "verified")
    list_filter = ("banned",)


admin.site.register(Member)
admin.site.register(Bot, BotFilter)
admin.site.register(BotMeta)
admin.site.register(BotTag)
admin.site.register(MemberMeta)
admin.site.register(BotVote)
admin.site.register(BotReport)
admin.site.register(Server)
admin.site.register(ServerTag)
admin.site.register(ServerReport)
admin.site.register(ServerVote)
admin.site.register(ServerMeta)
