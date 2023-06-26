import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
import json
import pandas as pd

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

# Fetch a protected resource, i.e. user profile
#r = spotify.get('https://api.spotify.com/v1/me/player/recently-played')

tracksToSearch = pd.read_csv('tracksToSearch.csv')

x = ",".join(tracksToSearch['id'])

r = spotify.get('https://api.spotify.com/v1/audio-features?ids=' + x)

# Writing to sample.json
with open("trackFeatures.json", "w") as outfile:
    json.dump(r.json(),outfile)

