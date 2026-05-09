import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io


def _header(title, sub):
    st.markdown(f"<div class='page-header'><h2>{title}</h2><p>{sub}</p></div>", unsafe_allow_html=True)


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
                             "Skew": f"{s.skew():.3f}", "Kurtosis": f"{s.kurtosis():.3f}"})
            else:
                row.update({"Min": "—", "Max": "—", "Mean": "—", "Std": "—", "Skew": "—", "Kurtosis": "—"})
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=450)

    with tab2:
        miss = df.isnull().sum()
        miss = miss[miss > 0].sort_values(ascending=False)
        if miss.empty:
            st.success("No missing values found in this dataset.")
        else:
            miss_df = pd.DataFrame({
                "Column": miss.index,
                "Count": miss.values,
                "Missing %": (miss.values / len(df) * 100).round(2)
            })
            st.dataframe(miss_df, use_container_width=True)

            fig, ax = plt.subplots(figsize=(10, max(3, len(miss) * 0.42)))
            colors = ["#EF4444" if p > 30 else "#F59E0B" if p > 10 else "#0EA5E9"
                      for p in miss_df["Missing %"][::-1]]
            bars = ax.barh(miss_df["Column"][::-1], miss_df["Missing %"][::-1], color=colors, height=0.6)
            for bar, val in zip(bars, miss_df["Missing %"][::-1]):
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                        f"{val:.1f}%", va="center", fontsize=9, color="#334155")
            ax.set_xlabel("Missing %", color="#64748B")
            ax.set_title("Missing Values by Column", fontsize=12, fontweight="bold", color="#0F172A")
            ax.tick_params(colors="#64748B")
            for spine in ax.spines.values():
                spine.set_edgecolor("#E2E8F0")
            ax.set_facecolor("#F8FAFC")
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_xlim(0, miss_df["Missing %"].max() * 1.18)
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close()

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

            skew = num_df.skew().sort_values()
            fig, ax = plt.subplots(figsize=(10, max(3, len(skew) * 0.42)))
            colors = ["#EF4444" if abs(v) > 1 else "#F59E0B" if abs(v) > 0.5 else "#10B981" for v in skew]
            ax.barh(skew.index, skew.values, color=colors, height=0.6)
            ax.axvline(0, color="#334155", linewidth=0.8, linestyle="--")
            ax.axvline(1, color="#EF4444", linewidth=0.6, linestyle=":")
            ax.axvline(-1, color="#EF4444", linewidth=0.6, linestyle=":")
            ax.set_title("Skewness by Column  (|skew| > 1 = highly skewed)", fontsize=11, fontweight="bold", color="#0F172A")
            ax.set_xlabel("Skewness", color="#64748B")
            ax.tick_params(colors="#64748B")
            for spine in ax.spines.values():
                spine.set_edgecolor("#E2E8F0")
            ax.set_facecolor("#F8FAFC")
            fig.patch.set_facecolor("#FFFFFF")
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close()

    with tab4:
        cat_df = df.select_dtypes(include=["object", "category"])
        if cat_df.empty:
            st.info("No categorical columns.")
        else:
            selected = st.selectbox("Column", cat_df.columns)
            vc = df[selected].value_counts().head(20)
            col_a, col_b = st.columns(2)
            with col_a:
                vc_df = pd.DataFrame({"Value": vc.index, "Count": vc.values, "Share %": (vc.values / len(df) * 100).round(2)})
                st.dataframe(vc_df, use_container_width=True)
            with col_b:
                fig, ax = plt.subplots(figsize=(6, max(3, len(vc) * 0.4)))
                palette = sns.color_palette("mako", len(vc))
                sns.barplot(x=vc.values, y=vc.index, palette=palette, ax=ax)
                ax.set_title(f"Top values: {selected}", fontsize=10, fontweight="bold", color="#0F172A")
                ax.set_xlabel("Count", color="#64748B")
                ax.tick_params(colors="#64748B")
                for spine in ax.spines.values():
                    spine.set_edgecolor("#E2E8F0")
                ax.set_facecolor("#F8FAFC")
                fig.patch.set_facecolor("#FFFFFF")
                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
                buf.seek(0)
                st.image(buf, use_container_width=True)
                plt.close()
