import pandas as pd
pd.set_option('display.max_columns', None)
from google.auth import load_credentials_from_file
from google.cloud.bigquery import Client
from popularity import calculate_popularity_metrics
from category_filter import category_filter


# Loading data from BigQuery
def clean_data():
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


    # Joining and cleaning
    # Joining together tracks, artists, chart_positions and mapping table together
    # Will later on be joined with the audio_features once cleaned

    data = tracks.merge(mapping, on = 'track_id' )
    data = data.merge(artists, on = 'artist_id')
    data.rename(columns = {'name_x':'track_name', 'name_y':'artist'}, inplace = True)
    data = data.merge(chart_positions, on = 'track_id')
    data = data[['track_name', 'artist', 'duration_ms', 
                'release_date', 'popularity', 'followers',
                'chart_week', 'list_position', 'track_id', 'artist_id']]

    # Cleaning audio_features 
    # Cleaned seperately for better visiblility of columns
    # - Got rid of null values
    # - Rounded and changed datatype of tempo-column from float to int
    # - Dropped redundant time_signature column

    # Getting rid of null values
    audio_features = audio_features.dropna()

    # rounding and changing datatype of tempo to int
    audio_features['tempo'] = round(audio_features['tempo']).astype('int')

    # dropping redundant columns
    audio_features = audio_features.drop(columns = 'time_signature')


    # Cleaning previously joined together data
    # Changing track duration format from miliseconds to minutes
    data['duration_ms'] = round((data['duration_ms']/1000)/60,1)
    data = data.rename(columns = {'duration_ms':'duration_min'})

    # release_date to release_year
    data['release_date'] = data['release_date'].str[:4]
    data['release_date'] = pd.to_datetime(data['release_date'], format = '%Y')
    data['release_date'] = data['release_date'].dt.year
    data = data.rename(columns = {'release_date': 'release_year'})
    data['chart_week'] = pd.to_datetime(data['chart_week'], format='%Y-%m-%d')

    # Joining together data with audio_features
    data = data.merge(audio_features, on = 'track_id')
    data = data.drop(columns = 'Unnamed: 0', errors = 'ignore')

    # Filter out obvious christmas music
    data = data[~data['track_name'].str.contains("christmas")]

    # Removing duplicates and resetting index. Filtering for songs released in 2000-2009
    data = data.drop_duplicates()
    cleaned_data = data[data['release_year'] >= 2000]
    cleaned_data = category_filter(cleaned_data)

    cleaned_data = calculate_popularity_metrics(cleaned_data)
    # Ensure only one 'popularity' column is kept
    if 'popularity_x' in cleaned_data.columns and 'popularity_y' in cleaned_data.columns:
        cleaned_data['popularity'] = cleaned_data['popularity_y']  # Keep calculated popularity
        cleaned_data = cleaned_data.drop(columns=['popularity_x', 'popularity_y'], errors='ignore')
        
    return cleaned_data.drop_duplicates(subset="track_name", keep="first").reset_index(drop=True)