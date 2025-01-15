import streamlit as st

def release_year_filter(data):
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
    ]
    return final_data

    # Display the filtered data
    #st.write("Filtered Songs:")
    #st.dataframe(filtered_data)