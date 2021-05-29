import requests
from django.conf import settings


class DiscordAPIClient:
    url = "https://discord.com/api/v8"
    headers = {"Authorization": f"Bot {settings.DISCORD_API_TOKEN}", "Content-Type": "application/json"}

    def get(self, endpoint):
        return requests.get(self.url+endpoint, headers=self.headers)

    def get_bot_info(self, bot_id):
        return self.get(f"/users/{bot_id}")
