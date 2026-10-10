import streamlit as st
import pandas as pd

st.title("Hello World")

data = pd.read_csv("player_profiles.csv")
st.write(data.head(10))