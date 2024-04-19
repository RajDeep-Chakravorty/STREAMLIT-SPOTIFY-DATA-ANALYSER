import streamlit as st
import pandas as pd
import altair as alt
import base64
import requests

# Set page configuration
st.set_page_config(
    page_title="Spotify Data Analyzer",
    page_icon="https://symbl-world.akamaized.net/i/webp/df/6766b8646eb16b761cb590d752e6b2.webp",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add the "Created By - RAJDEEP CHAKRAVORTY" text with fixed position relative to Streamlit interface
st.markdown(
    """
    <div style="position: fixed; top: 5px; right: 20px; z-index: 1000;">
        <div style="background-color: rgba(255, 255, 255, 0.7); color: red; padding: 5px; border-radius: 5px;">
            Created By - RAJDEEP CHAKRAVORTY
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)


# Define a function to set the background image from a URL
def set_background_image(image_url):
    # Use HTML/CSS to set the background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('{image_url}');
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the function with the URL of the image you want to use as the background
image_url = "https://i.postimg.cc/Y2Z8R7r2/spotify-gif-bg.gif"
set_background_image(image_url)

# Add space for logo and center align
st.markdown("<div style='text-align: center; padding-top: 20px; padding-bottom: 20px;'><img src='https://i.postimg.cc/9MJjbxSG/148-1487614-spotify-logo-small-spotify-logo-transparent-hd-png-removebg.png' width='300'></div>", unsafe_allow_html=True)

# Title and caption with text outline
st.markdown("<div style='text-align: center;'><h1 style='font-size: 55px; color: yellowgreen; font-weight: bold; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>Spotify Data Analyzer</h1><p style='font-size: 24px; color: magenta; font-weight: bold; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'><i>Where words fail, music speaks.</i></p></div>", unsafe_allow_html=True)

# Introduction and instructions section
st.markdown('''
<div style='text-align: center;'>
<h2 style='font-size: 40px; color: red; font-weight: bold; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>Introduction</h2>
<p style='font-size: 20px;color: white; font-weight: bold; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>Welcome to the Spotify Data Analyzer, an automatic web app designed to analyze your Spotify listening history. Simply upload your Spotify data, and get insightful visualizations!</p>

<h2 style='font-size: 40px; color: red; font-weight: bold; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>How to Request Your Spotify Data</h2>
<p style='font-size: 20px; color: white; font-weight: bold; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;'>Open this <a href="https://www.spotify.com/de/account/privacy/" target="_blank" style='color: #1DB954;'>link</a> and sign in to your Spotify account<br>
Scroll down, check the box for <code> Account</code><br>
Click on <code>Request</code><br>
You will receive a few files from Spotify. Take the one named <code>StreamingHistory</code><br>
Upload your data using the file uploader below<br>
Enjoy your insights!</p>
</div>
''', unsafe_allow_html=True)

# Define page options
pages = ["Analysis by Time", "Analysis by Artist and Song"]

# Tabs for selecting page
selected_page = st.radio("Select Analysis Type", pages)

# If "Analysis by Time" page is selected
if selected_page == "Analysis by Time":
    # Ask the user to upload a JSON file
    uploaded_file = st.file_uploader("Upload your Spotify data JSON file", type="json")

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
        st.altair_chart(fig3, use_container_width=True)

        # Create a histogram with the data from the "Month bin" column
        st.subheader("Your Music Listening Habits by Month")
        st.write("Explore which months you listen to music the most.")
        fig1 = alt.Chart(df).mark_bar().encode(
            alt.X("month bin", bin=alt.Bin(step=1), title="Month of the Year"),
            alt.Y("sum(Playtime in hours)", title="Total Playtime (hours)")
        ).properties(width=850, height=400)
        st.altair_chart(fig1, use_container_width=True)

        # Create a histogram with the data from the "Time bin" column
        st.subheader("Your Music Listening Habits by Time of Day")
        st.write("Explore which hours of the day you listen to music the most.")
        fig0 = alt.Chart(df).mark_bar().encode(
            alt.X("Time bin", bin=alt.Bin(step=1), title="Hour of the Day"),
            alt.Y("sum(Playtime in hours)", title="Total Playtime (hours)")
        ).properties(width=850, height=400)
        st.altair_chart(fig0, use_container_width=True)

    else:
        st.info("Please upload a Spotify data file to analyze or go ahead with the example file provided!")

# If "Analysis by Artist and Song" page is selected
elif selected_page == "Analysis by Artist and Song":
    # Ask the user to upload a JSON file
    uploaded_file = st.file_uploader("Upload your Spotify data JSON file", type="json")

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
        st.altair_chart(chart, use_container_width=True)

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
        st.altair_chart(chart, use_container_width=True)

    else:
        st.info("Please upload a Spotify data file to analyze or go ahead with the example file provided!")


st.markdown('''
    #### Interested what your data could look like? Download my example file from the below link and try it yourself!
''')

# Load Json
with open("spotify_data_example.json", "r") as f:
    data = f.read()

# Convert to base64
b64 = base64.b64encode(data.encode()).decode()

# Create DL-Link
href = f'<a href="data:file/json;base64,{b64}" download="spotify_data_example.json">Download example spotify data json file</a>'

# Import Dl-Link
st.markdown(href, unsafe_allow_html=True)
