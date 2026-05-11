import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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

def eda_page():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header("∿", "EDA & Statistics", "Exploratory analysis — correlations, distributions, and hypothesis testing"), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data uploaded yet. Please upload a file first.")
        return

    df = st.session_state["clean_data"]
    num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()

    if not num_cols:
        st.warning("No numeric columns found for EDA.")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Distributions", "🔗 Correlations", "📦 Box Plots", "🔵 Scatter", "📐 Stats Test"])

    # ── Distributions ──────────────────────────────────────────────────────────
    with tab1:
        col_sel = st.selectbox("Select column", num_cols, key="eda_dist_col")
        bins_sel = st.slider("Bins", 10, 100, 30, key="eda_bins")
        c1, c2 = st.columns(2)
        with c1:
            s = df[col_sel].dropna()
            fig = px.histogram(pd.DataFrame({"value": s}), x="value", nbins=bins_sel,
                               color_discrete_sequence=["#00D4FF"],
                               title=f"Histogram — {col_sel}")
            fig.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Box(y=df[col_sel].dropna(), name=col_sel,
                                  marker_color="#7C3AED", boxmean=True))
            fig2.update_layout(**PLOTLY_THEME, title=f"Box Plot — {col_sel}")
            st.plotly_chart(fig2, use_container_width=True)

        if cat_cols:
            group_col = st.selectbox("Group by category (optional)", ["— none —"] + cat_cols, key="eda_group")
            if group_col != "— none —":
                fig3 = px.histogram(df, x=col_sel, color=group_col, nbins=bins_sel,
                                    barmode="overlay", opacity=.7,
                                    color_discrete_sequence=["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B"],
                                    title=f"{col_sel} by {group_col}")
                fig3.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig3, use_container_width=True)

    # ── Correlations ───────────────────────────────────────────────────────────
    with tab2:
        method = st.radio("Correlation method", ["pearson", "spearman", "kendall"], horizontal=True)
        min_corr = st.slider("Min absolute correlation", 0.0, 1.0, 0.0, 0.05)

        corr = df[num_cols].corr(method=method)
        mask = (corr.abs() >= min_corr)
        corr_disp = corr.where(mask)

        fig = px.imshow(corr_disp, color_continuous_scale="RdBu_r",
                        zmin=-1, zmax=1, text_auto=".2f",
                        title=f"{method.capitalize()} Correlation Matrix",
                        aspect="auto")
        fig.update_layout(**PLOTLY_THEME)
        fig.update_traces(textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)

        # Top correlations
        corr_pairs = []
        for i in range(len(num_cols)):
            for j in range(i+1, len(num_cols)):
                corr_pairs.append((num_cols[i], num_cols[j], round(float(corr.iloc[i,j]), 4)))
        corr_df = pd.DataFrame(corr_pairs, columns=["Column A", "Column B", "Correlation"])
        corr_df = corr_df.reindex(corr_df["Correlation"].abs().sort_values(ascending=False).index)

        st.markdown('<div style="font-weight:600;color:#E2E8F0;margin:.75rem 0 .5rem;">Top Pairs</div>', unsafe_allow_html=True)
        st.dataframe(corr_df.head(20), use_container_width=True, hide_index=True)

    # ── Box Plots ──────────────────────────────────────────────────────────────
    with tab3:
        cols_sel = st.multiselect("Numeric columns", num_cols, default=num_cols[:min(6, len(num_cols))])
        if cols_sel:
            if cat_cols:
                color_by = st.selectbox("Color by", ["— none —"] + cat_cols, key="box_color")
            else:
                color_by = "— none —"

            fig = go.Figure()
            palette = ["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444"]
            for i, c in enumerate(cols_sel):
                fig.add_trace(go.Box(
                    y=df[c].dropna(), name=c,
                    marker_color=palette[i % len(palette)],
                    boxmean=True
                ))
            fig.update_layout(**PLOTLY_THEME, title="Box Plots", boxmode="group")
            st.plotly_chart(fig, use_container_width=True)

    # ── Scatter ────────────────────────────────────────────────────────────────
    with tab4:
        c1, c2, c3 = st.columns(3)
        with c1:
            x_col = st.selectbox("X axis", num_cols, key="scatter_x")
        with c2:
            y_col = st.selectbox("Y axis", num_cols[::-1], key="scatter_y")
        with c3:
            color_col = st.selectbox("Color by", ["— none —"] + cat_cols + num_cols, key="scatter_color")

        trendline = st.checkbox("Show trendline (OLS)", value=True)

        fig = px.scatter(
            df, x=x_col, y=y_col,
            color=None if color_col == "— none —" else color_col,
            trendline="ols" if trendline else None,
            opacity=.7,
            color_discrete_sequence=["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B"],
            title=f"{x_col} vs {y_col}"
        )
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)

        # Correlation value
        if x_col != y_col:
            r = df[[x_col, y_col]].dropna().corr().iloc[0, 1]
            strength = "strong" if abs(r) > .7 else "moderate" if abs(r) > .4 else "weak"
            direction = "positive" if r > 0 else "negative"
            st.markdown(f"""
            <div style="background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.15);
                        border-radius:8px;padding:.75rem 1rem;font-size:.88rem;">
              <b style="color:#00D4FF;">Pearson r = {r:.4f}</b>
              <span style="color:#94A3B8;"> — {strength} {direction} correlation</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Stats Test ─────────────────────────────────────────────────────────────
    with tab5:
        st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">Normality Test (Shapiro-Wilk)</div>', unsafe_allow_html=True)
        test_col = st.selectbox("Column to test", num_cols, key="norm_test_col")
        if st.button("Run Normality Test"):
            from scipy import stats as sp
            s = df[test_col].dropna()
            if len(s) > 5000:
                s = s.sample(5000, random_state=42)
            stat, p = sp.shapiro(s)
            normal = p > 0.05
            color = "#10B981" if normal else "#EF4444"
            result = "NORMAL (fail to reject H₀)" if normal else "NOT NORMAL (reject H₀)"
            st.markdown(f"""
            <div style="background:rgba(13,21,40,1);border:1px solid #1E293B;border-radius:8px;padding:1rem 1.25rem;">
              <div style="font-size:.85rem;color:#94A3B8;">Shapiro-Wilk test on <b style="color:#E2E8F0;">{test_col}</b> (n={len(s):,})</div>
              <div style="margin-top:.5rem;">
                <span style="font-family:monospace;color:#E2E8F0;">W = {stat:.6f}</span> &nbsp;
                <span style="font-family:monospace;color:#E2E8F0;">p = {p:.6f}</span>
              </div>
              <div style="margin-top:.5rem;font-weight:600;color:{color};">
                Distribution is {result}
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="font-weight:600;color:#E2E8F0;margin:1.25rem 0 .75rem;">T-Test (Two Columns)</div>', unsafe_allow_html=True)
        tc1 = st.selectbox("Column 1", num_cols, key="ttest_c1")
        tc2 = st.selectbox("Column 2", num_cols[::-1], key="ttest_c2")
        alpha = st.slider("Significance level (α)", 0.01, 0.10, 0.05, 0.01)
        if st.button("Run T-Test"):
            from scipy import stats as sp
            s1 = df[tc1].dropna()
            s2 = df[tc2].dropna()
            stat, p = sp.ttest_ind(s1, s2)
            sig = p < alpha
            color = "#10B981" if sig else "#EF4444"
            st.markdown(f"""
            <div style="background:rgba(13,21,40,1);border:1px solid #1E293B;border-radius:8px;padding:1rem 1.25rem;">
              <div style="font-size:.85rem;color:#94A3B8;">Independent samples t-test: <b style="color:#E2E8F0;">{tc1}</b> vs <b style="color:#E2E8F0;">{tc2}</b></div>
              <div style="margin-top:.5rem;">
                <span style="font-family:monospace;color:#E2E8F0;">t = {stat:.6f}</span> &nbsp;
                <span style="font-family:monospace;color:#E2E8F0;">p = {p:.6f}</span>
              </div>
              <div style="margin-top:.5rem;font-weight:600;color:{color};">
                {"Statistically SIGNIFICANT difference (p < α)" if sig else "NOT statistically significant (p ≥ α)"}
              </div>
            </div>
            """, unsafe_allow_html=True)
