import streamlit as st


def home_page():
    st.markdown("""
    <div class="main-header">
        <h1>🔬 DataViz Pro — Advanced Analytics Platform</h1>
        <p>Upload any dataset · Profile · Clean · Explore · Visualize · Export</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    stats = [
        ("📁", "4+", "File Formats", "#667eea"),
        ("📊", "12+", "Chart Types", "#f093fb"),
        ("🧹", "8+", "Cleaning Tools", "#4facfe"),
        ("📤", "3", "Export Options", "#43e97b"),
    ]
    for col, (icon, val, label, color) in zip(cols, stats):
        col.markdown(f"""
        <div style='background:white;border-radius:12px;padding:1.2rem;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);border-top:4px solid {color};
                    text-align:center;'>
            <div style='font-size:2rem'>{icon}</div>
            <div style='font-size:2rem;font-weight:700;color:{color}'>{val}</div>
            <div style='color:#666;font-size:0.85rem'>{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("## ✨ What You Can Do")

    features = [
        {
            "icon": "☁️",
            "title": "Upload Data",
            "desc": "Supports CSV, Excel (xlsx/xls), JSON, and Parquet files. Auto-detects column types and previews your dataset instantly.",
            "color": "#667eea"
        },
        {
            "icon": "🔎",
            "title": "Deep Data Profiling",
            "desc": "Get a full statistical profile: missing values, skewness, kurtosis, unique counts, memory usage, and more — per column.",
            "color": "#f093fb"
        },
        {
            "icon": "🧹",
            "title": "Advanced Data Cleaning",
            "desc": "Remove duplicates, fill or drop nulls (mean/median/mode/interpolate), detect and remove outliers via IQR or Z-Score, rename/drop columns.",
            "color": "#4facfe"
        },
        {
            "icon": "📈",
            "title": "EDA & Statistics",
            "desc": "Correlation heatmaps (Seaborn), distribution plots with KDE, pair plots, box plots, count plots, and skewness analysis.",
            "color": "#43e97b"
        },
        {
            "icon": "🎨",
            "title": "Interactive Chart Builder",
            "desc": "12+ chart types powered by Plotly: Bar, Line, Scatter, Pie, Box, Violin, Heatmap, Treemap, Sunburst, Histogram, Area, Bubble, Funnel.",
            "color": "#fa709a"
        },
        {
            "icon": "⚡",
            "title": "Auto Dashboard",
            "desc": "One click generates a full multi-panel dashboard with KPI cards, auto-selected charts, missing value summary, and top correlations.",
            "color": "#fee140"
        },
        {
            "icon": "📅",
            "title": "Time Series Analysis",
            "desc": "Auto-detect datetime columns, plot trends, add rolling averages, analyze year/month/day breakdowns and growth rates.",
            "color": "#a18cd1"
        },
        {
            "icon": "📤",
            "title": "Export Everything",
            "desc": "Download your cleaned data as CSV or Excel. Export any chart as interactive HTML. Generate a full HTML data report.",
            "color": "#fda085"
        },
    ]

    col1, col2 = st.columns(2)
    for i, f in enumerate(features):
        target = col1 if i % 2 == 0 else col2
        target.markdown(f"""
        <div style='background:white;border-radius:12px;padding:1.2rem 1.5rem;
                    margin-bottom:1rem;box-shadow:0 2px 10px rgba(0,0,0,0.07);
                    border-left:5px solid {f["color"]}'>
            <div style='font-size:1.5rem;margin-bottom:0.4rem'>{f["icon"]} <strong>{f["title"]}</strong></div>
            <div style='color:#555;font-size:0.9rem;line-height:1.5'>{f["desc"]}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🚀 Quick Start")
    st.info("👈 Click **Upload Data** in the sidebar to get started. Supported formats: CSV, Excel, JSON, Parquet")

    with st.expander("💡 Tips for best results"):
        st.markdown("""
        - **CSV files** work best with a clear header row
        - **Date columns** are auto-detected for time series analysis
        - Start with **Data Profiling** to understand your dataset before cleaning
        - Use **EDA & Statistics** to spot correlations before building charts
        - The **Auto Dashboard** gives you an instant overview with zero configuration
        """)
