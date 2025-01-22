import pandas as pd

# Load dataset
merged_data = pd.read_csv('merged_datasets_for_popularity.csv')

# Drop duplicate rows
merged_data = merged_data.drop_duplicates()

# Parse release_date and filter tracks by release date (2000-2024)
merged_data['release_date'] = pd.to_datetime(merged_data['release_date'], errors='coerce')
filtered_data = merged_data[(merged_data['release_date'].dt.year >= 2000) & (merged_data['release_date'].dt.year <= 2024)]

# Calculate cumulative weeks on chart
filtered_data['chart_week'] = pd.to_datetime(filtered_data['chart_week'], errors='coerce')
weeks_on_chart = filtered_data.groupby('track_id')['chart_week'].nunique().reset_index()
weeks_on_chart.columns = ['track_id', 'weeks_on_chart']

# Calculate highest chart position
highest_position = filtered_data.groupby('track_id')['list_position'].min().reset_index()
highest_position.columns = ['track_id', 'highest_position']

# Merge metrics into the dataset
metrics_data = filtered_data.merge(weeks_on_chart, on='track_id', how='left').merge(
    highest_position, on='track_id', how='left'
)

# Fill missing values
metrics_data['weeks_on_chart'] = metrics_data['weeks_on_chart'].fillna(0)
metrics_data['highest_position'] = metrics_data['highest_position'].fillna(100)
metrics_data['followers'] = metrics_data['followers'].fillna(0)

# Normalize metrics
metrics_data['normalized_followers'] = metrics_data['followers'] / metrics_data['followers'].max()
metrics_data['normalized_weeks'] = metrics_data['weeks_on_chart'] / metrics_data['weeks_on_chart'].max()
metrics_data['normalized_position'] = 1 - (metrics_data['highest_position'] / 100)

# Calculate popularity score with weights
weights = {'followers': 0.5, 'weeks': 0.3, 'position': 0.2}
metrics_data['popularity_score'] = (
    weights['followers'] * metrics_data['normalized_followers'] +
    weights['weeks'] * metrics_data['normalized_weeks'] +
    weights['position'] * metrics_data['normalized_position']
)

# Rank tracks by popularity score
ranked_tracks = metrics_data.sort_values(by='popularity_score', ascending=False)

# Remove duplicate track_id entries, keeping the one with the highest popularity_score
ranked_tracks = ranked_tracks.drop_duplicates(subset='track_id', keep='first')

# Select relevant columns for output
ranked_tracks_output = ranked_tracks[['track_id', 'name_x', 'name_y', 'release_date', 'weeks_on_chart',
                                       'highest_position', 'followers', 'popularity_score']]
ranked_tracks_output.columns = ['Track ID', 'Track Name', 'Artist Name',
                                 'Release Date', 'Weeks on Chart', 'Highest Position',
                                 'Followers', 'Popularity Score']

# Save results to CSV
ranked_tracks_output.to_csv('ranked_tracks_2000_to_2024.csv', index=False)


