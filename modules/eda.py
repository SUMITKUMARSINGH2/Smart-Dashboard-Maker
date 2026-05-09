import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
from scipy import stats as scipy_stats


def _header(title, sub):
    st.markdown(f"<div class='page-header'><h2>{title}</h2><p>{sub}</p></div>", unsafe_allow_html=True)


def eda_page():
    _header("EDA & Statistics", "Correlation analysis, distributions, pair plots, and hypothesis testing")

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Correlation Heatmap", "Distributions", "Box Plots", "Pair Plot", "Hypothesis Tests", "Scatter Analysis"
    ])

    SEABORN_STYLE = {"axes.facecolor": "#F8FAFC", "figure.facecolor": "#FFFFFF",
                     "axes.edgecolor": "#E2E8F0", "text.color": "#334155",
                     "axes.labelcolor": "#64748B", "xtick.color": "#64748B", "ytick.color": "#64748B",
                     "grid.color": "#F1F5F9"}

    with tab1:
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns.")
        else:
            sel = st.multiselect("Columns (empty = all numeric)", num_cols, default=num_cols[:min(12, len(num_cols))])
            if not sel: sel = num_cols
            method = st.radio("Method", ["pearson", "spearman", "kendall"], horizontal=True)
            corr = df[sel].corr(method=method)

            with sns.axes_style("white", SEABORN_STYLE):
                fig, ax = plt.subplots(figsize=(max(8, len(sel)), max(6, len(sel) * 0.8)))
                mask = np.triu(np.ones_like(corr, dtype=bool))
                cmap = sns.diverging_palette(220, 10, as_cmap=True)
                sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap=cmap,
                            center=0, vmin=-1, vmax=1, ax=ax, square=True,
                            linewidths=0.5, linecolor="#E2E8F0",
                            cbar_kws={"shrink": 0.8},
                            annot_kws={"size": max(7, 10 - len(sel)//3)})
                ax.set_title(f"{method.capitalize()} Correlation Matrix", fontsize=13,
                             fontweight="bold", color="#0F172A", pad=12)
                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#FFFFFF")
                buf.seek(0)
                st.image(buf, use_container_width=True)
                plt.close()

            st.markdown("**Top correlations**")
            pairs = corr.unstack().reset_index()
            pairs.columns = ["Col A", "Col B", "Correlation"]
            pairs = pairs[pairs["Col A"] != pairs["Col B"]]
            pairs["abs"] = pairs["Correlation"].abs()
            top = pairs.sort_values("abs", ascending=False).drop_duplicates("abs").head(15).drop("abs", axis=1).round(4)
            st.dataframe(top, use_container_width=True)

    with tab2:
        if not num_cols:
            st.info("No numeric columns.")
        else:
            col = st.selectbox("Column", num_cols)
            c1, c2 = st.columns(2)
            bins = c1.slider("Bins", 10, 100, 30)
            show_kde = c2.checkbox("Show KDE", True)

            data = df[col].dropna()
            with sns.axes_style("white", SEABORN_STYLE):
                fig, axes = plt.subplots(1, 2, figsize=(14, 5))

                sns.histplot(data, bins=bins, kde=show_kde, ax=axes[0],
                             color="#0EA5E9", edgecolor="white", alpha=0.85)
                axes[0].set_title(f"Distribution — {col}", fontweight="bold", color="#0F172A")
                axes[0].set_xlabel(col, color="#64748B")

                mu, sigma = scipy_stats.norm.fit(data)
                x = np.linspace(data.min(), data.max(), 200)
                axes[1].plot(x, scipy_stats.norm.pdf(x, mu, sigma), "#F59E0B", linewidth=2, label="Normal fit")
                sns.kdeplot(data, ax=axes[1], color="#0EA5E9", linewidth=2, label="KDE")
                axes[1].set_title(f"KDE vs Normal Fit — {col}", fontweight="bold", color="#0F172A")
                axes[1].legend()

                plt.tight_layout()
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#FFFFFF")
                buf.seek(0)
                st.image(buf, use_container_width=True)
                plt.close()

            ca, cb, cc, cd = st.columns(4)
            ca.metric("Mean", f"{data.mean():.4g}")
            cb.metric("Median", f"{data.median():.4g}")
            cc.metric("Skewness", f"{data.skew():.4f}")
            cd.metric("Kurtosis", f"{data.kurtosis():.4f}")

            stat, p_val = scipy_stats.shapiro(data.sample(min(5000, len(data)), random_state=42))
            if p_val < 0.05:
                st.warning(f"Shapiro-Wilk: p={p_val:.4f} → Data is **not** normally distributed")
            else:
                st.success(f"Shapiro-Wilk: p={p_val:.4f} → Consistent with normal distribution")

    with tab3:
        if not num_cols:
            st.info("No numeric columns.")
        else:
            sel = st.multiselect("Columns", num_cols, default=num_cols[:min(6, len(num_cols))])
            group_col = st.selectbox("Group by", ["None"] + cat_cols)
            if sel:
                g = group_col if group_col != "None" else None
                if g and len(sel) == 1:
                    fig = px.box(df, x=g, y=sel[0], color=g, template="plotly_white", points="outliers")
                elif g and len(sel) > 1:
                    fig = px.box(df.melt(value_vars=sel, id_vars=[g]), x="variable", y="value",
                                 color=g, template="plotly_white")
                else:
                    fig = px.box(df[sel].melt(var_name="Column", value_name="Value"),
                                 x="Column", y="Value", color="Column", template="plotly_white")
                fig.update_layout(height=500, showlegend=True,
                                  plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF")
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns.")
        else:
            sel_pp = st.multiselect("Columns (2–5 recommended)", num_cols, default=num_cols[:min(4, len(num_cols))])
            hue_pp = st.selectbox("Color by", ["None"] + cat_cols)
            if sel_pp and len(sel_pp) >= 2:
                with st.spinner("Building pair plot…"):
                    hue_val = hue_pp if hue_pp != "None" else None
                    pp_df = df[sel_pp + ([hue_val] if hue_val else [])].dropna()
                    if len(pp_df) > 2000:
                        pp_df = pp_df.sample(2000, random_state=42)
                    with sns.axes_style("white", SEABORN_STYLE):
                        g = sns.pairplot(pp_df, hue=hue_val, corner=False,
                                         plot_kws={"alpha": 0.5, "s": 18},
                                         palette="tab10")
                        g.fig.patch.set_facecolor("#FFFFFF")
                        g.fig.suptitle("Pair Plot", y=1.02, fontsize=12, fontweight="bold", color="#0F172A")
                        buf = io.BytesIO()
                        g.fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="#FFFFFF")
                        buf.seek(0)
                        st.image(buf, use_container_width=True)
                        plt.close("all")

    with tab5:
        test = st.selectbox("Test", [
            "t-test (2 numeric groups)", "Chi-square (categorical independence)",
            "ANOVA (3+ groups)", "Mann-Whitney U (non-parametric)"
        ])

        if test == "t-test (2 numeric groups)" and cat_cols and num_cols:
            gc = st.selectbox("Group column (2 categories)", cat_cols)
            vc = st.selectbox("Value column", num_cols)
            groups = df[gc].dropna().unique()
            if len(groups) == 2:
                g1 = df[df[gc] == groups[0]][vc].dropna()
                g2 = df[df[gc] == groups[1]][vc].dropna()
                t_stat, p_val = scipy_stats.ttest_ind(g1, g2)
                ca, cb, cc = st.columns(3)
                ca.metric("t-statistic", f"{t_stat:.4f}")
                cb.metric("p-value", f"{p_val:.6f}")
                cc.metric("Significant (α=0.05)", "Yes ✅" if p_val < 0.05 else "No ❌")
            else:
                st.warning("Select a column with exactly 2 unique values.")

        elif test == "Chi-square (categorical independence)" and len(cat_cols) >= 2:
            c1s = st.selectbox("Column A", cat_cols, key="chi_a")
            c2s = st.selectbox("Column B", cat_cols, key="chi_b")
            if c1s != c2s:
                ct = pd.crosstab(df[c1s], df[c2s])
                chi2, p_val, dof, _ = scipy_stats.chi2_contingency(ct)
                ca, cb, cc = st.columns(3)
                ca.metric("Chi² statistic", f"{chi2:.4f}")
                cb.metric("p-value", f"{p_val:.6f}")
                cc.metric("Significant (α=0.05)", "Yes ✅" if p_val < 0.05 else "No ❌")
                st.dataframe(ct, use_container_width=True)

        elif test == "ANOVA (3+ groups)" and cat_cols and num_cols:
            gc = st.selectbox("Group column", cat_cols, key="anova_g")
            vc = st.selectbox("Value column", num_cols, key="anova_v")
            groups_list = [g.dropna().values for _, g in df.groupby(gc)[vc]]
            if len(groups_list) >= 3:
                f_stat, p_val = scipy_stats.f_oneway(*groups_list)
                ca, cb, cc = st.columns(3)
                ca.metric("F-statistic", f"{f_stat:.4f}")
                cb.metric("p-value", f"{p_val:.6f}")
                cc.metric("Significant (α=0.05)", "Yes ✅" if p_val < 0.05 else "No ❌")
            else:
                st.warning("Need at least 3 groups.")

        elif test == "Mann-Whitney U (non-parametric)" and cat_cols and num_cols:
            gc = st.selectbox("Group column (2 categories)", cat_cols, key="mw_g")
            vc = st.selectbox("Value column", num_cols, key="mw_v")
            groups = df[gc].dropna().unique()
            if len(groups) == 2:
                g1 = df[df[gc] == groups[0]][vc].dropna()
                g2 = df[df[gc] == groups[1]][vc].dropna()
                u_stat, p_val = scipy_stats.mannwhitneyu(g1, g2)
                ca, cb, cc = st.columns(3)
                ca.metric("U-statistic", f"{u_stat:.4f}")
                cb.metric("p-value", f"{p_val:.6f}")
                cc.metric("Significant (α=0.05)", "Yes ✅" if p_val < 0.05 else "No ❌")
            else:
                st.warning("Select a column with exactly 2 unique values.")

    with tab6:
        if len(num_cols) < 2:
            st.info("Need at least 2 numeric columns.")
        else:
            xc = st.selectbox("X axis", num_cols, key="sc_x")
            yc = st.selectbox("Y axis", [c for c in num_cols if c != xc] or num_cols, key="sc_y")
            cc_ = st.selectbox("Color by", ["None"] + cat_cols + num_cols, key="sc_c")
            sz_ = st.selectbox("Size by", ["None"] + num_cols, key="sc_s")
            tl_ = st.checkbox("Trend line (OLS)", True)

            fig = px.scatter(df, x=xc, y=yc,
                             color=cc_ if cc_ != "None" else None,
                             size=sz_ if sz_ != "None" else None,
                             trendline="ols" if tl_ else None,
                             template="plotly_white", opacity=0.7,
                             title=f"{yc} vs {xc}",
                             color_continuous_scale="teal")
            fig.update_layout(height=520, plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig, use_container_width=True)
            corr_val = df[[xc, yc]].dropna().corr().iloc[0, 1]
            st.metric("Pearson Correlation", f"{corr_val:.4f}")
