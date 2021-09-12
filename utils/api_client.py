import json

import requests
from django.conf import settings


class DiscordAPIClient:
    url = "https://discord.com/api/v8"
    headers = {"Authorization": f"Bot {settings.DISCORD_API_TOKEN}", "Content-Type": "application/json"}

    def get(self, endpoint):
        return requests.get(self.url+endpoint, headers=self.headers)

    def post(self, endpoint, data: dict):
        return requests.post(self.url + endpoint, headers=self.headers, json=data)

    def get_bot_info(self, bot_id):
        return self.get(f"/users/{bot_id}")

    def get_guild_info(self, guild_id):
        return self.get(f"/guilds/{guild_id}")

    def create_dm_channel(self, user_id):
        resp = self.post("/users/@me/channels", data={"recipient_id": user_id})
        if resp.status_code == 200:
            return resp.json().get("id")

    def send_message(self, channel_id, message: str):
        return self.post(f"/channels/{channel_id}/messages", data={"content": message})

    def send_embed(self, embed: dict, channel_id=settings.LOG_CHANNEL_ID):
        return self.post(f"/channels/{channel_id}/messages", data={"embed": embed})
