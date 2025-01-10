final_data["Peaceful_lounge_music"] = (
    (final_data["danceability"].between(0.2, 0.6)) &
    (final_data["tempo"] < 110) &
    (final_data["energy"].between(0.1, 0.4)) &
    (final_data["speechiness"] < 0.3)
).astype(int)
lounge_and_peaceful_music = final_data[final_data["Peaceful_lounge_music"] == 1]
lounge_and_peaceful_music_unique = lounge_and_peaceful_music.drop_duplicates(subset="name_y", keep='first')