import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io


def _header(title, sub):
    st.markdown(f"<div class='page-header'><h2>{title}</h2><p>{sub}</p></div>", unsafe_allow_html=True)


def dashboard_page():
    _header("Auto Dashboard", "One-click overview — KPIs, distributions, correlations, and top breakdowns")

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    with st.expander("Dashboard Options"):
        top_n = st.slider("Top N categories in bar charts", 5, 20, 10)
        TMPL = "plotly_white"

    if not num_cols and not cat_cols:
        st.info("No suitable columns found.")
        return

    # ── KPI row ──────────────────────────────────────────────────────────
    st.markdown("**Key Metrics**")
    if num_cols:
        kpi_cols = num_cols[:min(5, len(num_cols))]
        cols = st.columns(len(kpi_cols))
        palette = ["#0EA5E9", "#F59E0B", "#10B981", "#8B5CF6", "#EF4444"]
        for col, nc, color in zip(cols, kpi_cols, palette):
            s = df[nc].dropna()
            col.markdown(f"""
            <div style='background:#FFFFFF;border-radius:10px;padding:1rem;
                        box-shadow:0 1px 4px rgba(0,0,0,0.06);border-top:3px solid {color};'>
                <div style='font-size:0.72rem;font-weight:600;color:#64748B;text-transform:uppercase;
                            letter-spacing:.05em;'>{nc}</div>
                <div style='font-size:1.7rem;font-weight:800;color:#0F172A;margin-top:4px;'>{s.mean():.3g}</div>
                <div style='font-size:0.75rem;color:#94A3B8;margin-top:2px;'>σ = {s.std():.3g}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1 ─────────────────────────────────────────────────────────────
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        if num_cols:
            col = num_cols[0]
            fig = px.histogram(df, x=col, nbins=40, template=TMPL,
                               title=f"Distribution: {col}",
                               color_discrete_sequence=["#0EA5E9"])
            fig.update_layout(height=370, showlegend=False,
                              plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF",
                              bargap=0.05)
            st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            fig = px.imshow(corr, text_auto=".1f", color_continuous_scale="RdBu_r",
                            zmin=-1, zmax=1, template=TMPL, title="Correlation Matrix", aspect="auto")
            fig.update_layout(height=370, paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig, use_container_width=True)
        elif cat_cols:
            vc = df[cat_cols[0]].value_counts().head(top_n)
            fig = px.bar(x=vc.values, y=vc.index, orientation="h", template=TMPL,
                         title=f"Top {top_n}: {cat_cols[0]}",
                         color=vc.values, color_continuous_scale="teal")
            fig.update_layout(height=370, yaxis={"categoryorder": "total ascending"},
                              plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 2 ─────────────────────────────────────────────────────────────
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        if cat_cols and num_cols:
            temp = df.groupby(cat_cols[0])[num_cols[0]].mean().nlargest(top_n).reset_index()
            fig = px.bar(temp, x=num_cols[0], y=cat_cols[0], orientation="h",
                         title=f"Avg {num_cols[0]} by {cat_cols[0]}",
                         template=TMPL, color=num_cols[0],
                         color_continuous_scale="oranges", text_auto=".2s")
            fig.update_layout(height=370, yaxis={"categoryorder": "total ascending"},
                              plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig, use_container_width=True)
        elif len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1], trendline="ols",
                             template=TMPL, title=f"{num_cols[1]} vs {num_cols[0]}",
                             opacity=0.65, color_discrete_sequence=["#8B5CF6"])
            fig.update_layout(height=370, plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        if len(num_cols) >= 2:
            melt = df[num_cols[:min(5, len(num_cols))]].melt(var_name="Column", value_name="Value")
            fig = px.box(melt, x="Column", y="Value", color="Column", template=TMPL,
                         title="Distribution Overview")
            fig.update_layout(height=370, showlegend=False,
                              plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig, use_container_width=True)
        elif cat_cols:
            vc = df[cat_cols[0]].value_counts().head(8)
            fig = px.pie(vc.reset_index(), values="count", names=cat_cols[0],
                         template=TMPL, title=f"Breakdown: {cat_cols[0]}", hole=0.45,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=370, paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig, use_container_width=True)

    # ── Pivot heatmap ──────────────────────────────────────────────────────
    if len(cat_cols) >= 2 and num_cols:
        try:
            pivot = df.groupby([cat_cols[0], cat_cols[1]])[num_cols[0]].mean().unstack(fill_value=0)
            pivot = pivot.iloc[:min(15, pivot.shape[0]), :min(15, pivot.shape[1])]
            fig = px.imshow(pivot, template=TMPL, aspect="auto", text_auto=".1f",
                            title=f"Pivot Heatmap: {num_cols[0]} by {cat_cols[0]} × {cat_cols[1]}",
                            color_continuous_scale="YlOrRd")
            fig.update_layout(height=420, paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

    # ── Missing values ─────────────────────────────────────────────────────
    miss = df.isnull().sum()
    miss = miss[miss > 0]
    if not miss.empty:
        st.markdown("---")
        fig = px.bar(x=miss.values, y=miss.index, orientation="h",
                     template=TMPL, title="Missing Values by Column",
                     color=miss.values, color_continuous_scale="reds",
                     labels={"x": "Missing Count", "y": "Column"})
        fig.update_layout(height=max(300, len(miss) * 38),
                          yaxis={"categoryorder": "total ascending"},
                          plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig, use_container_width=True)

    # ── Export ─────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("Export Dashboard as HTML"):
        charts_html = []
        if num_cols:
            charts_html.append(px.histogram(df, x=num_cols[0], nbins=40).to_html(full_html=False, include_plotlyjs="cdn"))
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            charts_html.append(px.imshow(corr, text_auto=".1f", color_continuous_scale="RdBu_r").to_html(full_html=False, include_plotlyjs=False))
        if cat_cols and num_cols:
            temp = df.groupby(cat_cols[0])[num_cols[0]].mean().nlargest(top_n).reset_index()
            charts_html.append(px.bar(temp, x=num_cols[0], y=cat_cols[0], orientation="h").to_html(full_html=False, include_plotlyjs=False))

        html = f"""<html><head><title>Auto Dashboard</title>
        <style>body{{font-family:'Segoe UI',sans-serif;background:#F1F5F9;padding:20px;}}
        h1{{background:#0F172A;color:white;padding:20px 30px;border-radius:10px;border-left:5px solid #0EA5E9;}}
        .chart{{background:white;border-radius:12px;padding:20px;margin:15px 0;box-shadow:0 2px 8px rgba(0,0,0,.06);}}</style>
        </head><body><h1>Auto Dashboard — {st.session_state.filename}</h1>
        {"".join(f'<div class="chart">{c}</div>' for c in charts_html)}
        </body></html>"""
        st.download_button("Download HTML", data=html.encode(),
                           file_name="dashboard.html", mime="text/html")
