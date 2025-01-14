import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from release_year_filter import release_year_filter

# Assuming your data is loaded here
data = pd.read_csv("cleaned_data.csv")

release_year_filter()

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
        music_filtered = filter_music(data, mode)
        st.write(music_filtered[["track_name", "artist", "popularity"]])

        if not music_filtered.empty:
            avg_data = music_filtered[["danceability", "energy", "speechiness"]].mean()
            st.bar_chart(avg_data)
    

if __name__ == "__main__":
    main()