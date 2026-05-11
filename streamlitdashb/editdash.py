import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from styles import DARK_CSS, section_header, kpi_row_html

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,21,40,1)",
    font=dict(family="Space Grotesk", color="#E2E8F0"),
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444"],
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
)

COLOR_SEQ = ["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444","#8B5CF6","#F97316","#06B6D4","#84CC16"]


def edit_dashboard():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header("▦", "Chart Builder", "Build custom charts with full control over axes, colors, and types"), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ Please upload and clean your data first.")
        return

    df = st.session_state["clean_data"]
    num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
    all_cols = df.columns.tolist()

    total_rows = df.shape[0]
    total_cols_n = df.shape[1]

    st.markdown(kpi_row_html([
        ("Rows", f"{total_rows:,}"),
        ("Columns", total_cols_n),
        ("Numeric", len(num_cols)),
        ("Categorical", len(cat_cols)),
        ("Duplicates", int(df.duplicated().sum())),
        ("Missing", int(df.isnull().sum().sum())),
    ]), unsafe_allow_html=True)

    st.markdown("---")

    chart_types = ["bar","scatter","line","histogram","box","area","pie","violin","heatmap","treemap","funnel","bubble"]

    if "chart_configs" not in st.session_state:
        st.session_state["chart_configs"] = [{"type": "bar"}]

    col_add, col_clear, col_info = st.columns([1, 1, 4])
    with col_add:
        if st.button("➕ Add Chart"):
            st.session_state["chart_configs"].append({"type": "bar"})
    with col_clear:
        if st.button("🗑️ Clear All") and len(st.session_state["chart_configs"]) > 1:
            st.session_state["chart_configs"] = [{"type": "bar"}]
            st.rerun()

    figs = []
    to_remove = None

    for i, config in enumerate(st.session_state["chart_configs"]):
        with st.expander(f"Chart {i+1} — {config.get('type','bar').capitalize()}", expanded=True):
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

            with c1:
                ctype = st.selectbox("Chart Type", chart_types,
                                      index=chart_types.index(config.get("type","bar")) if config.get("type") in chart_types else 0,
                                      key=f"ctype_{i}")
                config["type"] = ctype

            with c2:
                x_col = st.selectbox("X Axis", ["— none —"] + all_cols,
                                      index=([" — none —"] + all_cols).index(config.get("x","— none —")) if config.get("x") in all_cols else 0,
                                      key=f"xcol_{i}")
                config["x"] = x_col if x_col != "— none —" else None

            with c3:
                y_needed = ctype not in ["pie","histogram","treemap","funnel"]
                y_col = st.selectbox("Y Axis", ["— none —"] + all_cols,
                                      index=([" — none —"] + all_cols).index(config.get("y","— none —")) if config.get("y") in all_cols else 0,
                                      key=f"ycol_{i}") if y_needed else None
                config["y"] = y_col if y_col and y_col != "— none —" else None

            with c4:
                palette_choice = st.selectbox("Colors", ["Default","Vivid","Bold","Pastel"], key=f"pal_{i}")
                pal_map = {
                    "Default": COLOR_SEQ,
                    "Vivid": px.colors.qualitative.Vivid,
                    "Bold": px.colors.qualitative.Bold,
                    "Pastel": px.colors.qualitative.Pastel,
                }
                color_seq = pal_map[palette_choice]

            co1, co2, co3 = st.columns(3)
            with co1:
                color_by = st.selectbox("Color / Group by",
                                         ["— none —"] + cat_cols + num_cols,
                                         key=f"color_{i}")
                color_by = color_by if color_by != "— none —" else None
                config["color"] = color_by

            with co2:
                nbins = st.number_input("Bins (hist)", 5, 200, 25, key=f"bins_{i}") if ctype == "histogram" else None

            with co3:
                top_n = st.number_input("Rows limit", 10, len(df), min(500, len(df)), key=f"topn_{i}")

            try:
                dff = df.head(top_n)
                x = config.get("x")
                y = config.get("y")
                fig = None

                if ctype == "bar" and x:
                    if y:
                        if x in cat_cols:
                            agg = dff.groupby(x)[y].mean().reset_index().sort_values(y, ascending=False).head(25)
                            fig = px.bar(agg, x=x, y=y, color=x if not color_by else color_by,
                                         color_discrete_sequence=color_seq,
                                         title=f"Average {y} by {x}")
                        else:
                            fig = px.bar(dff, x=x, y=y, color=color_by,
                                         color_discrete_sequence=color_seq)
                    else:
                        vc = dff[x].value_counts().head(25).reset_index()
                        vc.columns = [x, "Count"]
                        fig = px.bar(vc, x=x, y="Count", color=x, color_discrete_sequence=color_seq)

                elif ctype == "scatter" and x and y:
                    fig = px.scatter(dff, x=x, y=y, color=color_by,
                                     color_discrete_sequence=color_seq, opacity=.75,
                                     trendline="ols" if not color_by else None)

                elif ctype == "line" and x and y:
                    fig = px.line(dff, x=x, y=y, color=color_by,
                                  color_discrete_sequence=color_seq)

                elif ctype == "histogram" and x:
                    fig = px.histogram(dff, x=x, nbins=nbins or 25, color=color_by,
                                       color_discrete_sequence=color_seq, barmode="overlay", opacity=.8)

                elif ctype == "box" and y:
                    fig = px.box(dff, x=x, y=y, color=color_by or x,
                                 color_discrete_sequence=color_seq, boxmean=True)

                elif ctype == "area" and x and y:
                    fig = px.area(dff, x=x, y=y, color=color_by,
                                  color_discrete_sequence=color_seq)

                elif ctype == "pie" and x:
                    vc = dff[x].value_counts().head(15)
                    fig = px.pie(values=vc.values, names=vc.index,
                                 color_discrete_sequence=color_seq, hole=.3)

                elif ctype == "violin" and y:
                    fig = px.violin(dff, x=x, y=y, box=True, points="outliers",
                                    color=color_by or x, color_discrete_sequence=color_seq)

                elif ctype == "heatmap" and len(num_cols) >= 2:
                    corr = dff[num_cols].corr()
                    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                                    zmin=-1, zmax=1, title="Correlation Heatmap", aspect="auto")

                elif ctype == "treemap" and x and cat_cols:
                    path_cols = [x]
                    if color_by and color_by != x:
                        path_cols = [color_by, x]
                    val_col = y if y and y in num_cols else num_cols[0] if num_cols else None
                    if val_col:
                        agg = dff.groupby(path_cols)[val_col].sum().reset_index()
                        fig = px.treemap(agg, path=path_cols, values=val_col,
                                         color=val_col, color_continuous_scale="Plasma")

                elif ctype == "funnel" and x and y:
                    agg = dff.groupby(x)[y].sum().reset_index().sort_values(y, ascending=False).head(10)
                    fig = px.funnel(agg, x=y, y=x, color_discrete_sequence=color_seq)

                elif ctype == "bubble" and x and y:
                    size_col = st.selectbox("Bubble size", ["— none —"] + num_cols, key=f"bubble_sz_{i}")
                    fig = px.scatter(dff, x=x, y=y,
                                     size=size_col if size_col != "— none —" else None,
                                     color=color_by, color_discrete_sequence=color_seq,
                                     opacity=.7)

                if fig:
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True, key=f"builder_chart_{i}")
                    figs.append(fig)
                else:
                    st.info("Configure X/Y axes above to render the chart.")

            except Exception as e:
                st.error(f"Chart error: {e}")

            if st.button(f"🗑️ Remove Chart {i+1}", key=f"rm_chart_{i}"):
                to_remove = i

    if to_remove is not None:
        st.session_state["chart_configs"].pop(to_remove)
        st.rerun()

    st.session_state["edited_dashboard"] = figs

    # ── Export ─────────────────────────────────────────────────────────────────
    if figs:
        st.markdown("---")
        chart_divs = "".join([
            f'<div style="margin-bottom:20px;">{pio.to_html(f, include_plotlyjs="cdn", full_html=False)}</div>'
            for f in figs
        ])
        full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>DataViz Pro — Custom Dashboard</title>
        <style>body{{font-family:'Segoe UI',sans-serif;background:#060B1A;color:#E2E8F0;padding:40px;margin:0;}}
        h1{{color:#00D4FF;}} .grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;}}</style>
        </head><body>
        <h1>▦ Custom Dashboard</h1>
        <p style="color:#94A3B8;margin-bottom:24px;">Built with DataViz Pro — {st.session_state.get("filename","dataset")}</p>
        <div class="grid">{chart_divs}</div>
        </body></html>"""
        st.download_button("⬇️ Download Dashboard (HTML)", full_html, "custom_dashboard.html", "text/html")
