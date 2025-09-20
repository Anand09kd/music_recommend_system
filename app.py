import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import os

# ------------------- Spotify Client -------------------
CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# ------------------- Load Similarity -------------------
def load_similarity():
    similarity = []
    parts = ["similarity_part_1.pkl", "similarity_part_2.pkl"]  # 2 parts

    for part_file in parts:
        if os.path.exists(part_file):
            with open(part_file, "rb") as f:
                similarity_part = pickle.load(f)
                # Ensure each part is a list of rows (convert if it's numpy array)
                if isinstance(similarity_part, np.ndarray):
                    similarity_part = similarity_part.tolist()
                similarity.extend(similarity_part)
        else:
            st.warning(f"{part_file} missing! Skipping...")

    return similarity

similarity = load_similarity()

# ------------------- Load Music Dataset -------------------
try:
    music = pickle.load(open('df.pkl', 'rb'))
except FileNotFoundError:
    st.error("Music dataset not found!")
    music = None

if music is not None:
    # Fill missing similarity rows with zeros if needed
    while len(similarity) < len(music):
        similarity.append(np.zeros(len(music)))

# ------------------- Get Album Cover -------------------
def get_song_album_cover_url(song_name, artist_name):
    try:
        query = f"{song_name} {artist_name}"
        results = sp.search(q=query, type='track', limit=1)
        if results and results['tracks']['items']:
            track = results['tracks']['items'][0]
            return track["album"]["images"][0]["url"]
        else:
            return "https://i.postimg.cc/0QNxYz4V/social.png"
    except:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

# ------------------- Recommendation Function -------------------
def recommend(song):
    try:
        index = list(music_list).index(song)
    except ValueError:
        st.warning("Song not found in database!")
        return [], []

    if index >= len(similarity):
        st.warning("Similarity data missing for this song! Showing empty recommendations.")
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []

    for i in distances[1:6]:  # top 5 recommendations
        song_index = i[0]
        recommended_music_names.append(music_list[song_index])
        recommended_music_posters.append(
            get_song_album_cover_url(music_list[song_index], music['artist'].iloc[song_index])
        )

    return recommended_music_names, recommended_music_posters

# ------------------- Streamlit Interface -------------------
st.header('🎵 Music Recommender System')

if music is not None:
    music_list = music['song'].values
    selectsong = st.selectbox("Type or select a song from the dropdown", music_list)

    if st.button("Show Recommendation"):
        recommended_music_names, recommended_music_posters = recommend(selectsong)
        if recommended_music_names:
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                col.text(recommended_music_names[idx])
                col.image(recommended_music_posters[idx])
        else:
            st.info("No recommendations available for this song.")
