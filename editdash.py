# import streamlit as st
# import plotly.express as px
# import plotly.io as pio

# def edit_dashboard():
#     st.header("✏️ Edit Dashboard", divider="rainbow")

#     if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
#         st.warning("⚠️ Please upload and clean your data first.")
#         return

#     df = st.session_state["clean_data"]

#     # --- KPI Cards ---
#     st.subheader("📌 Key Metrics")
#     k1,k2,k3,k4,k5,k6 = st.columns(6)
#     with k1: st.metric("Total Rows", df.shape[0])
#     with k2: st.metric("Total Columns", df.shape[1])
#     with k3: st.metric("Duplicate Rows", df.duplicated().sum())
#     with k4: st.metric("Missing Values", int(df.isnull().sum().sum()))
#     with k5: st.metric("Numeric Columns", df.select_dtypes(include=["int64","float64"]).shape[1])
#     with k6: st.metric("Categorical Columns", df.select_dtypes(include=["object","category"]).shape[1])
#     st.markdown("---")

#     # --- Column Detection ---
#     num_cols = df.select_dtypes(include=["int64","float64"]).columns.tolist()
#     cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
#     all_cols = df.columns.tolist()

#     chart_types = ["bar","scatter","line","hist","box","area","pie","violin","map"]
#     color_seq = px.colors.qualitative.Vivid

#     # --- Manage number of charts dynamically ---
#     if "num_edit_charts" not in st.session_state:
#         st.session_state["num_edit_charts"] = 1  # start with 1

#     if st.button("➕ Add One More Chart"):
#         st.session_state["num_edit_charts"] += 1

#     figs = []

#     # --- Chart builders ---
#     for i in range(st.session_state["num_edit_charts"]):
#         with st.container():
#             st.markdown(f"### Chart {i+1}")
#             col1, col2, col3 = st.columns([1, 1, 1])

#             with col1:
#                 ctype = st.selectbox(f"Type {i+1}", chart_types, key=f"type_{i}")

#             with col2:
#                 x_col = st.selectbox(f"X Axis {i+1}", all_cols, key=f"x_{i}")
#                 y_needed = ctype not in ["pie", "hist", "map"]
#                 y_col = st.selectbox(f"Y Axis {i+1}", [None] + all_cols, key=f"y_{i}") if y_needed else None

#             with col3:
#                 color_by = st.selectbox(
#                     f"Group/Color {i+1}",
#                     [None] + cat_cols,
#                     key=f"color_{i}"
#                 )

#             try:
#                 if ctype == "bar":
#                     fig = px.bar(df, x=x_col, y=y_col,
#                                  color=color_by or (x_col if x_col in cat_cols else None),
#                                  color_discrete_sequence=color_seq)
#                 elif ctype == "scatter":
#                     fig = px.scatter(df, x=x_col, y=y_col,
#                                      color=color_by, color_discrete_sequence=color_seq)
#                 elif ctype == "line":
#                     fig = px.line(df, x=x_col, y=y_col,
#                                   color=color_by, color_discrete_sequence=color_seq)
#                 elif ctype == "hist":
#                     fig = px.histogram(df, x=x_col,
#                                        color=color_by, nbins=20,
#                                        color_discrete_sequence=color_seq)
#                 elif ctype == "box":
#                     fig = px.box(df, x=x_col, y=y_col,
#                                  color=color_by or (x_col if x_col in cat_cols else None),
#                                  color_discrete_sequence=color_seq)
#                 elif ctype == "area":
#                     fig = px.area(df, x=x_col, y=y_col,
#                                   color=color_by, color_discrete_sequence=color_seq)
#                 elif ctype == "pie":
#                     fig = px.pie(df, names=x_col,
#                                  color=color_by or (x_col if x_col in cat_cols else None),
#                                  color_discrete_sequence=color_seq)
#                 elif ctype == "violin":
#                     fig = px.violin(df, x=x_col, y=y_col,
#                                     box=True, points="all",
#                                     color=color_by or (x_col if x_col in cat_cols else None),
#                                     color_discrete_sequence=color_seq)
#                 elif ctype == "map":
#                     location_cols = [c for c in df.columns if c.lower() in ["city","state","country","region"]]
#                     lat_cols = [c for c in df.columns if "lat" in c.lower()]
#                     lon_cols = [c for c in df.columns if "lon" in c.lower() or "lng" in c.lower()]
#                     if lat_cols and lon_cols:
#                         fig = px.scatter_geo(df, lat=lat_cols[0], lon=lon_cols[0],
#                                              text=location_cols[0] if location_cols else None,
#                                              color=color_by, color_discrete_sequence=color_seq)
#                     elif location_cols:
#                         fig = px.scatter_geo(df, locations=location_cols[0],
#                                              locationmode="country names",
#                                              color=color_by, color_discrete_sequence=color_seq)
#                     else:
#                         st.error("⚠️ No geo columns (lat/lon or city/state/country) found for map.")
#                         continue
#                 else:
#                     fig = px.histogram(df, x=x_col, nbins=20,
#                                        color=color_by, color_discrete_sequence=color_seq)

