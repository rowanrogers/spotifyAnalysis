import json
import pandas as pd

# Load recent listening tracks
with open('sample.json') as f:
    listening = json.load(f)

# Select items from json and turn into dataframe
df = pd.DataFrame(listening['items'])
normalized_df = pd.json_normalize(df['track'])

# Extract artists data (as there may be multiple artists per song), and merge with the track data
artists_data = pd.concat({i: pd.json_normalize(x) for i, x in normalized_df.pop('artists').items()})\
    .reset_index(level=1, drop=True)

updated_df = normalized_df.join(artists_data, rsuffix='_artist')

# select useful columns
useful_cols = ['disc_number', 'duration_ms', 'id', 'name', 'popularity', 'track_number', 'type', 'album.album_type',
              'album.name', 'album.release_date', 'album.release_date_precision', 'album.total_tracks', 'album.type',
              'id_artist']

tidied_data = updated_df[useful_cols]

#### Read in the musical features and add to the data
with open('trackFeatures.json') as f:
    features = json.load(f)
    features_df = pd.DataFrame(features['audio_features'])

full_data = tidied_data.merge(features_df, on = ['id', 'duration_ms'])

full_data.to_csv('fullData.csv')
