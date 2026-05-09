import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

_PLOTLY_DARK = dict(
    paper_bgcolor="#0A0F1E",
    plot_bgcolor="#0D1526",
    font=dict(color="#94A3B8", family="Space Grotesk"),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    title_font=dict(size=14, color="#E2E8F0"),
)


def _header(title, sub):
    st.markdown(f"""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// auto dashboard</div>
        <h2>{title}</h2>
        <div class='page-header-bar'></div>
        <p>{sub}</p>
    </div>""", unsafe_allow_html=True)


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

    if not num_cols and not cat_cols:
        st.info("No suitable columns found.")
        return

    # ── KPI row ──────────────────────────────────────────────────────────
    st.markdown("<span style='color:#A0AEC0;font-weight:600;font-size:.83rem;'>Key Metrics</span>", unsafe_allow_html=True)
    if num_cols:
        kpi_cols = num_cols[:min(5, len(num_cols))]
        cols = st.columns(len(kpi_cols))
        palette = ["#00D4FF", "#A855F7", "#10B981", "#F59E0B", "#FF006E"]
        for col, nc, color in zip(cols, kpi_cols, palette):
            s = df[nc].dropna()
            col.markdown(f"""
            <div style='background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                        border-radius:12px;padding:1rem 1.1rem;
                        border-top:2px solid {color};
                        transition:all .2s;'>
                <div style='font-size:.62rem;font-weight:600;color:#64748B;text-transform:uppercase;
                            letter-spacing:.1em;font-family:"JetBrains Mono",monospace;margin-bottom:4px;'>{nc}</div>
                <div style='font-size:1.6rem;font-weight:700;color:{color};font-family:"Space Grotesk",sans-serif;
                            line-height:1;'>{s.mean():.3g}</div>
                <div style='font-size:.68rem;color:#4A5568;margin-top:3px;font-family:"JetBrains Mono",monospace;'>
                    σ = {s.std():.3g}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1 ─────────────────────────────────────────────────────────────
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        if num_cols:
            col = num_cols[0]
            fig = px.histogram(df, x=col, nbins=40, template="plotly_dark",
                               title=f"Distribution: {col}",
                               color_discrete_sequence=["#00D4FF"])
            fig.update_layout(height=370, showlegend=False, bargap=0.05, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            fig = px.imshow(corr, text_auto=".1f",
                            color_continuous_scale=["#FF006E","#0D1526","#00D4FF"],
                            zmin=-1, zmax=1, template="plotly_dark",
                            title="Correlation Matrix", aspect="auto")
            fig.update_layout(height=370, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)
        elif cat_cols:
            vc = df[cat_cols[0]].value_counts().head(top_n)
            fig = px.bar(x=vc.values, y=vc.index, orientation="h",
                         template="plotly_dark",
                         title=f"Top {top_n}: {cat_cols[0]}",
                         color=vc.values,
                         color_continuous_scale=["#7C3AED", "#00D4FF"])
            fig.update_layout(height=370, yaxis={"categoryorder": "total ascending"}, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 2 ─────────────────────────────────────────────────────────────
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        if cat_cols and num_cols:
            temp = df.groupby(cat_cols[0])[num_cols[0]].mean().nlargest(top_n).reset_index()
            fig = px.bar(temp, x=num_cols[0], y=cat_cols[0], orientation="h",
                         title=f"Avg {num_cols[0]} by {cat_cols[0]}",
                         template="plotly_dark", color=num_cols[0],
                         color_continuous_scale=["#7C3AED", "#FF006E"], text_auto=".2s")
            fig.update_layout(height=370, yaxis={"categoryorder": "total ascending"}, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)
        elif len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1], trendline="ols",
                             template="plotly_dark",
                             title=f"{num_cols[1]} vs {num_cols[0]}",
                             opacity=0.65,
                             color_discrete_sequence=["#00D4FF"])
            fig.update_layout(height=370, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        if len(num_cols) >= 2:
            melt = df[num_cols[:min(5, len(num_cols))]].melt(var_name="Column", value_name="Value")
            fig = px.box(melt, x="Column", y="Value", color="Column",
                         template="plotly_dark", title="Distribution Overview",
                         color_discrete_sequence=["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B"])
            fig.update_layout(height=370, showlegend=False, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)
        elif cat_cols:
            vc = df[cat_cols[0]].value_counts().head(8)
            fig = px.pie(vc.reset_index(), values="count", names=cat_cols[0],
                         template="plotly_dark",
                         title=f"Breakdown: {cat_cols[0]}", hole=0.45,
                         color_discrete_sequence=["#00D4FF","#7C3AED","#FF006E",
                                                   "#10B981","#F59E0B","#0EA5E9"])
            fig.update_layout(height=370, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)

    # ── Pivot heatmap ──────────────────────────────────────────────────────
    if len(cat_cols) >= 2 and num_cols:
        try:
            pivot = df.groupby([cat_cols[0], cat_cols[1]])[num_cols[0]].mean().unstack(fill_value=0)
            pivot = pivot.iloc[:min(15, pivot.shape[0]), :min(15, pivot.shape[1])]
            fig = px.imshow(pivot, template="plotly_dark", aspect="auto", text_auto=".1f",
                            title=f"Pivot Heatmap: {num_cols[0]} by {cat_cols[0]} × {cat_cols[1]}",
                            color_continuous_scale=["#0D1526","#7C3AED","#00D4FF"])
            fig.update_layout(height=420, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

    # ── Missing values ─────────────────────────────────────────────────────
    miss = df.isnull().sum()
    miss = miss[miss > 0]
    if not miss.empty:
        st.markdown("---")
        fig = px.bar(x=miss.values, y=miss.index, orientation="h",
                     template="plotly_dark", title="Missing Values by Column",
                     color=miss.values,
                     color_continuous_scale=["#7C3AED","#FF006E"],
                     labels={"x": "Missing Count", "y": "Column"})
        fig.update_layout(height=max(300, len(miss) * 38),
                          yaxis={"categoryorder": "total ascending"}, **_PLOTLY_DARK)
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

        html = f"""<html><head><title>DataViz Pro Dashboard</title>
        <style>body{{font-family:'Space Grotesk',sans-serif;background:#060B1A;color:#E2E8F0;padding:20px;}}
        h1{{background:#0A0F1E;color:#F0F6FF;padding:20px 30px;border-radius:12px;
             border-left:4px solid #00D4FF;font-size:1.4rem;}}
        .chart{{background:#0A0F1E;border:1px solid rgba(255,255,255,0.07);border-radius:12px;
                padding:20px;margin:15px 0;}}</style>
        </head><body>
        <h1>Auto Dashboard — {st.session_state.filename}</h1>
        {"".join(f'<div class="chart">{c}</div>' for c in charts_html)}
        </body></html>"""
        st.download_button("Download HTML", data=html.encode(),
                           file_name="dashboard.html", mime="text/html")
