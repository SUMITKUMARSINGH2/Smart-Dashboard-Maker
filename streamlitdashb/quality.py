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
    font=dict(family="Inter", color="#E2E8F0"),
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=["#818cf8", "#f472b6", "#4ade80", "#fbbf24", "#38bdf8", "#a855f7"],
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
)


def _quality_score(df: pd.DataFrame) -> dict:
    n = len(df)
    if n == 0:
        return {"score": 0, "components": {}}

    null_pct = df.isnull().mean().mean() * 100
    dup_pct = df.duplicated().sum() / n * 100

    mixed_type_penalty = 0
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna().head(200)
        num_count = pd.to_numeric(sample, errors="coerce").notna().sum()
        if 0 < num_count < len(sample):
            mixed_type_penalty += 5

    high_card_penalty = 0
    for col in df.select_dtypes(include=["object"]).columns:
        ratio = df[col].nunique() / n
        if ratio > 0.95 and n > 50:
            high_card_penalty += 3

    completeness = max(0, 100 - null_pct * 2)
    uniqueness = max(0, 100 - dup_pct * 3)
    consistency = max(0, 100 - mixed_type_penalty)
    cardinality = max(0, 100 - high_card_penalty)

    score = round(completeness * 0.35 + uniqueness * 0.30 + consistency * 0.20 + cardinality * 0.15)

    return {
        "score": score,
        "components": {
            "Completeness": round(completeness),
            "Uniqueness": round(uniqueness),
            "Consistency": round(consistency),
            "Cardinality": round(cardinality),
        },
        "null_pct": round(null_pct, 2),
        "dup_pct": round(dup_pct, 2),
    }


def _describe_column(col: pd.Series) -> str:
    dtype = col.dtype
    n = len(col)
    n_null = col.isnull().sum()
    null_pct = round(n_null / n * 100, 1)
    n_unique = col.nunique()

    lines = []

    if pd.api.types.is_numeric_dtype(col):
        vals = col.dropna()
        mean = vals.mean()
        median = vals.median()
        std = vals.std()
        skew = vals.skew()
        q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
        iqr = q3 - q1

        lines.append(f"Numeric column with {n_unique:,} unique values.")
        lines.append(f"Range: {vals.min():.3g} → {vals.max():.3g}. Mean: {mean:.3g}, Median: {median:.3g}.")

        if abs(skew) < 0.5:
            lines.append("Distribution is approximately symmetric (low skew).")
        elif skew > 1.5:
            lines.append("Strongly right-skewed — a few large values pull the mean up.")
        elif skew > 0.5:
            lines.append("Slightly right-skewed.")
        elif skew < -1.5:
            lines.append("Strongly left-skewed — a few small values pull the mean down.")
        else:
            lines.append("Slightly left-skewed.")

        outliers = ((col < q1 - 1.5 * iqr) | (col > q3 + 1.5 * iqr)).sum()
        if outliers > 0:
            lines.append(f"~{outliers:,} potential outliers detected (IQR method).")

    elif pd.api.types.is_datetime64_any_dtype(col):
        vals = col.dropna()
        lines.append(f"Date/time column spanning {vals.min()} → {vals.max()}.")
        span_days = (vals.max() - vals.min()).days
        lines.append(f"Time span: {span_days:,} days.")

    else:
        top = col.value_counts().head(3)
        lines.append(f"Categorical column with {n_unique:,} unique values.")
        if n_unique <= 2:
            lines.append("Binary column — only two distinct values.")
        elif n_unique <= 10:
            lines.append("Low cardinality — good for grouping and filtering.")
        elif n_unique / n > 0.9:
            lines.append("Very high cardinality — may be an ID or free-text field.")

        if len(top):
            top_vals = ", ".join([f'"{v}" ({c:,}×)' for v, c in top.items()])
            lines.append(f"Most common: {top_vals}.")

    if null_pct == 0:
        lines.append("No missing values. ✓")
    elif null_pct < 5:
        lines.append(f"{null_pct}% missing — low, safe to impute.")
    elif null_pct < 30:
        lines.append(f"{null_pct}% missing — consider imputation strategy.")
    else:
        lines.append(f"⚠️ {null_pct}% missing — high, carefully review before using this column.")

    return " ".join(lines)


