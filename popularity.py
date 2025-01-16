import pandas as pd

def calculate_popularity_metrics(data):
    # Ensure necessary columns are present
    required_columns = {'track_id', 'chart_week', 'list_position', 'followers'}
    if not required_columns.issubset(data.columns):
        raise ValueError(f"Dataset is missing one or more required columns: {required_columns}")

    # Calculate cumulative weeks on chart
    weeks_on_chart = data.groupby('track_id')['chart_week'].nunique().reset_index()
    weeks_on_chart.columns = ['track_id', 'weeks_on_chart']

    # Calculate highest chart position
    highest_position = data.groupby('track_id')['list_position'].min().reset_index()
    highest_position.columns = ['track_id', 'highest_position']

    # Merge metrics into the dataset
    metrics_data = data.merge(weeks_on_chart, on='track_id', how='left').merge(
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
    metrics_data['popularity'] = round(
        weights['followers'] * metrics_data['normalized_followers'] +
        weights['weeks'] * metrics_data['normalized_weeks'] +
        weights['position'] * metrics_data['normalized_position']
    ,2)

    # Assign calculated metrics back to the original dataset
    data = data.merge(
        metrics_data[['track_id', 'weeks_on_chart', 'highest_position', 'popularity']].drop_duplicates(),
        on='track_id',
        how='left'
    )

    return data