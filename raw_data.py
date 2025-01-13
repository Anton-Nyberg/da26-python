import pandas as pd
pd.set_option('display.max_columns', None)
from google.auth import load_credentials_from_file
from google.cloud.bigquery import Client


# Loading data from BigQuery
credentials, project_id = load_credentials_from_file('key.json')

# Load data from BigQuery
client = Client(
    project = project_id,
    credentials=credentials
)

query = "SELECT * FROM `da26-python.music_data.tracks`"

load_job = client.query(query)
data = load_job.to_dataframe()

def load_data(table):
    query = f"SELECT * FROM `da26-python.music_data.{table}`"
    load_job = client.query(query)
    data = load_job.to_dataframe()
    return data


artists = load_data('artists')
audio_features = load_data('audio_features')
chart_positions = load_data('chart_positions')
mapping = load_data('tracks_artists_mapping')
tracks = load_data('tracks')

data = tracks.merge(mapping, on = 'track_id' )
data = data.merge(artists, on = 'artist_id')
data = data.merge(chart_positions, on = 'track_id')
data = data.merge(audio_features, on = 'track_id')

raw_data = data

raw_data.to_csv('raw_data.csv')