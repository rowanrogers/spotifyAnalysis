import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

class SpotifyClient:
    def __init__(self, token: str = None):

        load_dotenv()  # ideally this is called before the class is made as it's a bit sloppy here
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.auth_base_url = 'https://accounts.spotify.com/authorize'
        self.redirect_uri = 'https://localhost:8888/callback'
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.scope = "user-read-recently-played"
        self.token = token

    def __enter__(self):
        if self.token is not None:
            print("Token provided so no need to auth")
        else:
            oauth_session = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=self.redirect_uri)
            authorization_url, state = oauth_session.authorization_url(self.auth_base_url)
            print("Please go here and authorize:", )
            redirect_response = input(
                f"""Please go here and authorize: {authorization_url}
                    then paste the full  redirect URL here:
                """)

            self.token = oauth_session.fetch_token(
                self.token_url,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                authorization_response=redirect_response)
            if len(self.token) == 0 or self.token is None:
                raise Exception("Auth failed - after trying to get token it is still None or empty")