#                 fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
#                 st.plotly_chart(fig, use_container_width=True, key=f"edit_plot_{i}")
#                 figs.append(fig)

#             except Exception as e:
#                 st.error(f"⚠️ Error building chart {i+1}: {e}")

#     # Save edited dashboard
#     st.session_state["edited_dashboard"] = figs

#     # --- Export HTML (KPIs + Charts) ---
#     import plotly.io as pio
#     kpi_html = f"""
#     <div style="display:flex; gap:20px; justify-content:space-around; margin-bottom:30px;">
#         <div class="kpi-card"><h3>Total Rows</h3><p>{df.shape[0]}</p></div>
#         <div class="kpi-card"><h3>Total Columns</h3><p>{df.shape[1]}</p></div>
#         <div class="kpi-card"><h3>Duplicate Rows</h3><p>{df.duplicated().sum()}</p></div>
#         <div class="kpi-card"><h3>Missing Values</h3><p>{int(df.isnull().sum().sum())}</p></div>
#         <div class="kpi-card"><h3>Numeric Columns</h3><p>{len(num_cols)}</p></div>
#         <div class="kpi-card"><h3>Categorical Columns</h3><p>{len(cat_cols)}</p></div>
#     </div>
#     """

#     chart_html_parts = [pio.to_html(f, include_plotlyjs=False, full_html=False) for f in figs]
#     full_html = f"""
#     <html>
#     <head>
#         <meta charset="utf-8" />
#         <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
#         <style>
#             body {{ font-family: Arial, sans-serif; margin: 40px; background: #fff; }}
#             h1 {{ margin-bottom: 10px; }}
#             .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
#             .kpi-card {{
#                 padding: 12px 16px; border-radius: 10px; background:#f8f9fa;
#                 text-align:center; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
#             }}
#         </style>
#     </head>
#     <body>
#         <h1>✏️ Edited Dashboard</h1>
#         {kpi_html}
#         <div class="grid">
#             {''.join(f"<div>{c}</div>" for c in chart_html_parts)}
#         </div>
#     </body>
#     </html>
#     """

#     st.download_button(
#         "⬇️ Download Edited Dashboard (HTML)",
#         full_html,
#         "edited_dashboard.html",
#         "text/html"
#     )

import streamlit as st
import plotly.express as px
import plotly.io as pio

