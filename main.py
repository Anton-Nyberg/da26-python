def main():
    st.title("Party cruise music dashboard")

    final_data = pd.dataframe() # change this to the actual data when its ready
    # Adding the buttons to the sidebar 
    Music_type = st.sidebar.selectbox(
        "Select playlist",
        ("Peaceful Lounge", "Acoustic", "Relaxing", "Energetic/Workout", "Dancing")
    )

    if st.button(F"Show {"music_type"} Music"):
        mode = music_type.lower().replace(" ", "_")
        filtered_music = filtered_music(final_data, mode)
        # Selecting what columns we want to have displayed in the result
        st.write(filtered_music[["title", "artist", "popularity", "duration", "vibe_score"]])

        if not filtered_music.empty:
            # Creating the bar chart with information about the list
            avg_data = filtered_music[["danceability", "energy", "tempo", "speechiness"]].mean()
            st.bar_chart(avg_data)

            song_name = st.selectbox("Select a song to see details": filtered_music["title"].unique())
            if song_name:
                song_details = filtered_music[filtered_music["title"] == song_name]
                st.write(song_details)

if __main__ == "__main__":
    main()