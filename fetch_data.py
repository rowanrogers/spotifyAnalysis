from fetch_data_helper import fetch_recently_played, fetch_track_features
from main import spotify

# File names and output folder
data_folder = "data_raw"
recently_played_file = "recently_played_test.json"
track_features_file = "track_features_test.json"
full_data_file = "final_data.csv"

# Fetch the recently played data and format
recently_played = fetch_recently_played(data_folder + "/" + recently_played_file, spotify)
# Fetch the track features of recently played
track_features = fetch_track_features(data_folder + "/" + track_features_file, spotify, recently_played)

full_data = recently_played.merge(track_features, on=['id', 'duration_ms'])

full_data.to_csv(data_folder + '/' + full_data_file)




