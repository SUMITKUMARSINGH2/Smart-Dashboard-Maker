import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io


def dashboard_page():
    st.markdown("""
    <div class="main-header">
        <h1>⚡ Auto Dashboard</h1>
        <p>One-click smart dashboard — automatically analyzes your data and builds the best charts.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    with st.expander("⚙️ Dashboard Options", expanded=False):
        template = st.selectbox("Theme", ["plotly_white", "plotly", "plotly_dark", "ggplot2", "seaborn"])
        top_n = st.slider("Top N categories in bar charts", 5, 20, 10)

    st.markdown("---")

    st.markdown("### 📌 KPI Cards")
    if num_cols:
        kpi_cols = num_cols[:min(6, len(num_cols))]
        cols = st.columns(min(6, len(kpi_cols)))
        for col, nc in zip(cols, kpi_cols):
            s = df[nc].dropna()
            col.metric(nc, f"{s.mean():.3g}", delta=f"σ={s.std():.3g}")

    st.markdown("---")

    if not num_cols and not cat_cols:
        st.info("No suitable columns found for auto dashboard.")
        return

    row1c1, row1c2 = st.columns(2)

    with row1c1:
        if num_cols:
            col = num_cols[0]
            fig = px.histogram(df, x=col, nbins=40, template=template,
                               title=f"Distribution: {col}",
                               color_discrete_sequence=["#667eea"])
            fig.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with row1c2:
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            fig = px.imshow(corr, text_auto=".1f", color_continuous_scale="RdBu_r",
                            zmin=-1, zmax=1, template=template,
                            title="Correlation Matrix", aspect="auto")
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)
        elif cat_cols:
            col = cat_cols[0]
            vc = df[col].value_counts().head(top_n)
            fig = px.bar(x=vc.values, y=vc.index, orientation="h",
                         template=template, title=f"Top {top_n}: {col}",
                         color=vc.values, color_continuous_scale="viridis")
            fig.update_layout(height=380, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    row2c1, row2c2 = st.columns(2)

    with row2c1:
        if cat_cols and num_cols:
            cat = cat_cols[0]
            num = num_cols[0]
            temp = df.groupby(cat)[num].mean().nlargest(top_n).reset_index()
            fig = px.bar(temp, x=num, y=cat, orientation="h",
                         title=f"Avg {num} by {cat} (Top {top_n})",
                         template=template, color=num,
                         color_continuous_scale="plasma",
                         text_auto=".2s")
            fig.update_layout(height=380, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        elif len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                             trendline="ols", template=template,
                             title=f"{num_cols[1]} vs {num_cols[0]}",
                             opacity=0.6, color_discrete_sequence=["#764ba2"])
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    with row2c2:
        if len(num_cols) >= 2:
            box_cols = num_cols[:min(5, len(num_cols))]
            melt = df[box_cols].melt(var_name="Column", value_name="Value")
            fig = px.box(melt, x="Column", y="Value", color="Column",
                         template=template, title="Distribution Overview (Box Plots)")
            fig.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        elif cat_cols:
            col = cat_cols[0]
            vc = df[col].value_counts().head(8)
            fig = px.pie(vc.reset_index(), values="count", names=col,
                         template=template, title=f"Breakdown: {col}",
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

    if len(cat_cols) >= 2 and num_cols:
        st.markdown("---")
        cat1, cat2, num = cat_cols[0], cat_cols[1], num_cols[0]
        try:
            pivot = df.groupby([cat1, cat2])[num].mean().unstack(fill_value=0)
            pivot = pivot.iloc[:min(15, pivot.shape[0]), :min(15, pivot.shape[1])]
            fig = px.imshow(pivot, template=template,
                            title=f"Pivot Heatmap: {num} by {cat1} × {cat2}",
                            color_continuous_scale="YlOrRd", aspect="auto",
                            text_auto=".1f")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

    miss = df.isnull().sum()
    miss = miss[miss > 0]
    if not miss.empty:
        st.markdown("---")
        st.markdown("### 🕳️ Missing Values Summary")
        fig = px.bar(
            x=miss.values, y=miss.index, orientation="h",
            labels={"x": "Missing Count", "y": "Column"},
            template=template, title="Missing Value Count by Column",
            color=miss.values, color_continuous_scale="Reds"
        )
        fig.update_layout(height=max(300, len(miss) * 40), yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    if st.button("📥 Export Dashboard as HTML"):
        charts = []
        if num_cols:
            f = px.histogram(df, x=num_cols[0], nbins=40, title=f"Distribution: {num_cols[0]}")
            charts.append(f)
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            f = px.imshow(corr, text_auto=".1f", title="Correlation Matrix",
                          color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
            charts.append(f)
        if cat_cols and num_cols:
            temp = df.groupby(cat_cols[0])[num_cols[0]].mean().nlargest(top_n).reset_index()
            f = px.bar(temp, x=num_cols[0], y=cat_cols[0], orientation="h",
                       title=f"Avg {num_cols[0]} by {cat_cols[0]}")
            charts.append(f)

        html_parts = ["<html><head><title>Auto Dashboard</title></head><body>",
                      "<h1 style='font-family:sans-serif;color:#333'>Auto Dashboard</h1>"]
        for ch in charts:
            html_parts.append(ch.to_html(full_html=False, include_plotlyjs="cdn"))
        html_parts.append("</body></html>")
        full_html = "\n".join(html_parts)
        st.download_button("💾 Download HTML Dashboard", data=full_html.encode(),
                           file_name="dashboard.html", mime="text/html")
