def category_filter(data):
    data["relaxing"] = (
        (data["energy"] <= 0.5) &
        (data["tempo"] <= 100) &
        (data["acousticness"] >= 0.6) &
        (data["valence"] <= 0.5) &
        (data["danceability"] <= 0.6)
    ).astype('boolean')

    data["dance"] = (
        (data["danceability"].between(0.75, 1)) &
        (data["tempo"].between(100, 140)) &
        (data["energy"].between(0.7, 1)) &
        (data["valence"].between(0.6, 1)) &
        (data["loudness"].between(-6, 0)) &
        (data["acousticness"].between(0.0, 0.3)) &
        (data["instrumentalness"].between(0.0, 0.5))
    ).astype('boolean')

    data["lounge"] = (
        (data["danceability"].between(0.2, 0.6)) &
        (data["tempo"] < 110) &
        (data["energy"].between(0.1, 0.4)) &
        (data["speechiness"] < 0.3)
    ).astype('boolean')

    data["acoustic"] = (
        (data["acousticness"] > 0.8) &
        (data["energy"] <= 0.5) &
        (data["tempo"] <= 100)
    ).astype('boolean')

    data["energetic"] = (
        (data["energy"] > 0.8) &
        (data["tempo"] >= 120) &
        (data["danceability"] >= 0.6) &
        (data["valence"] >= 0.6)
    ).astype('boolean')

    data["Vibe_Score"] = (
    0.2 * data["danceability"] +
    0.2 * data["energy"] +
    0.05 * data["key"] +
    0.15 * data["loudness"] +
    0.1 * data["mode"] +
    0.05 * data["speechiness"] +
    0.05 * data["acousticness"] +
    0.05 * data["instrumentalness"] +
    0.05 * data["liveness"] +
    0.1 * data["valence"] +
    0.1 * data["tempo"]
    )
    
    # Normalize Vibe Score to a 0-1 range
    vibe_min = data["Vibe_Score"].min()
    vibe_max = data["Vibe_Score"].max()
    data["Vibe_Score"] = round((data["Vibe_Score"] - vibe_min) / (vibe_max - vibe_min),2)
    return