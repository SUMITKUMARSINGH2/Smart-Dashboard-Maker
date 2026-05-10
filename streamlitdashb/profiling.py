import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from styles import DARK_CSS, section_header, kpi_row_html, badge

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,21,40,1)",
    font=dict(family="Space Grotesk", color="#E2E8F0"),
    margin=dict(l=20, r=20, t=40, b=20),
)

def data_profiling():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header("◎", "Data Profiling", "Deep-dive into every column's statistics and distribution"), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data uploaded yet. Please upload a file first.")
        return

    df = st.session_state["clean_data"]
    total = len(df)
    missing_total = int(df.isnull().sum().sum())
    dups = int(df.duplicated().sum())
    mem_mb = round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)

    st.markdown(kpi_row_html([
        ("Rows", f"{total:,}"),
        ("Columns", df.shape[1]),
        ("Missing", f"{missing_total:,}"),
        ("Duplicates", dups),
        ("Mem (MB)", mem_mb),
        ("Missing %", f"{round(missing_total/(total*df.shape[1])*100,1) if total else 0}%"),
    ]), unsafe_allow_html=True)

    # Missing heatmap
    cols_with_nulls = [c for c in df.columns if df[c].isnull().any()]
    if cols_with_nulls:
        with st.expander("🕳️ Missing Values Heatmap", expanded=False):
            null_pcts = [(c, round(df[c].isnull().sum() / total * 100, 1)) for c in cols_with_nulls]
            null_pcts.sort(key=lambda x: -x[1])
            ndf = pd.DataFrame(null_pcts, columns=["Column", "Missing %"])
            fig = px.bar(ndf, x="Missing %", y="Column", orientation="h",
                         color="Missing %", color_continuous_scale="Plasma",
                         title="Missing % per Column")
            fig.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)

    # Per-column profiling
    st.markdown('<div style="font-weight:600;color:#E2E8F0;margin:1rem 0 .75rem;">Column Profiles</div>', unsafe_allow_html=True)

    col_filter = st.selectbox("Show column", ["— all —"] + list(df.columns))
    show_cols = [col_filter] if col_filter != "— all —" else list(df.columns)

    for col in show_cols:
        series = df[col]
        dtype = str(series.dtype)
        n_miss = int(series.isna().sum())
        n_uniq = int(series.nunique())
        miss_pct = round(n_miss / total * 100, 1)

        is_num = pd.api.types.is_numeric_dtype(series)

        with st.expander(f"**{col}** — {dtype} · {n_uniq} unique · {miss_pct}% missing", expanded=False):
            c1, c2 = st.columns([1, 2])
            with c1:
                if is_num:
                    s = series.dropna()
                    stats = {
                        "Count": f"{len(s):,}",
                        "Min": round(float(s.min()), 4) if len(s) else "—",
                        "Max": round(float(s.max()), 4) if len(s) else "—",
                        "Mean": round(float(s.mean()), 4) if len(s) else "—",
                        "Median": round(float(s.median()), 4) if len(s) else "—",
                        "Std Dev": round(float(s.std()), 4) if len(s) else "—",
                        "Skewness": round(float(s.skew()), 4) if len(s) else "—",
                        "Kurtosis": round(float(s.kurt()), 4) if len(s) else "—",
                        "Zeros": int((s == 0).sum()),
                        "Missing": f"{n_miss:,} ({miss_pct}%)",
                    }
                else:
                    vc = series.value_counts()
                    stats = {
                        "Count": f"{total:,}",
                        "Unique": n_uniq,
                        "Missing": f"{n_miss:,} ({miss_pct}%)",
                        "Top Value": str(vc.index[0]) if len(vc) else "—",
                        "Top Freq": f"{int(vc.iloc[0]):,}" if len(vc) else "—",
                        "Top %": f"{round(vc.iloc[0]/total*100,1)}%" if len(vc) else "—",
                    }

                for k, v in stats.items():
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:.25rem 0;
                                border-bottom:1px solid #1E293B;font-size:.82rem;">
                      <span style="color:#94A3B8;">{k}</span>
                      <span style="font-family:monospace;color:#E2E8F0;">{v}</span>
                    </div>""", unsafe_allow_html=True)

            with c2:
                if is_num and len(series.dropna()) > 1:
                    s = series.dropna()
                    fig = px.histogram(pd.DataFrame({"value": s}), x="value",
                                       nbins=min(40, n_uniq),
                                       color_discrete_sequence=["#00D4FF"])
                    fig.update_layout(**PLOTLY_THEME, title=f"Distribution of {col}")
                    fig.update_traces(marker_line_width=0)
                    st.plotly_chart(fig, use_container_width=True, key=f"hist_{col}")
                elif not is_num:
                    vc = series.value_counts().head(15)
                    fig = px.bar(x=vc.values, y=vc.index.astype(str),
                                 orientation="h",
                                 color_discrete_sequence=["#7C3AED"],
                                 labels={"x": "Count", "y": col})
                    fig.update_layout(**PLOTLY_THEME, title=f"Top values in {col}")
                    st.plotly_chart(fig, use_container_width=True, key=f"bar_{col}")
