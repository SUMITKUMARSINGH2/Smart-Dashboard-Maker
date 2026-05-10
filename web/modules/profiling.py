import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io


_DARK_STYLE = {
    "axes.facecolor": "#0A0F1E",
    "figure.facecolor": "#0A0F1E",
    "axes.edgecolor": "#1E293B",
    "text.color": "#94A3B8",
    "axes.labelcolor": "#64748B",
    "xtick.color": "#64748B",
    "ytick.color": "#64748B",
    "grid.color": "#1E293B",
}


@st.cache_data(show_spinner=False)
def _build_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        row = {
            "Column": col,
            "Dtype": str(s.dtype),
            "Non-Null": int(s.notnull().sum()),
            "Null %": f"{s.isnull().mean()*100:.1f}%",
            "Unique": int(s.nunique()),
            "Unique %": f"{s.nunique()/max(len(s),1)*100:.1f}%",
        }
        if pd.api.types.is_numeric_dtype(s):
            row.update({"Min": f"{s.min():.3g}", "Max": f"{s.max():.3g}",
                         "Mean": f"{s.mean():.3g}", "Std": f"{s.std():.3g}",
                         "Skew": f"{s.skew():.3f}", "Kurt": f"{s.kurtosis():.3f}"})
        else:
            row.update({"Min": "—", "Max": "—", "Mean": "—", "Std": "—",
                        "Skew": "—", "Kurt": "—"})
        rows.append(row)
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def _missing_chart(miss_vals: dict) -> bytes:
    miss_df = pd.DataFrame(list(miss_vals.items()), columns=["Column", "Missing %"])
    miss_df = miss_df.sort_values("Missing %", ascending=False)
    with sns.axes_style("dark", _DARK_STYLE):
        fig, ax = plt.subplots(figsize=(10, max(3, len(miss_df) * 0.42)))
        fig.patch.set_facecolor("#0A0F1E")
        colors = ["#FF006E" if p > 30 else "#F59E0B" if p > 10 else "#00D4FF"
                  for p in miss_df["Missing %"]]
        ax.barh(miss_df["Column"][::-1], miss_df["Missing %"][::-1],
                color=colors[::-1], height=0.6)
        for i, (_, row) in enumerate(miss_df[::-1].iterrows()):
            ax.text(row["Missing %"] + 0.3, i, f"{row['Missing %']:.1f}%",
                    va="center", fontsize=9, color="#94A3B8")
        ax.set_xlabel("Missing %", color="#64748B")
        ax.set_title("Missing Values by Column", fontsize=12, fontweight="bold", color="#E2E8F0")
        ax.tick_params(colors="#64748B")
        for sp in ax.spines.values():
            sp.set_edgecolor("#1E293B")
        ax.set_facecolor("#0A0F1E")
        ax.set_xlim(0, miss_df["Missing %"].max() * 1.18)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#0A0F1E")
        buf.seek(0)
        plt.close()
        return buf.read()


def _header(title, sub):
    st.markdown(f"""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// data profiling</div>
        <h2>{title}</h2>
        <div class='page-header-bar'></div>
        <p>{sub}</p>
    </div>""", unsafe_allow_html=True)


def profiling_page():
    _header("Data Profiling", "Per-column statistics, missing value analysis, and distribution insights")

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Rows", f"{df.shape[0]:,}")
    m2.metric("Columns", df.shape[1])
    m3.metric("Missing %", f"{df.isnull().mean().mean()*100:.1f}%")
    m4.metric("Duplicates", f"{df.duplicated().sum():,}")
    mem = df.memory_usage(deep=True).sum()
    m5.metric("Memory", f"{mem/1024:.1f} KB" if mem < 1024**2 else f"{mem/1024/1024:.1f} MB")

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Column Profile", "Missing Values", "Numeric Stats", "Categorical"])

    with tab1:
        profile_df = _build_profile(df)
        st.dataframe(profile_df, use_container_width=True, height=450)

    with tab2:
        miss = df.isnull().sum()
        miss = miss[miss > 0].sort_values(ascending=False)
        if miss.empty:
            st.success("No missing values found in this dataset.")
        else:
            miss_pct = {col: round(cnt / len(df) * 100, 2) for col, cnt in miss.items()}
            miss_df = pd.DataFrame({
                "Column": list(miss_pct.keys()),
                "Count": miss.values,
                "Missing %": list(miss_pct.values()),
            })
            st.dataframe(miss_df, use_container_width=True)
            img = _missing_chart(miss_pct)
            st.image(img, use_container_width=True)

    with tab3:
        num_df = df.select_dtypes(include="number")
        if num_df.empty:
            st.info("No numeric columns.")
        else:
            desc = num_df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
            desc["skewness"] = num_df.skew()
            desc["kurtosis"] = num_df.kurtosis()
            desc["cv"] = (num_df.std() / num_df.mean()).abs().round(4)
            st.dataframe(desc.round(4), use_container_width=True, height=400)

    with tab4:
        cat_df = df.select_dtypes(include=["object", "category"])
        if cat_df.empty:
            st.info("No categorical columns.")
        else:
            selected = st.selectbox("Column", cat_df.columns)
            vc = df[selected].value_counts().head(20)
            col_a, col_b = st.columns(2)
            with col_a:
                vc_df = pd.DataFrame({
                    "Value": vc.index,
                    "Count": vc.values,
                    "Share %": (vc.values / len(df) * 100).round(2),
                })
                st.dataframe(vc_df, use_container_width=True)
            with col_b:
                with sns.axes_style("dark", _DARK_STYLE):
                    fig, ax = plt.subplots(figsize=(6, max(3, len(vc) * 0.4)))
                    fig.patch.set_facecolor("#0A0F1E")
                    ax.set_facecolor("#0A0F1E")
                    palette = sns.color_palette(["#00D4FF", "#7C3AED", "#FF006E",
                                                  "#10B981", "#F59E0B", "#0EA5E9",
                                                  "#A855F7", "#14B8A6", "#F97316",
                                                  "#EC4899"], len(vc))
                    sns.barplot(x=vc.values, y=vc.index, palette=palette, ax=ax)
                    ax.set_title(f"Top values: {selected}", fontsize=10,
                                 fontweight="bold", color="#E2E8F0")
                    ax.set_xlabel("Count", color="#64748B")
                    ax.tick_params(colors="#64748B")
                    for sp in ax.spines.values():
                        sp.set_edgecolor("#1E293B")
                    plt.tight_layout()
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#0A0F1E")
                    buf.seek(0)
                    st.image(buf, use_container_width=True)
                    plt.close()
