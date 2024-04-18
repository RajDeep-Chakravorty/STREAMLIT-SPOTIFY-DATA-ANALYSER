import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image
import base64

# Set page configuration
st.set_page_config(
    page_title="Spotify Data Analyzer",
    page_icon="https://symbl-world.akamaized.net/i/webp/df/6766b8646eb16b761cb590d752e6b2.webp",
    layout="wide",
    initial_sidebar_state="expanded"
)

import base64

def set_bg_from_file(image_path):
    '''
    A function to load an image from file and set it as the background.
    
    Parameters:
        image_path (str): The path to the image file on your system.
    
    Returns:
        The background.
    '''
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
            encoded_image = base64.b64encode(image_data).decode()
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background: url('data:image/png;base64,{encoded_image}');
                    background-size: cover;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"Error loading background image: {e}")

# Call the function to set background image
image_path ="D:\PROJECTS\END TO END DEPLOYMENT PROJECTS\STREAMLIT SPOTIFY DATA ANALYSER\background_image.png"# Replace with your image path
set_bg_from_file(image_path)

# Title and caption
st.title("Spotify Data Analyzer")
st.markdown("*Where words fail, music speaks.*")

# Image in the sidebar
image = Image.open("D:\PROJECTS\END TO END DEPLOYMENT PROJECTS\STREAMLIT SPOTIFY DATA ANALYSER\spotify_small.png")
st.sidebar.image(image, caption='Listening is everything')

# Introduction and instructions section
st.markdown('''
## Introduction
Welcome to the Spotify Data Analyzer, an automatic web app designed to analyze your Spotify listening history. Simply upload your Spotify data, and get insightful visualizations!

## How to Request Your Spotify Data
1. Open this [link](https://www.spotify.com/de/account/privacy/) and sign in to your Spotify account
2. Scroll down, check the box for "Account Data"
3. Click on "Request"
4. You will receive a few files from Spotify. Take the one named "StreamingHistory0"
5. Upload your data using the sidebar
6. Enjoy your insights! 
''')

st.markdown('''
#### Interested in what your data could look like? Download my example file and try it yourself!
''')

# Load example JSON data
with open("D:\PROJECTS\END TO END DEPLOYMENT PROJECTS\STREAMLIT SPOTIFY DATA ANALYSER\spotify_data_example.json", "r") as f:
    data = f.read()

# Convert to base64
b64 = base64.b64encode(data.encode()).decode()

# Create download link
href = f'<a href="data:file/json;base64,{b64}" download="spotify_data_example.json">Download example Spotify data JSON file</a>'
st.markdown(href, unsafe_allow_html=True)

# Define page options
pages = ["Analysis by Time", "Analysis by Artist and Song"]

# Sidebar to select analysis type
selected_page = st.sidebar.radio("Select Analysis Type", pages)

# If "Analysis by Time" page is selected
if selected_page == "Analysis by Time":
    # Ask the user to upload a JSON file
    uploaded_file = st.sidebar.file_uploader("", type="json")

    # If the user uploads a file, process it and display the results
    if uploaded_file is not None:
        # Read the JSON file into a pandas dataframe
        df = pd.read_json(uploaded_file)

        # Change column names
        df.columns = ["Date and Time", "Artist", "Song title", "Playtime"]

        # Apply functions to the Playtime column and create new columns
        df["Playtime in hours"] = df["Playtime"] / 3600000
        df["Playtime in minutes"] = df["Playtime"] / 60000

        # Convert the "Date and Time" column to datetime
        df["Date and Time"] = pd.to_datetime(df["Date and Time"])

        # Create a new column "Time bin" containing only the hour information
        df["Time bin"] = df["Date and Time"].dt.hour

        # Group by "Time bin" and sum the "Playtime" column
        grouped_time_df = df.groupby("Time bin")["Playtime"].sum()

        # Convert the data to datetime format
        df['month bin'] = pd.to_datetime(df['Date and Time'])

        # Define bins for months
        bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        # Create a new column for month
        df['month bin'] = df['Date and Time'].dt.month

        # Group by month and sum playtime in hours
        grouped = df.groupby(pd.cut(df['month bin'], bins=bins))['Playtime in hours'].sum()

        # Set DateTime column as index
        df.index = pd.to_datetime(df['Date and Time'])

        # Group by weekday and sum Playtime in Hours
        grouped = df.groupby(df.index.weekday)['Playtime in hours'].sum()

        # Rename weekdays
        grouped.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Create a new column "weekday" based on the "Date and Time" column
        df['weekday'] = df['Date and Time'].dt.day_name()

        # Create a bar chart with the data from the "weekday" column
        st.subheader("Your Music Listening Habits by Weekday")
        st.write("Explore when you listen to music the most.")
        fig3 = alt.Chart(df).mark_bar(size=105).encode(
            alt.X("weekday", sort=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                  title="Day of the Week", axis=alt.Axis(labelAngle=0)),
            alt.Y("sum(Playtime in hours)", title="Total Playtime (hours)")
        ).properties(width=850, height=370)
        st.altair_chart(fig3)

        # Create a histogram with the data from the "Month bin" column
        st.subheader("Your Music Listening Habits by Month")
        st.write("Explore which months you listen to music the most.")
        fig1 = alt.Chart(df).mark_bar().encode(
            alt.X("month bin", bin=alt.Bin(step=1), title="Month of the Year"),
            alt.Y("sum(Playtime in hours)", title="Total Playtime (hours)")
        ).properties(width=850, height=400)
        st.altair_chart(fig1)

        # Create a histogram with the data from the "Time bin" column
        st.subheader("Your Music Listening Habits by Time of Day")
        st.write("Explore which hours of the day you listen to music the most.")
        fig0 = alt.Chart(df).mark_bar().encode(
            alt.X("Time bin", bin=alt.Bin(step=1), title="Hour of the Day"),
            alt.Y("sum(Playtime in hours)", title="Total Playtime (hours)")
        ).properties(width=850, height=400)
        st.altair_chart(fig0)

    else:
        st.info("Please upload a Spotify data file to analyze.")


