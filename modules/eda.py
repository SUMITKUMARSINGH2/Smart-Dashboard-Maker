import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
from scipy import stats as scipy_stats


def eda_page():
    st.markdown("""
    <div class="main-header">
        <h1>📈 EDA & Statistics</h1>
        <p>Explore relationships, distributions, and statistical patterns in your data.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔥 Correlation", "📊 Distributions", "📦 Box Plots", "👯 Pair Plot", "🔢 Hypothesis Tests", "📐 Scatter Analysis"
    ])

    with tab1:
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns for correlation analysis.")
        else:
            sel_cols = st.multiselect("Select columns (leave empty = all numeric)", num_cols, default=num_cols[:min(12, len(num_cols))])
            if not sel_cols:
                sel_cols = num_cols
            method = st.radio("Correlation method", ["pearson", "spearman", "kendall"], horizontal=True)
            corr = df[sel_cols].corr(method=method)

            fig, ax = plt.subplots(figsize=(max(8, len(sel_cols)), max(6, len(sel_cols) * 0.8)))
            mask = np.triu(np.ones_like(corr, dtype=bool))
            sns.heatmap(
                corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, vmin=-1, vmax=1, ax=ax,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
                annot_kws={"size": max(7, 10 - len(sel_cols) // 3)}
            )
            ax.set_title(f"{method.capitalize()} Correlation Matrix", fontsize=14, fontweight="bold", pad=15)
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close()

            st.markdown("#### 🏆 Top Correlations")
            pairs = corr.unstack().reset_index()
            pairs.columns = ["Col A", "Col B", "Correlation"]
            pairs = pairs[pairs["Col A"] != pairs["Col B"]]
            pairs["abs"] = pairs["Correlation"].abs()
            top = pairs.sort_values("abs", ascending=False).drop_duplicates(subset=["abs"]).head(15)
            top = top.drop("abs", axis=1).round(4)
            st.dataframe(top, use_container_width=True)

    with tab2:
        if not num_cols:
            st.info("No numeric columns for distribution analysis.")
        else:
            col = st.selectbox("Select column", num_cols)
            bins = st.slider("Bins", 10, 100, 30)
            show_kde = st.checkbox("Show KDE curve", True)
            show_rug = st.checkbox("Show rug plot", False)

            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            data = df[col].dropna()

            sns.histplot(data, bins=bins, kde=show_kde, ax=axes[0],
                         color="#667eea", edgecolor="white", alpha=0.8)
            if show_rug:
                axes[0].plot(data, np.zeros_like(data) - axes[0].get_ylim()[1]*0.02,
                             "|", color="#764ba2", alpha=0.3, markersize=4)
            axes[0].set_title(f"Distribution of {col}", fontweight="bold")
            axes[0].set_xlabel(col)

            (mu, sigma) = scipy_stats.norm.fit(data)
            x = np.linspace(data.min(), data.max(), 200)
            p = scipy_stats.norm.pdf(x, mu, sigma)
            axes[1].plot(x, p, "#667eea", linewidth=2, label="Normal fit")
            sns.kdeplot(data, ax=axes[1], color="#f093fb", linewidth=2, label="KDE")
            axes[1].set_title(f"KDE vs Normal Fit — {col}", fontweight="bold")
            axes[1].legend()

            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Mean", f"{data.mean():.4g}")
            c2.metric("Median", f"{data.median():.4g}")
            c3.metric("Skewness", f"{data.skew():.4f}")
            c4.metric("Kurtosis", f"{data.kurtosis():.4f}")

            stat, p_val = scipy_stats.shapiro(data.sample(min(5000, len(data)), random_state=42))
            if p_val < 0.05:
                st.warning(f"Shapiro-Wilk test: p={p_val:.4f} → Data is **NOT** normally distributed")
            else:
                st.success(f"Shapiro-Wilk test: p={p_val:.4f} → Data appears normally distributed")

    with tab3:
        if not num_cols:
            st.info("No numeric columns.")
        else:
            sel = st.multiselect("Columns for box plots", num_cols, default=num_cols[:min(6, len(num_cols))])
            group_col = st.selectbox("Group by (optional)", ["None"] + cat_cols)
            if sel:
                if group_col != "None" and group_col:
                    fig = px.box(df, y=sel[0] if len(sel) == 1 else None,
                                 x=group_col if group_col != "None" else None,
                                 color=group_col if group_col != "None" else None,
                                 template="plotly_white")
                    if len(sel) > 1:
                        fig = px.box(df.melt(value_vars=sel, id_vars=[group_col] if group_col != "None" else []),
                                     x="variable", y="value",
                                     color=group_col if group_col != "None" else None,
                                     template="plotly_white")
                else:
                    melt = df[sel].melt(var_name="Column", value_name="Value")
                    fig = px.box(melt, x="Column", y="Value", color="Column", template="plotly_white",
                                 title="Box Plot Comparison")
                fig.update_layout(height=500, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns.")
        else:
            sel_pp = st.multiselect("Columns for pair plot (2–6 recommended)", num_cols,
                                    default=num_cols[:min(4, len(num_cols))])
            hue_pp = st.selectbox("Color by", ["None"] + cat_cols, key="pp_hue")
            if sel_pp and len(sel_pp) >= 2:
                with st.spinner("Generating pair plot..."):
                    fig, ax = plt.subplots(figsize=(10, 8))
                    plt.close()
                    hue_val = hue_pp if hue_pp != "None" else None
                    pp_df = df[sel_pp + ([hue_val] if hue_val else [])].dropna()
                    if len(pp_df) > 2000:
                        pp_df = pp_df.sample(2000, random_state=42)
                    g = sns.pairplot(pp_df, hue=hue_val, plot_kws={"alpha": 0.5, "s": 20},
                                     palette="husl", corner=False)
                    g.fig.suptitle("Pair Plot", y=1.02, fontsize=13, fontweight="bold")
                    buf = io.BytesIO()
                    g.fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
                    buf.seek(0)
                    st.image(buf, use_container_width=True)
                    plt.close("all")

    with tab5:
        st.markdown("#### 🧪 Statistical Hypothesis Tests")
        test_type = st.selectbox("Test", [
            "t-test (compare 2 numeric groups)",
            "Chi-square (categorical independence)",
            "ANOVA (compare 3+ groups)",
            "Mann-Whitney U (non-parametric)"
        ])

        if test_type == "t-test (compare 2 numeric groups)":
            if cat_cols and num_cols:
                grp_col = st.selectbox("Group column (2 categories)", cat_cols)
                val_col = st.selectbox("Value column", num_cols)
                groups = df[grp_col].dropna().unique()
                if len(groups) == 2:
                    g1 = df[df[grp_col] == groups[0]][val_col].dropna()
                    g2 = df[df[grp_col] == groups[1]][val_col].dropna()
                    t_stat, p_val = scipy_stats.ttest_ind(g1, g2)
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("t-statistic", f"{t_stat:.4f}")
                    col_b.metric("p-value", f"{p_val:.6f}")
                    col_c.metric("Significant (α=0.05)", "Yes ✅" if p_val < 0.05 else "No ❌")
                else:
                    st.warning("Please select a column with exactly 2 unique values.")
            else:
                st.info("Need both numeric and categorical columns.")

        elif test_type == "Chi-square (categorical independence)":
            if len(cat_cols) >= 2:
                c1_sel = st.selectbox("Column A", cat_cols, key="chi_a")
                c2_sel = st.selectbox("Column B", cat_cols, key="chi_b")
                if c1_sel != c2_sel:
                    ct = pd.crosstab(df[c1_sel], df[c2_sel])
                    chi2, p_val, dof, _ = scipy_stats.chi2_contingency(ct)
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Chi² statistic", f"{chi2:.4f}")
                    col_b.metric("p-value", f"{p_val:.6f}")
                    col_c.metric("Significant (α=0.05)", "Yes ✅" if p_val < 0.05 else "No ❌")
                    st.dataframe(ct, use_container_width=True)
            else:
                st.info("Need at least 2 categorical columns.")

        elif test_type == "ANOVA (compare 3+ groups)":
            if cat_cols and num_cols:
                grp_col = st.selectbox("Group column", cat_cols, key="anova_grp")
                val_col = st.selectbox("Value column", num_cols, key="anova_val")
                groups = [g.dropna().values for _, g in df.groupby(grp_col)[val_col]]
                if len(groups) >= 3:
                    f_stat, p_val = scipy_stats.f_oneway(*groups)
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("F-statistic", f"{f_stat:.4f}")
                    col_b.metric("p-value", f"{p_val:.6f}")
                    col_c.metric("Significant (α=0.05)", "Yes ✅" if p_val < 0.05 else "No ❌")
                else:
                    st.warning("Need at least 3 groups.")
            else:
                st.info("Need both numeric and categorical columns.")

        elif test_type == "Mann-Whitney U (non-parametric)":
            if cat_cols and num_cols:
                grp_col = st.selectbox("Group column (2 categories)", cat_cols, key="mw_grp")
                val_col = st.selectbox("Value column", num_cols, key="mw_val")
                groups = df[grp_col].dropna().unique()
                if len(groups) == 2:
                    g1 = df[df[grp_col] == groups[0]][val_col].dropna()
                    g2 = df[df[grp_col] == groups[1]][val_col].dropna()
                    u_stat, p_val = scipy_stats.mannwhitneyu(g1, g2)
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("U-statistic", f"{u_stat:.4f}")
                    col_b.metric("p-value", f"{p_val:.6f}")
                    col_c.metric("Significant (α=0.05)", "Yes ✅" if p_val < 0.05 else "No ❌")
                else:
                    st.warning("Please select a column with exactly 2 unique values.")

    with tab6:
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns.")
        else:
            x_col = st.selectbox("X axis", num_cols, key="sc_x")
            y_col = st.selectbox("Y axis", [c for c in num_cols if c != x_col], key="sc_y")
            color_col = st.selectbox("Color by", ["None"] + cat_cols + num_cols, key="sc_c")
            size_col = st.selectbox("Size by (numeric)", ["None"] + num_cols, key="sc_s")
            trend = st.checkbox("Add trend line (OLS)", True)

            color = color_col if color_col != "None" else None
            size = size_col if size_col != "None" else None
            tl = "ols" if trend else None
            fig = px.scatter(
                df, x=x_col, y=y_col, color=color, size=size,
                trendline=tl, template="plotly_white", opacity=0.7,
                title=f"{y_col} vs {x_col}",
                color_continuous_scale="viridis"
            )
            fig.update_layout(height=520)
            st.plotly_chart(fig, use_container_width=True)

            if trend:
                corr_val = df[[x_col, y_col]].dropna().corr().iloc[0, 1]
                st.metric("Pearson Correlation", f"{corr_val:.4f}")
