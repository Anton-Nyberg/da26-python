import pandas as pd

# Load the dataset
file_path = 'metrics_merged_tracks_audio_features.csv'
data = pd.read_csv(file_path)

# Step 1: Only keep the relevant columns
columns_to_keep = ['name', 'release_date', 'energy', 'liveness', 'tempo', 'valence', 'mode', 
                   'key', 'loudness', 'danceability', 'track_id']
data_cleaned = data[columns_to_keep]

# Step 2: Filter tracks with release dates between 2000 and 2024
data_cleaned.loc[:, 'release_date'] = pd.to_numeric(data_cleaned['release_date'], errors='coerce')  # Ensure numeric values
filtered_data = data_cleaned[(data_cleaned['release_date'] >= 2000) & (data_cleaned['release_date'] <= 2024)]

# Step 3: Remove decimals from the release year by converting to integer
filtered_data.loc[:, 'release_date'] = filtered_data['release_date'].astype(int)

# Step 4: Add a new column to mark energetic tracks (energy > 0.7)
energy_threshold = 0.7
filtered_data.loc[:, 'is_energetic'] = (filtered_data['energy'] > energy_threshold).astype(int)

# Step 5: Keep only the final set of relevant columns
final_columns = ['liveness', 'tempo', 'valence', 'mode', 'energy', 
                 'key', 'loudness', 'danceability', 'release_date', 
                 'name', 'track_id', 'is_energetic']

# Check if all required columns exist
missing_columns = [col for col in final_columns if col not in filtered_data.columns]
if missing_columns:
    print(f"Warning: Missing columns in the dataset: {missing_columns}")
final_data = filtered_data[[col for col in final_columns if col in filtered_data.columns]]

# Display the final cleaned data as a table (useful for Jupyter Notebook)
from IPython.display import display
display(final_data.head())

# Optional: Save the final cleaned dataset to a CSV file
final_data.to_csv('final_filtered_energetic_tracks.csv', index=False)
