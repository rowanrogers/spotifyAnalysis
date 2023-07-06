import os
import pandas as pd
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from pathlib import Path
from datetime import datetime
from helper import write_output

class SpotifyClient:
    def __init__(self, data_folder: Path = None):
        """
        Init SpotifyClient to handle authentication to spotify APIs
        #:param auth_token: Oauth2 token if it already exists, default None
        :param data_folder: file path to fetch data, Default path is "./data-raw"
                            Created if it doesn't exist
        """
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.auth_base_url = 'https://accounts.spotify.com/authorize'
        self.redirect_uri = 'https://localhost:8888/callback'
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.scope = "user-read-recently-played"
        self.data_folder = Path("./data_raw") if data_folder is None else data_folder
        self.oauth_session = None
    def __enter__(self):  # using this dunder method can be cleaner for doing some initial auth. __exit__ can then be used to "clean up" your auth, ie disconnect from a db

        print("Running auth flow to get API token")
        self.oauth_session = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=self.redirect_uri)
        authorization_url, state = self.oauth_session.authorization_url(self.auth_base_url)
        redirect_response = input(
            f"""Please go here and authorize: {authorization_url}
                then paste the full  redirect URL here:
                """)

        self.token = self.oauth_session.fetch_token(
            self.token_url,
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            authorization_response=redirect_response)
        if len(self.token) == 0 or self.token is None:
            raise Exception("Auth failed - after trying to get token it is still None or empty")
        return(self)

    def fetch_recently_played(self, output_file: str = None) -> pd.DataFrame:
        """
        Function to fetch recently played for a spotify user that has been
        validated with Oauth2. Returns a json with the track name, album,
        artists and other metadata.
        :param: output_file - file path to save the output too. Must be a json file
        :return: df of recently played tracks
        """

        r = self.oauth_session.get('https://api.spotify.com/v1/me/player/recently-played')

        if output_file is not None:
            write_output(json_object = r, output_file = output_file)

        # Select items from json and turn into dataframe
        raw_data = r.json()
        df = pd.DataFrame(raw_data['items'])

        # Normalize the track column to separate into multiple columns
        normalized_df = pd.json_normalize(df['track'])

        # Extract artists data (as there may be multiple artists per song), and merge with the track data
        artists_data = pd.concat({i: pd.json_normalize(x) for i, x in normalized_df.pop('artists').items()}) \
            .reset_index(level=1, drop=True)

        updated_df = normalized_df.join(artists_data, rsuffix='_artist')

        # Select useful columns
        useful_cols = ['disc_number', 'duration_ms', 'id', 'name', 'popularity', 'track_number', 'type',
                       'album.album_type',
                       'album.name', 'album.release_date', 'album.release_date_precision', 'album.total_tracks',
                       'album.type',
                       'id_artist']

        tidied_data = updated_df[useful_cols]

        return tidied_data


    def fetch_track_features(
            self,
            track_ids,  # note I've used `from typing import List`. if using python >=3.9 you can just use the built in type directly e.g. list[str]
            output_file: str = None
    ) -> pd.DataFrame:
        """
        Function to fetch track features for a given set of IDs.
        The input (tracks_to_search) should be a pandas dataframe
        that has a column 'id' which contains the track IDs to
        fetch the features for. The output is written to a json file.
        :return: df of track features
        """

        x = ",".join(track_ids)
        r = self.oauth_session.get('https://api.spotify.com/v1/audio-features?ids=' + x)

        if output_file is not None:
            write_output(json_object = r, output_file = output_file)

        features = r.json()
        features_df = pd.DataFrame(features['audio_features'])

        return features_df

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("DONE")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    today = datetime.today().strftime('%Y-%m-%d')
    with SpotifyClient() as sc:  # calling a class using the `with` terminology calls the `__enter__` dunder method of the class
        print(sc.token)
        tracks = sc.fetch_recently_played()
        track_ids = list(tracks['id'].unique())  # wrap in list() to match my type hint of List[str] because pandas returns as type np.ndarray.
        # doesn't actually matter much, could just typehint that
        track_feats = sc.fetch_track_features(track_ids=track_ids)

        full_data = tracks.merge(track_feats, on=['id', 'duration_ms'])
        full_data_file = 'final_results' + today + '.csv'
        full_data.to_csv('data_raw/' + full_data_file)
