import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io


def profiling_page():
    st.markdown("""
    <div class="main-header">
        <h1>🔎 Data Profiling</h1>
        <p>Deep statistical profile of every column in your dataset.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
        return

    df = st.session_state.df

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Rows", f"{df.shape[0]:,}")
    m2.metric("Columns", df.shape[1])
    missing_pct = df.isnull().mean().mean() * 100
    m3.metric("Missing %", f"{missing_pct:.1f}%")
    m4.metric("Duplicates", f"{df.duplicated().sum():,}")
    mem = df.memory_usage(deep=True).sum()
    m5.metric("Memory", f"{mem/1024:.1f} KB" if mem < 1024*1024 else f"{mem/1024/1024:.1f} MB")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Column Profile", "📊 Missing Values", "🔢 Numeric Stats", "🔠 Categorical Stats"])

    with tab1:
        rows = []
        for col in df.columns:
            s = df[col]
            row = {
                "Column": col,
                "Type": str(s.dtype),
                "Non-Null": int(s.notnull().sum()),
                "Null %": f"{s.isnull().mean()*100:.1f}%",
                "Unique": int(s.nunique()),
                "Unique %": f"{s.nunique()/len(s)*100:.1f}%",
            }
            if pd.api.types.is_numeric_dtype(s):
                row["Min"] = f"{s.min():.3g}"
                row["Max"] = f"{s.max():.3g}"
                row["Mean"] = f"{s.mean():.3g}"
                row["Std"] = f"{s.std():.3g}"
                row["Skew"] = f"{s.skew():.3f}"
                row["Kurtosis"] = f"{s.kurtosis():.3f}"
            else:
                row["Min"] = row["Max"] = row["Mean"] = row["Std"] = row["Skew"] = row["Kurtosis"] = "—"
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

    with tab2:
        miss = df.isnull().sum()
        miss = miss[miss > 0].sort_values(ascending=False)
        if miss.empty:
            st.success("🎉 No missing values found in the dataset!")
        else:
            st.markdown(f"**{len(miss)} columns** have missing values:")
            miss_df = pd.DataFrame({
                "Column": miss.index,
                "Missing Count": miss.values,
                "Missing %": (miss.values / len(df) * 100).round(2)
            })
            st.dataframe(miss_df, use_container_width=True)

            fig, ax = plt.subplots(figsize=(10, max(3, len(miss) * 0.4)))
            colors = sns.color_palette("RdYlGn_r", len(miss))
            bars = ax.barh(miss_df["Column"][::-1], miss_df["Missing %"][::-1], color=colors[::-1])
            ax.set_xlabel("Missing %")
            ax.set_title("Missing Value % by Column", fontsize=13, fontweight="bold")
            for bar, val in zip(bars, miss_df["Missing %"][::-1]):
                ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                        f"{val:.1f}%", va="center", fontsize=9)
            ax.set_xlim(0, miss_df["Missing %"].max() * 1.15)
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close()

    with tab3:
        num_df = df.select_dtypes(include="number")
        if num_df.empty:
            st.info("No numeric columns in this dataset.")
        else:
            desc = num_df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
            desc["skewness"] = num_df.skew()
            desc["kurtosis"] = num_df.kurtosis()
            desc["cv"] = (num_df.std() / num_df.mean()).abs().round(4)
            st.dataframe(desc.round(4), use_container_width=True)

            st.markdown("#### 📊 Skewness Chart")
            skew = num_df.skew().sort_values()
            fig, ax = plt.subplots(figsize=(10, max(3, len(skew) * 0.45)))
            colors = ["#e74c3c" if v > 1 or v < -1 else "#2ecc71" if abs(v) < 0.5 else "#f39c12" for v in skew]
            ax.barh(skew.index, skew.values, color=colors)
            ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
            ax.axvline(1, color="#e74c3c", linewidth=0.6, linestyle=":")
            ax.axvline(-1, color="#e74c3c", linewidth=0.6, linestyle=":")
            ax.set_title("Skewness by Column (|skew| > 1 = highly skewed)", fontsize=12, fontweight="bold")
            ax.set_xlabel("Skewness")
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close()

    with tab4:
        cat_df = df.select_dtypes(include=["object", "category"])
        if cat_df.empty:
            st.info("No categorical columns found.")
        else:
            selected = st.selectbox("Select categorical column", cat_df.columns)
            vc = df[selected].value_counts().head(20)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Top values for `{selected}`**")
                vc_df = pd.DataFrame({"Value": vc.index, "Count": vc.values, "Share %": (vc.values / len(df) * 100).round(2)})
                st.dataframe(vc_df, use_container_width=True)
            with col_b:
                fig, ax = plt.subplots(figsize=(6, max(3, len(vc) * 0.45)))
                sns.barplot(x=vc.values, y=vc.index, palette="viridis", ax=ax)
                ax.set_title(f"Top values: {selected}", fontsize=11, fontweight="bold")
                ax.set_xlabel("Count")
                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
                buf.seek(0)
                st.image(buf, use_container_width=True)
                plt.close()
