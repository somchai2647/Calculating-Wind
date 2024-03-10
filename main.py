import streamlit as st
import pandas as pd
import numpy as np
from scipy import interpolate
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

import wind


st.set_page_config(page_title='แรงลม มยผ', layout='wide', page_icon="🏗️")
st.sidebar.title('Navigation')
page = st.sidebar.radio("Go to", ["Wind", "Earthquake"])

if page == "Wind":
    wind.main()

elif page == "Earthquake":
    st.write("# Earthquake Data")

    # Load data
    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/earthquakes-23k.csv")

    # Display data
    st.write("## Raw data")
    st.write(df)

    # Create a scatter plot
    st.write("## Scatter plot")
    st.line_chart(df)

    # Create a histogram
    st.write("## Histogram")
    st.hist(df["mag"], bins=50)