def data_quality_page():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header(
        "🏅", "Data Quality",
        "Quality scoring, outlier detection, column intelligence & formula columns"
    ), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data uploaded yet. Please upload a file first.")
        return

    df = st.session_state["clean_data"]
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏅 Quality Score", "🔭 Outlier Detection", "🧠 Column Intelligence", "🧮 Formula Columns"
    ])

    # ── Tab 1: Quality Score ───────────────────────────────────────────────────
    with tab1:
        result = _quality_score(df)
        score = result["score"]
        comps = result["components"]

        color = "#4ade80" if score >= 80 else "#fbbf24" if score >= 60 else "#f87171"
        label = "Excellent" if score >= 80 else "Fair" if score >= 60 else "Needs Attention"

        st.markdown(f"""
        <div style="text-align:center;padding:2rem 1rem 1.5rem;margin-bottom:1rem;">
          <div style="font-size:5rem;font-weight:900;color:{color};line-height:1;
                      text-shadow:0 0 40px {color}55;">{score}</div>
          <div style="font-size:1.1rem;font-weight:700;color:{color};margin-top:.3rem;">{label}</div>
          <div style="font-size:.8rem;color:#7c7f96;margin-top:.4rem;">Overall Data Quality Score / 100</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(kpi_row_html([
            ("Completeness", f"{comps['Completeness']}%"),
            ("Uniqueness", f"{comps['Uniqueness']}%"),
            ("Consistency", f"{comps['Consistency']}%"),
            ("Cardinality", f"{comps['Cardinality']}%"),
            ("Null Rate", f"{result['null_pct']}%"),
            ("Dup Rate", f"{result['dup_pct']}%"),
        ]), unsafe_allow_html=True)

        fig = go.Figure(go.Bar(
            x=list(comps.values()),
            y=list(comps.keys()),
            orientation="h",
            marker_color=["#4ade80" if v >= 80 else "#fbbf24" if v >= 60 else "#f87171" for v in comps.values()],
        ))
        fig.update_layout(**PLOTLY_THEME, title="Quality Score Breakdown", xaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.75rem;">Per-Column Quality</div>', unsafe_allow_html=True)
        col_scores = []
        for col in df.columns:
            s = df[col]
            null_p = round(s.isnull().mean() * 100, 1)
            uniq = s.nunique()
            uniq_p = round(uniq / len(df) * 100, 1)
            col_score = max(0, round(100 - null_p * 2 - (10 if uniq_p > 95 and len(df) > 50 else 0)))
            col_scores.append({
                "Column": col,
                "Type": str(s.dtype),
                "Null %": null_p,
                "Unique": uniq,
                "Unique %": uniq_p,
                "Quality": col_score,
            })
        st.dataframe(pd.DataFrame(col_scores), use_container_width=True, hide_index=True)

    # ── Tab 2: Outlier Detection ───────────────────────────────────────────────
    with tab2:
        if not num_cols:
            st.info("No numeric columns for outlier detection.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                sel_col = st.selectbox("Column", num_cols, key="out_col")
            with c2:
                method = st.selectbox("Method", ["IQR (Tukey)", "Z-Score (3σ)", "Both"], key="out_method")
            with c3:
                z_thresh = st.number_input("Z-Score threshold", 1.5, 5.0, 3.0, 0.1, key="out_z")

            s = df[sel_col].dropna()
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            iqr_mask = (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
            z_mask = (np.abs((s - s.mean()) / s.std()) > z_thresh)

            if method == "IQR (Tukey)":
                mask = iqr_mask
            elif method == "Z-Score (3σ)":
                mask = z_mask
            else:
                mask = iqr_mask | z_mask

            n_out = mask.sum()
            pct = round(n_out / len(s) * 100, 1)

            c1, c2, c3 = st.columns(3)
            c1.metric("Outliers Detected", f"{n_out:,}")
            c2.metric("Outlier %", f"{pct}%")
            c3.metric("Clean Rows", f"{len(s) - n_out:,}")

            plot_df = pd.DataFrame({"value": s, "type": ["Outlier" if m else "Normal" for m in mask]})
            fig = px.strip(plot_df, x="type", y="value", color="type",
                           color_discrete_map={"Normal": "#818cf8", "Outlier": "#f87171"},
                           title=f"Outliers in '{sel_col}' — {method}")
            fig.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)

            col_a, col_b = st.columns(2)
            with col_a:
                fig2 = px.box(df, y=sel_col, color_discrete_sequence=["#818cf8"],
                              title=f"Box Plot — {sel_col}")
                fig2.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig2, use_container_width=True)
            with col_b:
                fig3 = px.histogram(df, x=sel_col, nbins=50, color_discrete_sequence=["#38bdf8"],
                                    title=f"Distribution — {sel_col}")
                fig3.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig3, use_container_width=True)

            if n_out > 0:
                st.markdown("---")
                st.markdown(f'<div style="font-weight:600;color:#f1f2f6;margin-bottom:.5rem;">Outlier Rows ({n_out:,})</div>', unsafe_allow_html=True)
                outlier_idx = s[mask].index
                st.dataframe(df.loc[outlier_idx].head(200), use_container_width=True, hide_index=True)

                if st.button(f"🗑️ Remove {n_out:,} outlier rows from dataset", key="remove_outliers"):
                    clean_idx = df.index.difference(outlier_idx)
                    st.session_state["clean_data"] = df.loc[clean_idx].reset_index(drop=True)
                    st.success(f"✅ Removed {n_out:,} outliers. Dataset now has {len(clean_idx):,} rows.")
                    st.rerun()

    # ── Tab 3: Column Intelligence ─────────────────────────────────────────────
    with tab3:
        st.markdown("""
        <div style="background:rgba(129,140,248,.05);border:1px solid rgba(129,140,248,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;">
          Automatic statistical analysis of each column — no AI API required.
        </div>
        """, unsafe_allow_html=True)

        search = st.text_input("Filter columns", placeholder="Search…", key="ci_search")
        cols_to_show = [c for c in df.columns if search.lower() in c.lower()] if search else list(df.columns)

        for col in cols_to_show:
            s = df[col]
            dtype_color = "#38bdf8" if pd.api.types.is_numeric_dtype(s) else \
                          "#4ade80" if pd.api.types.is_datetime64_any_dtype(s) else "#f472b6"
            dtype_label = "Numeric" if pd.api.types.is_numeric_dtype(s) else \
                          "DateTime" if pd.api.types.is_datetime64_any_dtype(s) else "Categorical"

            description = _describe_column(s)

            with st.expander(f"**{col}**", expanded=False):
                st.markdown(f"""
                <div style="display:flex;gap:.5rem;align-items:center;margin-bottom:.75rem;">
                  <span style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
                               color:{dtype_color};font-size:.7rem;font-weight:600;padding:.2rem .65rem;
                               border-radius:999px;">{dtype_label}</span>
                  <span style="color:#475569;font-size:.75rem;">{str(s.dtype)}</span>
                </div>
                <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
                            border-radius:10px;padding:.9rem 1rem;color:#94A3B8;font-size:.84rem;line-height:1.7;">
                  {description}
                </div>
                """, unsafe_allow_html=True)

                if pd.api.types.is_numeric_dtype(s):
                    vals = s.dropna()
                    ca, cb = st.columns(2)
                    with ca:
                        st.metric("Mean", f"{vals.mean():.4g}")
                        st.metric("Std Dev", f"{vals.std():.4g}")
                    with cb:
                        st.metric("Median", f"{vals.median():.4g}")
                        st.metric("Skewness", f"{vals.skew():.3f}")
                else:
                    vc = s.value_counts().head(8).reset_index()
                    vc.columns = ["Value", "Count"]
                    fig = px.bar(vc, x="Value", y="Count", color_discrete_sequence=["#818cf8"],
                                 title=f"Top values — {col}")
                    fig.update_layout(**PLOTLY_THEME, height=250)
                    st.plotly_chart(fig, use_container_width=True)

    # ── Tab 4: Formula Columns ─────────────────────────────────────────────────
    with tab4:
        st.markdown("""
        <div style="background:rgba(251,191,36,.05);border:1px solid rgba(251,191,36,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;line-height:1.7;">
          Create new columns using Python/pandas expressions.
          Use column names directly — e.g. <code>price * quantity</code> or <code>revenue - cost</code>.
          Math functions: <code>log()</code>, <code>abs()</code>, <code>sqrt()</code>, <code>round()</code>.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.5rem;">Available columns</div>', unsafe_allow_html=True)
        col_pills = " &nbsp;".join([
            f'<code style="background:rgba(255,255,255,.05);padding:.15rem .45rem;border-radius:4px;font-size:.75rem;color:#818cf8;">{c}</code>'
            for c in df.columns
        ])
        st.markdown(f'<div style="line-height:2;">{col_pills}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns([1.2, 2])
        with c1:
            new_col_name = st.text_input("New column name", placeholder="profit_margin", key="fc_name")
        with c2:
            formula = st.text_input("Formula", placeholder="(revenue - cost) / revenue * 100", key="fc_formula")

        st.markdown("""
        <div style="font-size:.75rem;color:#475569;margin-top:.25rem;">
          Examples: &nbsp;
          <code>price * quantity</code> &nbsp;·&nbsp;
          <code>log(salary)</code> &nbsp;·&nbsp;
          <code>age / 10</code> &nbsp;·&nbsp;
          <code>revenue - cost</code>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ Add Column", key="add_fc", use_container_width=False):
            if not new_col_name.strip():
                st.error("Please enter a column name.")
            elif not formula.strip():
                st.error("Please enter a formula.")
            elif new_col_name in df.columns:
                st.error(f"Column '{new_col_name}' already exists. Choose a different name.")
            else:
                try:
                    import math
                    local_env = {c: df[c] for c in df.columns}
                    local_env.update({
                        "log": np.log, "log10": np.log10, "log2": np.log2,
                        "sqrt": np.sqrt, "abs": np.abs, "round": np.round,
                        "exp": np.exp, "sin": np.sin, "cos": np.cos,
                        "floor": np.floor, "ceil": np.ceil,
                        "pi": math.pi, "e": math.e,
                    })
                    result = eval(formula, {"__builtins__": {}}, local_env)
                    df[new_col_name] = result
                    st.session_state["clean_data"] = df
                    st.success(f"✅ Added column **'{new_col_name}'** — preview below:")
                    st.dataframe(df[[new_col_name]].head(10), use_container_width=True, hide_index=True)
                    st.rerun()
                except Exception as e:
                    st.error(f"Formula error: {e}")

        st.markdown("---")
        st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.5rem;">Current Columns</div>', unsafe_allow_html=True)
        cols_info = [{"Column": c, "Type": str(df[c].dtype), "Sample": str(df[c].iloc[0]) if len(df) else "—"} for c in df.columns]
        st.dataframe(pd.DataFrame(cols_info), use_container_width=True, hide_index=True)
