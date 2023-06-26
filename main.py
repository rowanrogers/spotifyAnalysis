import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

load_dotenv()

authorization_base_url = 'https://accounts.spotify.com/authorize'
redirect_uri = 'https://localhost:8888/callback'
token_url = 'https://accounts.spotify.com/api/token'
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
scope = "user-read-recently-played"

spotify = OAuth2Session(CLIENT_ID, scope=scope, redirect_uri=redirect_uri)

# Redirect user to Spotify for authorization
authorization_url, state = spotify.authorization_url(authorization_base_url)
print('Please go here and authorize: ', authorization_url)

# Get the authorization verifier code from the callback url
redirect_response = input('\n\nPaste the full redirect URL here: ')
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

# Fetch the access token
token = spotify.fetch_token(token_url, auth=auth,
                            authorization_response=redirect_response)
print(token)


