import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import random

def generate_dash_app():
    st.header("📊 Interactive Dashboard", divider="rainbow")

    # Check data
    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data available. Please upload a file first.")
        return

    df = st.session_state["clean_data"]

    # --- KPI Cards ---
    st.subheader("📌 Key Metrics")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    total_rows = df.shape[0]
    total_cols = df.shape[1]
    dup_rows = df.duplicated().sum()
    null_vals = int(df.isnull().sum().sum())
    num_cols = df.select_dtypes(include=['int64','float64']).shape[1]
    cat_cols_count = df.select_dtypes(include=['object','category']).shape[1]

    with kpi1: st.metric("Total Rows", total_rows)
    with kpi2: st.metric("Total Columns", total_cols)
    with kpi3: st.metric("Duplicate Rows", dup_rows)
    with kpi4: st.metric("Missing Values", null_vals)
    with kpi5: st.metric("Numeric Columns", num_cols)
    with kpi6: st.metric("Categorical Columns", cat_cols_count)
    st.markdown("---")

    # --- Regenerate ---
    if "regen" not in st.session_state:
        st.session_state["regen"] = 0
    if st.button("🔄 Regenerate Dashboard"):
        st.session_state["regen"] += 1

    # --- Prepare columns & colors ---
    numeric_cols = df.select_dtypes(include=["int64","float64"]).columns
    cat_cols = df.select_dtypes(include=["object","category"]).columns
    chart_types = ["bar","scatter","line","hist","box","pie","area","violin"]
    random.seed(st.session_state["regen"])
    color_seq = px.colors.qualitative.Vivid

    figs = []

    # --- Generate random charts ---
    for i in range(6):
        chart_type = random.choice(chart_types)
        try:
            if chart_type=="bar" and len(cat_cols) > 0:
                x, y = random.choice(cat_cols), random.choice(numeric_cols)
                fig = px.bar(df, x=x, y=y, color=x, color_discrete_sequence=color_seq)
            elif chart_type=="scatter" and len(numeric_cols) > 1:
                x, y = random.sample(list(numeric_cols), 2)
                fig = px.scatter(df, x=x, y=y,
                                 color=random.choice(cat_cols) if len(cat_cols) > 0 else None,
                                 color_discrete_sequence=color_seq)
            elif chart_type=="line" and len(numeric_cols) > 1:
                x, y = random.sample(list(numeric_cols), 2)
                fig = px.line(df, x=x, y=y,
                              color=random.choice(cat_cols) if len(cat_cols) > 0 else None,
                              color_discrete_sequence=color_seq)
            elif chart_type=="pie" and len(cat_cols) > 0:
                col = random.choice(cat_cols)
                fig = px.pie(df, names=col, color=col, color_discrete_sequence=color_seq)
            elif chart_type=="area" and len(numeric_cols) > 1:
                x, y = random.sample(list(numeric_cols), 2)
                fig = px.area(df, x=x, y=y,
                              color=random.choice(cat_cols) if len(cat_cols) > 0 else None,
                              color_discrete_sequence=color_seq)
            elif chart_type=="violin" and len(cat_cols) > 0 and len(numeric_cols) > 0:
                x, y = random.choice(cat_cols), random.choice(numeric_cols)
                fig = px.violin(df, x=x, y=y, box=True, points="all",
                                color=x, color_discrete_sequence=color_seq)
            else:
                col = random.choice(numeric_cols)
                fig = px.histogram(df, x=col, nbins=20, color_discrete_sequence=color_seq)

            fig.update_layout(template="plotly_white", margin=dict(l=20,r=20,t=40,b=20))
            figs.append(fig)
        except Exception as e:
            st.error(f"⚠️ Error in chart {i+1}: {e}")

    # --- Add Map if Location Columns exist ---
    location_cols = [c for c in df.columns if c.lower() in ["city","state","country","region"]]
    lat_cols = [c for c in df.columns if "lat" in c.lower()]
    lon_cols = [c for c in df.columns if "lon" in c.lower() or "lng" in c.lower()]

    try:
        if lat_cols and lon_cols:
            fig_map = px.scatter_geo(df, lat=lat_cols[0], lon=lon_cols[0],
                                     text=location_cols[0] if len(location_cols) > 0 else None,
                                     title="🌍 Map (Lat/Lon)",
                                     color_discrete_sequence=color_seq)
        elif location_cols:
            fig_map = px.scatter_geo(df, locations=location_cols[0],
                                     locationmode="country names",
                                     title=f"🌍 Map of {location_cols[0]}",
                                     color_discrete_sequence=color_seq)
        else:
            fig_map = None
        if fig_map:
            fig_map.update_layout(template="plotly_white", margin=dict(l=20,r=20,t=40,b=20))
            figs.append(fig_map)
    except Exception as e:
        st.error(f"⚠️ Map could not be generated: {e}")

    # --- Display in Grid ---
    # --- Grid Layout ---
    for i in range(0, len(figs), 2):
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(figs[i], width='strecth', key=f"chart_{i}")
        if i + 1 < len(figs): 
            with c2:
                st.plotly_chart(figs[i+1], width='strecth', key=f"chart_{i+1}")


    # --- Save in session for editing later ---
    st.session_state["random_dashboard"] = figs

    # --- Build Exportable HTML with fully embedded charts ---
    kpi_html = f"""
    <div style="display:flex; gap:20px; justify-content:space-around; margin-bottom:30px;">
        <div><h3>Total Rows</h3><p>{total_rows}</p></div>
        <div><h3>Total Columns</h3><p>{total_cols}</p></div>
        <div><h3>Duplicate Rows</h3><p>{dup_rows}</p></div>
        <div><h3>Missing Values</h3><p>{null_vals}</p></div>
        <div><h3>Numeric Columns</h3><p>{num_cols}</p></div>
        <div><h3>Categorical Columns</h3><p>{cat_cols_count}</p></div>
    </div>
    """

    # Use full_html=True to make sure every chart renders properly
    chart_html_parts = [pio.to_html(f, include_plotlyjs=True, full_html=True) for f in figs]

    # Combine charts
    charts_combined_html = "<div class='grid'>" + "".join(chart_html_parts) + "</div>"

    full_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h2 {{ color: #333; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .kpi-card {{ padding: 10px; border-radius: 10px; background:#f8f9fa; text-align:center; }}
        </style>
    </head>
    <body>
        <h1>📊 Smart Dashboard Maker</h1>
        {kpi_html}
        {charts_combined_html}
    </body>
    </html>
    """

    st.download_button("⬇️ Download Dashboard (HTML)", full_html, "dashboard.html", "text/html")

