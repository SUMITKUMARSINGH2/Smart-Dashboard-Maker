# file input code will be added here
#Importing necessary libraries and modules
import streamlit as st 
import pandas as pd
from streamlit_lottie import st_lottie
from lotti.lot import Filepre_lo
def file_upload():
    col1, col2 = st.columns([2, 2])
    with col1:
        st.header('📁 Upload your data', divider='rainbow')
        st.markdown(
            """
            ### 🔼 Upload Your Dataset  
            Smart Dashboard Maker supports **CSV and Excel files (.csv, .xlsx, .xls)**.  
            Upload your data below to preview it instantly and start creating dashboards.  
            """
        )
    with col2:
        st_lottie(Filepre_lo, speed=1, reverse=True, loop=True, quality='medium', height=380, width=680, key=None)
    st.header('📁 Upload your data... ���')
    inputer = st.file_uploader('Upload your data here', type=['csv','xlsx','xls'],label_visibility = "hidden")
    if inputer is not None:
        if inputer.name.endswith('.csv'):
            data = pd.read_csv(inputer)
        elif inputer.name.endswith('.xlsx') or inputer.name.endswith('.xls'):
            data = pd.read_excel(inputer)
        st.session_state["raw_data"] = data.copy()
        st.session_state["clean_data"] = data.copy()
        st.success('File uploaded successfully!')
        st.dataframe(data,hide_index=True,width="stretch",on_select="ignore",use_container_width=True,height=600)
    else:
        st.info("ℹ️ Please upload a file to proceed.")