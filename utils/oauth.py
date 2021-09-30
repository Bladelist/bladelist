import requests
from django.conf import settings


class Oauth:
    redirect_uri = settings.AUTH_CALLBACK_URL
    discord_api_url = "https://discord.com/api/v8"
    client_id = settings.OAUTH_CLIENT_ID
    client_secret = settings.OAUTH_CLIENT_SECRET

    def __init__(self,
                 redirect_uri=settings.AUTH_CALLBACK_URL,
                 scope="identify%20guilds"
                 ):
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.discord_login_url = (
            f"https://discord.com/api/oauth2/authorize?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}&response_type=code&scope={self.scope}"
        )

    def post(self, endpoint, payload):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(url=self.discord_api_url+endpoint, data=payload, headers=headers)

    def get_token_json(self, code):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope
        }
        resp = self.post("/oauth2/token", payload=data)
        return resp.json()

    @staticmethod
    def get(access_token, endpoint):
        headers = {"Authorization": f"Bearer {access_token}"}
        response_object = requests.get(url=endpoint, headers=headers)
        return response_object.json()

    def get_user_json(self, access_token):
        url = f"{self.discord_api_url}/users/@me"
        return self.get(access_token, endpoint=url)

    def get_guild_info_json(self, access_token):
        url = f"{self.discord_api_url}/users/@me/guilds"
        return self.get(access_token, endpoint=url)

    def refresh_access_token(self, refresh_token):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        resp = self.post("/oauth2/token", payload=data)
        return resp.json()
