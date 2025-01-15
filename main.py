import streamlit as st
import pandas as pd
import spotipy
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# Assuming your data is loaded here
data = pd.read_csv("cleaned_data.csv")

# Setup Spotify client
load_dotenv()
def setup_spotify_client():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        CLIENT_ID = os.getenv("client_id")
        CLIENT_SECRET = os.getenv("client_secret")
        REDIRECT_URI = os.getenv("redirect_uri")
        scope="playlist-modify-public playlist-modify-private"))
    return sp

spotify_client = setup_spotify_client()

def filter_music(data, mode):
    # Definitions for filtering based on mode
    if mode == "peaceful_lounge":
        condition = (
            (data["danceability"].between(0.2, 0.6)) &
            (data["tempo"] < 110) &
            (data["energy"].between(0.1, 0.4)) &
            (data["speechiness"] < 0.3)
        )
    elif mode == "acoustic":
        condition = data["acousticness"] > 0.8
    elif mode == "relaxing":
        condition = (
            (data['tempo'] >= 60) &
            (data['tempo'] <= 90) &
            (data['energy'] < 0.5) &
            (data['speechiness'] < 0.1330) &
            (data['instrumentalness'] > 0.5) 
        )
    elif mode == "dancing":
        condition = (
            (data["danceability"].between(0.75, 1)) &
            (data["tempo"].between(100, 140)) &
            (data["energy"].between(0.7, 1)) &
            (data["valence"].between(0.6, 1)) &
            (data["loudness"].between(-6, 0)) &
            (data["acousticness"].between(0.0, 0.3)) &
            (data["instrumentalness"].between(0.0, 0.5))
        )
    elif mode == "energetic":
        condition = (data["energy"] > 0.8)
    filtered_data = data[condition]
    return filtered_data.drop_duplicates(subset="track_name", keep="first")


def export_to_spotify(spotify_client, tracks, playlist_name=None, mode=None):
    if playlist_name is None:
        playlist_name = f"My {mode} Cruise Playlist"  # Use mode to set the playlist name if not provided
    user_id = spotify_client.current_user()['id']
    playlist = spotify_client.user_playlist_create(user_id, playlist_name, public=True)
    # Add tracks in batches of 100 because spotify have a limit
    for i in range(0, len(tracks), 100):
        batch = tracks[i:i+100]
        spotify_client.playlist_add_items(playlist['id'], batch)
    return playlist['external_urls']['spotify']


def main():
    st.title("Party Cruise Music Dashboard")
    final_data = pd.read_csv("cleaned_data.csv")  # Ensure this data is loaded properly

    music_type = st.sidebar.selectbox(
        "Select playlist",
        ("Peaceful Lounge", "Acoustic", "Relaxing", "Energetic", "Dancing")
    )

test
    mode = music_type.lower().replace(" ", "_")
    music_filtered = filter_music(final_data, mode)

    if music_filtered.empty:
        st.error("No tracks to export. Please generate a playlist first.")
    else:

    if st.button(f"Show {music_type} Music"):
        mode = music_type.lower().replace(" ", "_")
        music_filtered = filter_music(data, mode)

        st.write(music_filtered[["track_name", "artist", "popularity"]])
        avg_data = music_filtered[["danceability", "energy", "speechiness"]].mean()
        st.bar_chart(avg_data)

        if st.button("Export to Spotify"):
            track_ids = music_filtered['track_id'].tolist()
            playlist_url = export_to_spotify(spotify_client, track_ids, mode=mode)
            st.success(f"Playlist created! [Open Playlist]({playlist_url})")

if __name__ == "__main__":
    main()