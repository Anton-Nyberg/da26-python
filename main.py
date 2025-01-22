import streamlit as st
import pandas as pd
import spotipy
import os
import requests
import base64
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from clean_data import clean_data
load_dotenv()

# Set page configuration (must be first Streamlit command)
st.set_page_config(
    layout="wide",
    page_title="Party Cruise Dashboard",
    page_icon="🚢"
)

# Load the dataset with caching
@st.cache_resource
def load_data():
    return clean_data()

# Setup Spotify client with caching
@st.cache_resource
def setup_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv('client_id'),
        client_secret=os.getenv('client_secret'),
        redirect_uri='http://localhost:8080/callback',
        scope="playlist-modify-public playlist-modify-private ugc-image-upload"
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
    
    # Add tracks to the playlist
    for i in range(0, len(tracks), 100):
        batch = tracks[i:i+100]
        spotify_client.playlist_add_items(playlist['id'], batch)
    
    # GitHub raw file URL for the image
    github_image_url = "https://raw.githubusercontent.com/Anton-Nyberg/da26-python/main/Party_cruise_Medium.jpeg"
    
    try:
        # Fetch the image from GitHub
        response = requests.get(github_image_url)
        response.raise_for_status()  # Raise an error if the request fails
        
        # Encode the image in Base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        # Upload the image to Spotify
        spotify_client.playlist_upload_cover_image(playlist['id'], image_data)
    except requests.RequestException as e:
        print(f"Failed to fetch the image from GitHub: {e}")
    except Exception as e:
        print(f"An error occurred while uploading the image: {e}")
    
    return playlist['external_urls']['spotify']

def main():
    st.title(":tada: Party Cruise Music Dashboard :ship:")

    # Load and preprocess data
    data = load_data()

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
    ].sort_values(by="vibe_score", ascending=False)

    # Sidebar playlist dropdown
    music_type = st.sidebar.selectbox(
        "Select playlist",
        ("Relaxing", "Dance", "Lounge", "Acoustic", "Energetic")
    )

    mode = music_type.lower()
    music_filtered = filter_music(final_data, mode)
    music_filtered = music_filtered.reset_index(drop=True)
    music_filtered['y_axis=1'] = 1

    # Calculate averages for sidebar
    if not music_filtered.empty:
        avg_tempo = int(round(music_filtered["tempo"].mean(),0))
        avg_energy = music_filtered["energy"].mean()
        avg_valence = music_filtered["valence"].mean()
        avg_danceability = music_filtered["danceability"].mean()
        avg_acousticness = music_filtered["acousticness"].mean()

        # Display averages in the sidebar
        st.sidebar.markdown("## Average Characteristics")
        st.sidebar.write(f"*Tempo:* {avg_tempo} BPM")
        st.sidebar.write(f"*Energy:* {avg_energy:.2f}")
        st.sidebar.write(f"*Valence:* {avg_valence:.2f}")
        st.sidebar.write(f"*Danceability:* {avg_danceability:.2f}")
        st.sidebar.write(f"*Acousticness:* {avg_acousticness:.2f}")
    else:
        st.sidebar.markdown("### Average Characteristics")
        st.sidebar.write("No data available for selected mode.")

    if music_filtered.empty:
        st.error("No tracks to export. Please generate a playlist first.")
    else:
        # Create two columns for layout
        col1, col2 = st.columns([3, 2])  # Adjust widths: col1 for table, col2 for bar chart
        
        # Display filtered table in the left column (reset index to avoid graying out)
        with col1:
            st.write(
                music_filtered[[
                    "track_name", "artist", "duration_min", "release_year", "vibe_score", "popularity", "weeks_on_chart", "highest_position"]]
            )

        # Display bar chart in the right column
        with col2:
            avg_data = music_filtered[[
                "danceability", "energy", "valence", "acousticness", "instrumentalness", "speechiness", 'y_axis=1'
            ]].mean()
            st.bar_chart(avg_data)

        # Export button
        if st.button("Export to Spotify"):
            track_ids = music_filtered.reset_index()['track_id'].tolist()
            playlist_url = export_to_spotify(spotify_client, track_ids, mode=mode)
            st.success(f"Playlist created! [Open Playlist]({playlist_url})")

if __name__ == "__main__":
    main()