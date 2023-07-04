import os
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from pathlib import Path
import pandas as pd
from typing import List

class SpotifyClient:
    def __init__(self, auth_token: str = None, data_folder: Path = None):
        """
        Init SpotifyClient which handles authing to Spotify API with Oauth2 and
        exposes methods for fetching recently played tracks.
        :param auth_token: Oauth2 token if already exists, default None.
        :param data_folder: Local filepath to store fetched spotify data.
                            Default Path("./data_raw"). Created if doesn't exist
        """

        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.auth_base_url = 'https://accounts.spotify.com/authorize'
        self.redirect_uri = 'https://localhost:8888/callback'
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.scope = "user-read-recently-played"
        self.token = auth_token
        self.data_folder = Path("./data_raw") if data_folder is None else data_folder

    def __enter__(self):  # using this dunder method can be cleaner for doing some initial auth. __exit__ can then be used to "clean up" your auth, ie disconnect from a db
        if self.token is not None:  # I am actually not sure what the token is used for so maybe this logic isn't needed
            print("Token provided so no need to auth")
        else:
            print("Running auth flow to get API token")
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

    def fetch_recently_played(self) -> pd.DataFrame:
        """
        Function to fetch recently played for a spotify user that has been
        validated with Oauth2. Returns a json with the track name, album,
        artists and other metadata.
        :return: df of recently played tracks
        """
        # todo
        pass

    def fetch_track_features(
            self,
            track_ids: List[str]  # note I've used `from typing import List`. if using python >=3.9 you can just use the built in type directly e.g. list[str]
    ) -> pd.DataFrame:
        """
        Function to fetch track features for a given set of IDs.
        The input (tracks_to_search) should be a pandas dataframe
        that has a column 'id' which contains the track IDs to
        fetch the features for. The output is written to a json file.
        :return: df of track features
        """
        # todo
        pass


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    with SpotifyClient() as sc:  # calling a class using the `with` terminology calls the `__enter__` dunder method of the class
        tracks = sc.fetch_recently_played()
        track_ids = list(tracks['id'].unique())  # wrap in list() to match my type hint of List[str] because pandas returns as type np.ndarray. doesn't actually matter much, could just typehint that
        track_feats = sc.fetch_track_features(track_ids=track_ids)