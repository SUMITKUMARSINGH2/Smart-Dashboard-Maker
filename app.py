# all main code will be return here 
import streamlit as st
from streamlit_option_menu import option_menu
from home import home_page
from filesin import file_upload
from dataover import data_overview
from dashgen import generate_dash_app
from editdash import edit_dashboard



st.set_page_config(
    page_title="Smart Dashboard Maker",
    page_icon="📊",
    layout="wide"
)


with st.sidebar:
    app = option_menu(
                    menu_title="Menu",
                    options=['Home', 
                            'File upload',
                            'Data Overview',
                            'Dashboard Generator',
                            'Edit Dashboard',
                            ],
                            icons=[
                            'house-fill',
                            'cloud-upload',  
                            'table',      
                            'bar-chart-line',         
                            'pencil-square',     
                            ],      
                            menu_icon="bookmark-star"
                    )
if app == 'Home':
    home_page()
elif app ==  'File upload':
    file_upload()
elif app == 'Data Overview':
    data_overview()
elif app == 'Dashboard Generator':
     generate_dash_app()
elif app ==  'Edit Dashboard':
    edit_dashboard()

