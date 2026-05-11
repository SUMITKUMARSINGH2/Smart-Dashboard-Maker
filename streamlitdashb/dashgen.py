import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import random
from .styles import DARK_CSS, section_header, kpi_row_html

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,21,40,1)",
    font=dict(family="Space Grotesk", color="#E2E8F0"),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
)

COLOR_SEQ = ["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444","#8B5CF6","#F97316","#06B6D4","#84CC16"]


def generate_dash_app():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header("⚡", "Auto Dashboard", "AI-generated charts and KPIs from your dataset"), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data available. Please upload a file first.")
        return

    df = st.session_state["clean_data"]

    # ── KPI Row ────────────────────────────────────────────────────────────────
    total_rows = df.shape[0]
    total_cols = df.shape[1]
    dup_rows = int(df.duplicated().sum())
    null_vals = int(df.isnull().sum().sum())
    num_count = df.select_dtypes(include=["int64","float64","int32","float32"]).shape[1]
    cat_count = df.select_dtypes(include=["object","category"]).shape[1]

    st.markdown(kpi_row_html([
        ("Rows", f"{total_rows:,}"),
        ("Columns", total_cols),
        ("Duplicate Rows", dup_rows),
        ("Missing Values", f"{null_vals:,}"),
        ("Numeric Cols", num_count),
        ("Categorical Cols", cat_count),
    ]), unsafe_allow_html=True)

    st.markdown("---")

    # ── Controls ───────────────────────────────────────────────────────────────
    ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([1, 1, 2])
    with ctrl_c1:
        n_charts = st.slider("Number of charts", 2, 12, 6)
    with ctrl_c2:
        if "regen" not in st.session_state:
            st.session_state["regen"] = 0
        if st.button("🔄 Regenerate Dashboard"):
            st.session_state["regen"] += 1
    with ctrl_c3:
        chart_style = st.selectbox("Chart palette", ["Cyan/Purple", "Vivid", "Bold", "Pastel"])

    palette_map = {
        "Cyan/Purple": COLOR_SEQ,
        "Vivid": px.colors.qualitative.Vivid,
        "Bold": px.colors.qualitative.Bold,
        "Pastel": px.colors.qualitative.Pastel,
    }
    color_seq = palette_map[chart_style]

    # ── Generate Charts ────────────────────────────────────────────────────────
    numeric_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
    chart_types = ["bar","scatter","line","hist","box","pie","area","violin"]

    random.seed(st.session_state["regen"])
    figs = []

    for i in range(n_charts):
        chart_type = random.choice(chart_types)
        try:
            if chart_type == "bar" and cat_cols and numeric_cols:
                x, y = random.choice(cat_cols), random.choice(numeric_cols)
                agg_df = df.groupby(x)[y].mean().reset_index().sort_values(y, ascending=False).head(20)
                fig = px.bar(agg_df, x=x, y=y, color=x, color_discrete_sequence=color_seq,
                             title=f"Average {y} by {x}")

            elif chart_type == "scatter" and len(numeric_cols) >= 2:
                x, y = random.sample(numeric_cols, 2)
                fig = px.scatter(df, x=x, y=y,
                                 color=random.choice(cat_cols) if cat_cols else None,
                                 color_discrete_sequence=color_seq, opacity=.7,
                                 title=f"{x} vs {y}")

            elif chart_type == "line" and len(numeric_cols) >= 2:
                x, y = random.sample(numeric_cols, 2)
                fig = px.line(df.head(200), x=x, y=y,
                              color=random.choice(cat_cols) if cat_cols else None,
                              color_discrete_sequence=color_seq,
                              title=f"{y} over {x}")

            elif chart_type == "pie" and cat_cols:
                col = random.choice(cat_cols)
                vc = df[col].value_counts().head(10)
                fig = px.pie(values=vc.values, names=vc.index,
                             color_discrete_sequence=color_seq,
                             title=f"Distribution of {col}", hole=.35)

            elif chart_type == "area" and len(numeric_cols) >= 2:
                x, y = random.sample(numeric_cols, 2)
                fig = px.area(df.head(200), x=x, y=y,
                              color=random.choice(cat_cols) if cat_cols else None,
                              color_discrete_sequence=color_seq,
                              title=f"{y} area over {x}")

            elif chart_type == "violin" and cat_cols and numeric_cols:
                x, y = random.choice(cat_cols), random.choice(numeric_cols)
                top_cats = df[x].value_counts().head(6).index
                dff = df[df[x].isin(top_cats)]
                fig = px.violin(dff, x=x, y=y, box=True, points="outliers",
                                color=x, color_discrete_sequence=color_seq,
                                title=f"{y} by {x}")

            elif chart_type == "box" and numeric_cols:
                col = random.choice(numeric_cols)
                grp = random.choice(cat_cols) if cat_cols else None
                if grp:
                    top_cats = df[grp].value_counts().head(6).index
                    dff = df[df[grp].isin(top_cats)]
                    fig = px.box(dff, x=grp, y=col, color=grp,
                                 color_discrete_sequence=color_seq,
                                 title=f"{col} by {grp}")
                else:
                    fig = px.box(df, y=col, color_discrete_sequence=color_seq,
                                 title=f"Box plot — {col}")

            else:
                if numeric_cols:
                    col = random.choice(numeric_cols)
                    fig = px.histogram(df, x=col, nbins=25,
                                       color_discrete_sequence=color_seq,
                                       title=f"Distribution of {col}")
                else:
                    continue

            fig.update_layout(**PLOTLY_THEME)
            fig.update_traces(marker_line_width=0)
            figs.append(fig)

        except Exception as e:
            st.error(f"Chart {i+1} error: {e}")

    # ── Map ────────────────────────────────────────────────────────────────────
    lat_cols = [c for c in df.columns if "lat" in c.lower()]
    lon_cols = [c for c in df.columns if "lon" in c.lower() or "lng" in c.lower()]
    loc_cols = [c for c in df.columns if c.lower() in ["city","state","country","region"]]
    try:
        if lat_cols and lon_cols:
            fig_map = px.scatter_mapbox(df.dropna(subset=[lat_cols[0], lon_cols[0]]).head(500),
                                         lat=lat_cols[0], lon=lon_cols[0],
                                         hover_name=loc_cols[0] if loc_cols else None,
                                         color_discrete_sequence=["#00D4FF"],
                                         zoom=2, title="🌍 Geographic Map")
            fig_map.update_layout(mapbox_style="carto-darkmatter", **PLOTLY_THEME)
            figs.append(fig_map)
    except Exception:
        pass

    # ── Grid Display ───────────────────────────────────────────────────────────
    for i in range(0, len(figs), 2):
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(figs[i], use_container_width=True, key=f"dash_chart_{i}")
        if i + 1 < len(figs):
            with c2:
                st.plotly_chart(figs[i+1], use_container_width=True, key=f"dash_chart_{i+1}")

    st.session_state["random_dashboard"] = figs

    # ── Export ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    kpi_html = f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px;">
      <div style="background:#0D1528;padding:16px 20px;border-radius:10px;border-top:3px solid #00D4FF;min-width:120px;">
        <div style="font-family:monospace;font-size:1.5rem;color:#00D4FF;font-weight:700;">{total_rows:,}</div>
        <div style="font-size:.72rem;text-transform:uppercase;color:#94A3B8;">Total Rows</div>
      </div>
      <div style="background:#0D1528;padding:16px 20px;border-radius:10px;border-top:3px solid #7C3AED;min-width:120px;">
        <div style="font-family:monospace;font-size:1.5rem;color:#7C3AED;font-weight:700;">{total_cols}</div>
        <div style="font-size:.72rem;text-transform:uppercase;color:#94A3B8;">Columns</div>
      </div>
      <div style="background:#0D1528;padding:16px 20px;border-radius:10px;border-top:3px solid #10B981;min-width:120px;">
        <div style="font-family:monospace;font-size:1.5rem;color:#10B981;font-weight:700;">{num_count}</div>
        <div style="font-size:.72rem;text-transform:uppercase;color:#94A3B8;">Numeric Cols</div>
      </div>
      <div style="background:#0D1528;padding:16px 20px;border-radius:10px;border-top:3px solid #FF006E;min-width:120px;">
        <div style="font-family:monospace;font-size:1.5rem;color:#FF006E;font-weight:700;">{null_vals:,}</div>
        <div style="font-size:.72rem;text-transform:uppercase;color:#94A3B8;">Missing</div>
      </div>
    </div>"""

    charts_html = "".join([
        f'<div style="margin-bottom:20px;">{pio.to_html(f, include_plotlyjs="cdn", full_html=False)}</div>'
        for f in figs
    ])
    export_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>DataViz Pro Dashboard</title>
    <style>body{{font-family:'Segoe UI',sans-serif;background:#060B1A;color:#E2E8F0;padding:40px;margin:0;}}
    h1{{color:#00D4FF;margin-bottom:8px;}} .grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;}}</style>
    </head><body>
    <h1>⬡ DataViz Pro Dashboard</h1>
    <p style="color:#94A3B8;margin-bottom:24px;">Auto-generated from {st.session_state.get("filename","dataset")}</p>
    {kpi_html}
    <div class="grid">{charts_html}</div>
    </body></html>"""

    st.download_button("⬇️ Download Dashboard (HTML)", export_html, "dashboard.html", "text/html")
