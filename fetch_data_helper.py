import re
import json
import pandas as pd

def fetch_recently_played(output_file, spotify):
    '''
    Function to fetch recently played for a spotify user that has been validated with Oauth2. Returns a json with
    the track name, album, artists and other metadata.
    '''

    r = spotify.get('https://api.spotify.com/v1/me/player/recently-played')

    if not bool(re.search("\.json", output_file)):
        output_file += ".json"

    # Writing to sample.json
    with open(output_file, "w") as outfile:
        json.dump(r.json(), outfile)

    print("Raw output written successfully")

    # Select items from json and turn into dataframe
    raw_data = r.json()
    df = pd.DataFrame(raw_data['items'])

    # Normalize the track column to separate into multiple columns
    normalized_df = pd.json_normalize(df['track'])

    # Extract artists data (as there may be multiple artists per song), and merge with the track data
    artists_data = pd.concat({i: pd.json_normalize(x) for i, x in normalized_df.pop('artists').items()}) \
        .reset_index(level=1, drop=True)

    updated_df = normalized_df.join(artists_data, rsuffix='_artist')

    # select useful columns
    useful_cols = ['disc_number', 'duration_ms', 'id', 'name', 'popularity', 'track_number', 'type', 'album.album_type',
                   'album.name', 'album.release_date', 'album.release_date_precision', 'album.total_tracks',
                   'album.type',
                   'id_artist']

    tidied_data = updated_df[useful_cols]

    return tidied_data

def fetch_track_features(output_file, spotify, tracks_to_search):
    '''
    Function to fetch track features for a given set of IDs. The input (tracks_to_search) should be a pandas dataframe
    that has a column 'id' which contains the track IDs to fetch the features for. The output is written to a json file.
    '''
    x = ",".join(tracks_to_search['id'])

    r = spotify.get('https://api.spotify.com/v1/audio-features?ids=' + x)

    # Writing to sample.json
    with open(output_file, "w") as outfile:
        json.dump(r.json(), outfile)

    print("Output written successfully")

    features = r.json()
    features_df = pd.DataFrame(features['audio_features'])

    return features_df







