import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Assuming your data is loaded here
final_data = pd.read_csv("cleaned_data.csv")

# Setup Spotify client
def setup_spotify_client():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='YOUR_CLIENT_ID',
                                                   client_secret='YOUR_CLIENT_SECRET',
                                                   redirect_uri='YOUR_REDIRECT_URI',
                                                   scope="playlist-modify-public playlist-modify-private"))
    return sp

spotify_client = setup_spotify_client()

def export_to_spotify(spotify_client, tracks, playlist_name="My Party Cruise Playlist"):
    user_id = spotify_client.current_user()['id']
    playlist = spotify_client.user_playlist_create(user_id, playlist_name, public=True)
    spotify_client.playlist_add_items(playlist['id'], tracks)
    return playlist['external_urls']['spotify']

def filter_music(data, mode):
    # Ensure this function is defined in the global scope, not nested inside another function
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
            (data['loudness'] < -10) &
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
    elif mode == "energetic_workout":
        condition = (
            (data["energy"] > 0.8))  # Example condition
    filtered_data = data[condition]
    return filtered_data.drop_duplicates(subset="track_name", keep="first")


def main():
    st.title("Party Cruise Music Dashboard")

    music_type = st.sidebar.selectbox(
        "Select playlist",
        ("Peaceful Lounge", "Acoustic", "Relaxing", "Energetic_Workout", "Dancing")
    )

    if st.button(f"Show {music_type} Music"):
        mode = music_type.lower().replace(" ", "_")
        music_filtered = filter_music(final_data, mode)
        st.write(music_filtered[["track_name", "artist", "popularity"]])

        if not music_filtered.empty:
            avg_data = music_filtered[["danceability", "energy", "speechiness"]].mean()
            st.bar_chart(avg_data)
    
    # Export to Spotify button
    if st.button("Export to Spotify"):
        if not music_filtered.empty:
            track_ids = music_filtered['track_id'].tolist()  # collecting the track_id
            playlist_url = export_to_spotify(spotify_client, track_ids)
            st.success(f"Playlist created! [Open Playlist]({playlist_url})")
        else:
            st.error("No tracks to export. Please generate a playlist first.")

if __name__ == "__main__":
    main()

