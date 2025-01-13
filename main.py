def filter_music(data, mode):
    # Creating the conditions for each playlist
    if mode == "Peaceful_lounge":
        condition = (
            (data["danceability"].between(0.2, 0.6)) &
            (data["tempo"] < 110) &
            (data["energy"].between(0.1, 0.4)) &
            (data["speechiness"] < 0.3)
        )
    elif mode == "acoustic":
        condition = (
            
        )
    elif mode == "relaxing":
        condition = (
            
        )
    elif mode == "dancing":
        condition = (
            
        )
    elif mode == "energetic_workout":
        condition = (
            
        )
    filtered_data = data[condition]
    return filtered_data.drop_duplicates(subset="title", keep="first")