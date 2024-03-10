import streamlit as st
import pandas as pd
import numpy as np
from scipy import interpolate
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

import wind_low_building
import wind_hight_building
import earthquake


st.set_page_config(page_title='แรงลม มยผ', layout='wide', page_icon="🏗️")
st.sidebar.title('Navigation')
page = st.sidebar.radio("Go to", ["การคำนวณแรงลมสำหรับอาคารเตี้ย", "การคำนวณแรงลมสำหรับอาคารสูง","แรงแผ่นดินไหว"])

st.title(page)

if page == "การคำนวณแรงลมสำหรับอาคารเตี้ย":
    wind_low_building.main()

elif page == "การคำนวณแรงลมสำหรับอาคารสูง":
    wind_hight_building.main()

elif page == "แรงแผ่นดินไหว":
    earthquake.main()