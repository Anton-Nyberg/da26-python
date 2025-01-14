data["dancing_music"] = (
    (data["danceability"].between(0.75, 1)) &
    (data["tempo"].between(100, 140)) &
    (data["energy"].between(0.7, 1)) &
    (data["valence"].between(0.6, 1)) &
    (data["loudness"].between(-6, 0)) &
    (data["acousticness"].between(0.0, 0.3)) &
    (data["instrumentalness"].between(0.0, 0.5))
).astype(int)
dancing_music = data[data["dancing_music"] == 1]
dancing_music_unique = dancing_music.drop_duplicates(subset="track_name", keep='first')