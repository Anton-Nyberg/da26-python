import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from category_filter import category_filter
from clean_data import clean_data

# Load the dataset with caching
@st.cache_resource
def load_data():
    return clean_data()

st.set_page_config(layout="wide")

# Setup Spotify client with caching
@st.cache_resource
def setup_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id='your_client_id',
        client_secret='your_client_secret',
        redirect_uri='http://localhost:8080/callback',
        scope="playlist-modify-public playlist-modify-private"
    ))

# Cache Spotify client
spotify_client = setup_spotify_client()

def filter_music(data, mode):
    if mode not in data.columns:
        raise ValueError(f"Invalid mode: {mode}. Ensure that 'category_filter' is applied first.")
    filtered_data = data[data[mode]]
    return filtered_data

def export_to_spotify(spotify_client, tracks, playlist_name=None, mode=None):
    if playlist_name is None:
        playlist_name = f"My {mode.capitalize()} Playlist"
    user_id = spotify_client.current_user()['id']
    playlist = spotify_client.user_playlist_create(user_id, playlist_name, public=True)
    for i in range(0, len(tracks), 100):
        batch = tracks[i:i+100]
        spotify_client.playlist_add_items(playlist['id'], batch)
    return playlist['external_urls']['spotify']

def main():
    st.title(":tada: Party Cruise Music Dashboard :ship:")

    # Load and preprocess data
    data = load_data()
    category_filter(data)

    st.title("Filter Songs by Release Year")

    # Get the min and max years from the data
    min_year = int(data['release_year'].min())
    max_year = int(data['release_year'].max())

    # Add a slider to select the year range
    year_range = st.slider(
        "Select Release Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)  # Default to full range
    )

    # Filter the data based on the selected range
    final_data = data[
        (data['release_year'] >= year_range[0]) & (data['release_year'] <= year_range[1])
    ].sort_values(by = "popularity", ascending = False)

    music_type = st.sidebar.selectbox(
        "Select playlist",
        ("Relaxing", "Dance", "Lounge", "Acoustic", "Energetic")
    )

    mode = music_type.lower()
    music_filtered = filter_music(final_data, mode)
    music_filtered = music_filtered.reset_index(drop=True)

    if music_filtered.empty:
        st.error("No tracks to export. Please generate a playlist first.")
    else:
        st.write(music_filtered[["track_name", "artist", "duration_min", "release_year", "popularity", "weeks_on_chart", "highest_position", "vibe_score"]])
        music_filtered['x_always_one'] = 1
        st.title(" "*50)
        avg_data = music_filtered[["danceability", "energy", "valence", "acousticness", "instrumentalness", "speechiness", "x_always_one"]].mean()
        st.bar_chart(avg_data)

        if st.button("Export to Spotify"):
            track_ids = music_filtered['track_id'].tolist()
            playlist_url = export_to_spotify(spotify_client, track_ids, mode=mode)
            st.success(f"Playlist created! [Open Playlist]({playlist_url})")

if __name__ == "__main__":
    main()