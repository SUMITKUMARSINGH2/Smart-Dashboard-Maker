# home page code will be added here 
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from lotti.lot import Home_lo  

def home_page():
    # Main layout with two columns
    col1, col2 = st.columns([2, 2])
    with col1:
        st.header('📊 Smart Dashboard Maker', divider='rainbow')
        st.caption('✨ Upload → Clean → Visualize → Export ✨')
        st.markdown(
            """
            <div style="font-size:16px; line-height:1.6; text-align:justify;">
            Smart Dashboard Maker is a <b>no-code tool</b> that transforms your data into interactive dashboards instantly.  
            🚀 Upload CSV or Excel files, clean and explore your dataset, auto-generate visualizations, and customize them with ease.  
            <br><br>
            ⚡ <b>Simple</b>, <b>fast</b>, and <b>ready for insights</b> — all in one place.
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st_lottie(Home_lo, speed=1, reverse=True, loop=True, quality='medium', height=380, width=680, key=None)

    # Navigation tabs
    ap = option_menu(
        menu_title=None,
        options=['📘 Introduction', '🚀 Future Features', '💬 Support'],
        icons=['book', 'rocket', 'envelope'],
        orientation='horizontal',
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "#4CAF50", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "5px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#4CAF50", "color": "white"},
        }
    )

    # Content cards
    if ap == '📘 Introduction':
        st.markdown(
            """
            <div style="background:#ffffff; padding:20px; border-radius:15px; 
                        box-shadow:0 4px 10px rgba(0,0,0,0.1); font-size:16px;">
            ✅ <b>Features include:</b><br><br>
            - 📂 Upload CSV/Excel files  <br><br>
            - 🧹 Clean your data (handle missing values, duplicates, replace values)  <br><br>
            - 📊 Auto-generate dashboards <br><br> 
            - 🎨 Customize charts  <br><br>
            - 💾 Export dashboards or cleaned datasets <br><br>  
            - 🤖 Future ML insights and predictions  <br><br>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif ap == '🚀 Future Features':
        st.markdown(
            """
            <div style="background:#ffffff; padding:20px; border-radius:15px; 
                        box-shadow:0 4px 10px rgba(0,0,0,0.1); font-size:16px;">
            🌟 <b>Coming Soon:</b><br><br>
            - 🤖 Automated Machine Learning (AutoML) <br><br>
            - ⏳ Time Series Forecasting  <br><br>
            - 📈 Smart Chart Recommendations  <br><br>
            - 🖼️ Ready-to-use Dashboard Templates  <br><br>
            - 👨‍👩‍👧 Collaboration Features  <br><br>
            - ☁️ Cloud Storage & Live Data APIs  <br><br>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif ap == '💬 Support':
        with st.form("support_form", clear_on_submit=True):
            st.markdown(
                """
                <div style="background:#f9f9f9; padding:20px; border-radius:15px; 
                            box-shadow:0 4px 10px rgba(0,0,0,0.1); margin-bottom:15px;">
                💡 Need help? Fill out the form below and our team will get back to you.  
                </div>
                """,
                unsafe_allow_html=True
            )
            name = st.text_input("👤 Your Name")
            email = st.text_input("📧 Your Email")
            message = st.text_area("💬 Message")
            submitted = st.form_submit_button("📨 Submit")
            if submitted:
                if name and email and message:
                    st.success("✅ Thank you! Your request has been submitted.")
                else:
                    st.error("⚠️ Please fill all fields before submitting.")