def edit_dashboard():
    st.header("✏️ Edit Dashboard", divider="rainbow")

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ Please upload and clean your data first.")
        return

    df = st.session_state["clean_data"]

    # --- KPI Cards ---
    st.subheader("📌 Key Metrics")
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    with k1: st.metric("Total Rows", df.shape[0])
    with k2: st.metric("Total Columns", df.shape[1])
    with k3: st.metric("Duplicate Rows", df.duplicated().sum())
    with k4: st.metric("Missing Values", int(df.isnull().sum().sum()))
    with k5: st.metric("Numeric Columns", df.select_dtypes(include=["int64","float64"]).shape[1])
    with k6: st.metric("Categorical Columns", df.select_dtypes(include=["object","category"]).shape[1])
    st.markdown("---")

    # --- Column Detection ---
    num_cols = df.select_dtypes(include=["int64","float64"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
    all_cols = df.columns.tolist()

    chart_types = ["bar","scatter","line","hist","box","area","pie","violin","map"]
    color_seq = px.colors.qualitative.Vivid

    # --- Manage number of charts dynamically ---
    if "chart_configs" not in st.session_state:
        st.session_state["chart_configs"] = [{}]  # start with 1 chart

    if st.button("➕ Add Chart"):
        st.session_state["chart_configs"].append({})

    figs = []

    # --- Chart builders ---
    for i, config in enumerate(st.session_state["chart_configs"]):
        with st.container():
            st.markdown(f"### Chart {i+1}")
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                ctype = st.selectbox(f"Type {i+1}", chart_types,
                                     key=f"type_{i}", index=chart_types.index(config.get("type","bar")) if config.get("type") in chart_types else 0)
                config["type"] = ctype

            with col2:
                x_col = st.selectbox(f"X Axis {i+1}", all_cols,
                                     key=f"x_{i}", index=all_cols.index(config.get("x", all_cols[0])) if config.get("x") in all_cols else 0)
                config["x"] = x_col

                y_needed = ctype not in ["pie", "hist", "map"]
                y_col = st.selectbox(f"Y Axis {i+1}", [None] + all_cols,
                                     key=f"y_{i}", index=( [None]+all_cols ).index(config.get("y")) if config.get("y") in all_cols else 0) if y_needed else None
                config["y"] = y_col

            with col3:
                color_by = st.selectbox(f"Group/Color {i+1}", [None] + cat_cols,
                                        key=f"color_{i}", index=( [None]+cat_cols ).index(config.get("color")) if config.get("color") in cat_cols else 0)
                config["color"] = color_by

            try:
                if ctype == "bar":
                    fig = px.bar(df, x=x_col, y=y_col,
                                 color=color_by or (x_col if x_col in cat_cols else None),
                                 color_discrete_sequence=color_seq)
                elif ctype == "scatter":
                    fig = px.scatter(df, x=x_col, y=y_col,
                                     color=color_by, color_discrete_sequence=color_seq)
                elif ctype == "line":
                    fig = px.line(df, x=x_col, y=y_col,
                                  color=color_by, color_discrete_sequence=color_seq)
                elif ctype == "hist":
                    fig = px.histogram(df, x=x_col,
                                       color=color_by, nbins=20,
                                       color_discrete_sequence=color_seq)
                elif ctype == "box":
                    fig = px.box(df, x=x_col, y=y_col,
                                 color=color_by or (x_col if x_col in cat_cols else None),
                                 color_discrete_sequence=color_seq)
                elif ctype == "area":
                    fig = px.area(df, x=x_col, y=y_col,
                                  color=color_by, color_discrete_sequence=color_seq)
                elif ctype == "pie":
                    fig = px.pie(df, names=x_col,
                                 color=color_by or (x_col if x_col in cat_cols else None),
                                 color_discrete_sequence=color_seq)
                elif ctype == "violin":
                    fig = px.violin(df, x=x_col, y=y_col,
                                    box=True, points="all",
                                    color=color_by or (x_col if x_col in cat_cols else None),
                                    color_discrete_sequence=color_seq)
                elif ctype == "map":
                    location_cols = [c for c in df.columns if c.lower() in ["city","state","country","region"]]
                    lat_cols = [c for c in df.columns if "lat" in c.lower()]
                    lon_cols = [c for c in df.columns if "lon" in c.lower() or "lng" in c.lower()]
                    if lat_cols and lon_cols:
                        fig = px.scatter_geo(df, lat=lat_cols[0], lon=lon_cols[0],
                                             text=location_cols[0] if location_cols else None,
                                             color=color_by, color_discrete_sequence=color_seq)
                    elif location_cols:
                        fig = px.scatter_geo(df, locations=location_cols[0],
                                             locationmode="country names",
                                             color=color_by, color_discrete_sequence=color_seq)
                    else:
                        st.error("⚠️ No geo columns (lat/lon or city/state/country) found for map.")
                        continue
                else:
                    fig = px.histogram(df, x=x_col, nbins=20,
                                       color=color_by, color_discrete_sequence=color_seq)

                fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True, key=f"edit_plot_{i}")
                figs.append(fig)

                # Remove button for this chart
                if st.button(f"➖ Remove Chart {i+1}", key=f"remove_{i}"):
                    st.session_state["chart_configs"].pop(i)
                    st.rerun()

            except Exception as e:
                st.error(f"⚠️ Error building chart {i+1}: {e}")

    # Save edited dashboard
    st.session_state["edited_dashboard"] = figs

    # --- Export HTML (KPIs + Charts) ---
    kpi_html = f"""
    <div style="display:flex; gap:20px; justify-content:space-around; margin-bottom:30px;">
        <div class="kpi-card"><h3>Total Rows</h3><p>{df.shape[0]}</p></div>
        <div class="kpi-card"><h3>Total Columns</h3><p>{df.shape[1]}</p></div>
        <div class="kpi-card"><h3>Duplicate Rows</h3><p>{df.duplicated().sum()}</p></div>
        <div class="kpi-card"><h3>Missing Values</h3><p>{int(df.isnull().sum().sum())}</p></div>
        <div class="kpi-card"><h3>Numeric Columns</h3><p>{len(num_cols)}</p></div>
        <div class="kpi-card"><h3>Categorical Columns</h3><p>{len(cat_cols)}</p></div>
    </div>
    """
    chart_html_parts = [pio.to_html(f, include_plotlyjs=False, full_html=False) for f in figs]
    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8" />
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #fff; }}
            h1 {{ margin-bottom: 10px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .kpi-card {{
                padding: 12px 16px; border-radius: 10px; background:#f8f9fa;
                text-align:center; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            }}
        </style>
    </head>
    <body>
        <h1>✏️ Edited Dashboard</h1>
        {kpi_html}
        <div class="grid">
            {''.join(f"<div>{c}</div>" for c in chart_html_parts)}
        </div>
    </body>
    </html>
    """
    st.download_button(
        "⬇️ Download Edited Dashboard (HTML)",
        full_html,
        "edited_dashboard.html",
        "text/html"
    )