# If "Analysis by Artist and Song" page is selected
elif selected_page == "Analysis by Artist and Song":
    # Ask the user to upload a JSON file
    uploaded_file = st.sidebar.file_uploader("", type="json")

    # If the user uploads a file, process it and display the results
    if uploaded_file is not None:
        # Read the JSON file into a pandas dataframe
        df = pd.read_json(uploaded_file)

        # Change column names
        df.columns = ["Date and Time", "Artist", "Song title", "Playtime"]

        # Apply functions to the Playtime column and create new columns
        df["Playtime in hours"] = df["Playtime"] / 3600000

        # Group by Artist and sum Playtime columns
        grouped_artist_df = df.groupby("Artist")[["Playtime", "Playtime in hours"]].sum()

        # Group by Song title and sum Playtime columns
        grouped_song_df = df.groupby("Song title")[["Playtime", "Playtime in hours"]].sum()

        # Sort by Playtime in minutes descending and get the top 50 rows
        sorted_artist_df = grouped_artist_df.sort_values("Playtime in hours", ascending=False).head(50)
        sorted_song_df = grouped_song_df.sort_values("Playtime in hours", ascending=False).head(50)

        # Display the top artists based on the selected number
        num_top_artists = st.slider("Select the number of top artists to display:", 5, 50, 10, 5)
        st.subheader(f"Top {num_top_artists} Streamed Artists")
        top_artists_df = sorted_artist_df.head(num_top_artists)
        st.dataframe(top_artists_df.style.format(precision=0))
        st.write("Top Artists Visualized")
        chart = alt.Chart(top_artists_df.reset_index()).mark_bar().encode(
            y=alt.Y("Artist", sort="-x"),
            x="Playtime in hours"
        )
        st.altair_chart(chart)

        # Display the top songs based on the selected number
        num_top_songs = st.slider("Select the number of top songs to display:", 5, 50, 10, 5)
        st.subheader(f"Top {num_top_songs} Streamed Songs")
        top_songs_df = sorted_song_df.head(num_top_songs)
        st.dataframe(top_songs_df.style.format(precision=0))
        st.write("Top Songs Visualized")
        chart = alt.Chart(top_songs_df.reset_index()).mark_bar().encode(
            y=alt.Y("Song title", sort="-x", axis=alt.Axis(labelLimit=150)),
            x="Playtime in hours"
        )
        st.altair_chart(chart)

    else:
        st.info("Please upload a Spotify data file to analyze.")

else:
    st.markdown('''
    ## Introduction
    Welcome to the Spotify Data Analyzer, an automatic web app designed to analyze your Spotify listening history. Simply upload your Spotify data, and get insightful visualizations!

    ## How to Request Your Spotify Data
    1. Open this [link](https://www.spotify.com/de/account/privacy/) and sign in to your Spotify account
    2. Scroll down, check the box for "Account Data"
    3. Click on "Request"
    4. You will receive a few files from Spotify. Take the one named "StreamingHistory0"
    5. Upload your data using the sidebar
    6. Enjoy your insights! 
    ''')

    st.markdown('''
    #### Interested in what your data could look like? Download my example file and try it yourself!
    ''')

    # Load example JSON data
    with open("D:\PROJECTS\END TO END DEPLOYMENT PROJECTS\STREAMLIT SPOTIFY DATA ANALYSER\spotify_data_example.json", "r") as f:
        data = f.read()

    # Convert to base64
    b64 = base64.b64encode(data.encode()).decode()

    # Create download link
    href = f'<a href="data:file/json;base64,{b64}" download="spotify_data_example.json">Download example Spotify data JSON file</a>'
    st.markdown(href, unsafe_allow_html=True)
