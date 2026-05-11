import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from styles import DARK_CSS, section_header

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,21,40,1)",
    font=dict(family="Inter", color="#E2E8F0"),
    margin=dict(l=20, r=20, t=50, b=20),
    colorway=["#818cf8", "#f472b6", "#4ade80", "#fbbf24", "#38bdf8", "#a855f7", "#f87171"],
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
)


def viz_tools_page():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header(
        "🎨", "Visualization Tools",
        "Chart templates, animated time series, comparison mode & heatmap calendar"
    ), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data uploaded yet. Please upload a file first.")
        return

    df = st.session_state["clean_data"]
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetime64"]).columns.tolist()

    # Try to auto-detect date columns from object columns
    for col in cat_cols:
        try:
            parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
            if parsed.notna().mean() > 0.8:
                date_cols.append(col)
        except Exception:
            pass

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Chart Templates", "▶️ Animated Time Series", "⚖️ Comparison Mode", "📅 Heatmap Calendar"
    ])

    # ── Tab 1: Chart Templates ─────────────────────────────────────────────────
    with tab1:
        st.markdown("""
        <div style="background:rgba(129,140,248,.05);border:1px solid rgba(129,140,248,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;">
          Pre-built chart setups — pick a template, map your columns, and generate instantly.
        </div>
        """, unsafe_allow_html=True)

        templates = {
            "📊 Sales Dashboard": "bar_sum",
            "📈 Trend Line": "line_trend",
            "🔵 Scatter Matrix": "scatter_matrix",
            "🥧 Category Breakdown": "pie_cat",
            "🌡️ Correlation Heatmap": "corr_heat",
            "🎻 Distribution Violin": "violin",
            "📦 Box Plot Comparison": "box_compare",
            "🔺 Funnel Chart": "funnel",
            "💧 Waterfall Chart": "waterfall",
            "🌐 Bubble Chart": "bubble",
        }

        chosen = st.selectbox("Choose a chart template", list(templates.keys()), key="tmpl_choice")
        kind = templates[chosen]

        if kind == "bar_sum":
            if not cat_cols or not num_cols:
                st.info("Need at least one categorical and one numeric column.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    x_col = st.selectbox("Category (X axis)", cat_cols, key="bs_x")
                with c2:
                    y_col = st.selectbox("Numeric (Y axis)", num_cols, key="bs_y")
                agg = st.radio("Aggregation", ["Sum", "Mean", "Count", "Max", "Min"], horizontal=True, key="bs_agg")
                if st.button("Generate Chart", key="gen_bar_sum"):
                    agg_fn = {"Sum": "sum", "Mean": "mean", "Count": "count", "Max": "max", "Min": "min"}[agg]
                    agg_df = df.groupby(x_col)[y_col].agg(agg_fn).reset_index().sort_values(y_col, ascending=False)
                    fig = px.bar(agg_df, x=x_col, y=y_col, color=x_col,
                                 title=f"{agg} of {y_col} by {x_col}",
                                 color_discrete_sequence=px.colors.qualitative.Bold)
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

        elif kind == "line_trend":
            if not num_cols:
                st.info("Need at least one numeric column.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    x_col = st.selectbox("X axis", df.columns.tolist(), key="lt_x")
                with c2:
                    y_cols = st.multiselect("Y axis (metrics)", num_cols, default=num_cols[:2], key="lt_y")
                if st.button("Generate Chart", key="gen_line"):
                    if y_cols:
                        fig = px.line(df, x=x_col, y=y_cols, title=f"Trend: {', '.join(y_cols)} over {x_col}",
                                      markers=True)
                        fig.update_layout(**PLOTLY_THEME)
                        st.plotly_chart(fig, use_container_width=True)

        elif kind == "scatter_matrix":
            if len(num_cols) < 2:
                st.info("Need at least 2 numeric columns.")
            else:
                sel = st.multiselect("Columns", num_cols, default=num_cols[:min(4, len(num_cols))], key="sm_cols")
                color_col = st.selectbox("Color by", ["— none —"] + cat_cols, key="sm_color")
                if st.button("Generate Chart", key="gen_smat") and len(sel) >= 2:
                    fig = px.scatter_matrix(df, dimensions=sel,
                                            color=color_col if color_col != "— none —" else None,
                                            title="Scatter Matrix")
                    fig.update_layout(**PLOTLY_THEME)
                    fig.update_traces(diagonal_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

        elif kind == "pie_cat":
            if not cat_cols:
                st.info("Need at least one categorical column.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    names_col = st.selectbox("Category column", cat_cols, key="pie_names")
                with c2:
                    vals_col = st.selectbox("Value column (optional)", ["— count —"] + num_cols, key="pie_vals")
                if st.button("Generate Chart", key="gen_pie"):
                    if vals_col == "— count —":
                        pie_df = df[names_col].value_counts().reset_index()
                        pie_df.columns = [names_col, "count"]
                        fig = px.pie(pie_df, names=names_col, values="count", title=f"Distribution of {names_col}")
                    else:
                        pie_df = df.groupby(names_col)[vals_col].sum().reset_index()
                        fig = px.pie(pie_df, names=names_col, values=vals_col, title=f"{vals_col} by {names_col}")
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

        elif kind == "corr_heat":
            if len(num_cols) < 2:
                st.info("Need at least 2 numeric columns.")
            else:
                sel = st.multiselect("Columns", num_cols, default=num_cols[:min(10, len(num_cols))], key="ch_cols")
                if st.button("Generate Chart", key="gen_corr") and len(sel) >= 2:
                    corr = df[sel].corr()
                    fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                                    color_continuous_scale="RdBu_r",
                                    title="Correlation Heatmap")
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

        elif kind == "violin":
            if not num_cols:
                st.info("Need at least one numeric column.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    y_col = st.selectbox("Numeric column", num_cols, key="vio_y")
                with c2:
                    x_col = st.selectbox("Group by", ["— none —"] + cat_cols, key="vio_x")
                if st.button("Generate Chart", key="gen_vio"):
                    fig = px.violin(df, y=y_col, x=x_col if x_col != "— none —" else None,
                                    box=True, points="outliers", title=f"Distribution of {y_col}",
                                    color=x_col if x_col != "— none —" else None)
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

        elif kind == "box_compare":
            if not num_cols:
                st.info("Need at least one numeric column.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    y_cols = st.multiselect("Metrics to compare", num_cols, default=num_cols[:3], key="box_y")
                with c2:
                    color_col = st.selectbox("Color by", ["— none —"] + cat_cols, key="box_color")
                if st.button("Generate Chart", key="gen_box") and y_cols:
                    if len(y_cols) == 1:
                        fig = px.box(df, y=y_cols[0],
                                     x=color_col if color_col != "— none —" else None,
                                     color=color_col if color_col != "— none —" else None,
                                     title=f"Box Plot — {y_cols[0]}")
                    else:
                        melt = df[y_cols].melt(var_name="Metric", value_name="Value")
                        fig = px.box(melt, x="Metric", y="Value", color="Metric",
                                     title="Box Plot Comparison")
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

        elif kind == "funnel":
            if not cat_cols or not num_cols:
                st.info("Need at least one categorical and one numeric column.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    stage_col = st.selectbox("Stage column", cat_cols, key="fn_stage")
                with c2:
                    val_col = st.selectbox("Value column", num_cols, key="fn_val")
                if st.button("Generate Chart", key="gen_funnel"):
                    fn_df = df.groupby(stage_col)[val_col].sum().reset_index().sort_values(val_col, ascending=False)
                    fig = px.funnel(fn_df, x=val_col, y=stage_col, title=f"Funnel: {val_col} by {stage_col}")
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

        elif kind == "waterfall":
            if not num_cols:
                st.info("Need at least one numeric column.")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    label_col = st.selectbox("Label column", df.columns.tolist(), key="wf_label")
                with c2:
                    val_col = st.selectbox("Value column", num_cols, key="wf_val")
                if st.button("Generate Chart", key="gen_wf"):
                    wf_df = df[[label_col, val_col]].dropna().head(20)
                    fig = go.Figure(go.Waterfall(
                        name="", orientation="v",
                        x=wf_df[label_col].astype(str).tolist(),
                        y=wf_df[val_col].tolist(),
                        connector={"line": {"color": "rgba(255,255,255,.1)"}},
                        increasing={"marker": {"color": "#4ade80"}},
                        decreasing={"marker": {"color": "#f87171"}},
                        totals={"marker": {"color": "#818cf8"}},
                    ))
                    fig.update_layout(**PLOTLY_THEME, title=f"Waterfall — {val_col}")
                    st.plotly_chart(fig, use_container_width=True)

        elif kind == "bubble":
            if len(num_cols) < 3:
                st.info("Need at least 3 numeric columns.")
            else:
                c1, c2, c3 = st.columns(3)
                with c1: x_col = st.selectbox("X", num_cols, key="bb_x")
                with c2: y_col = st.selectbox("Y", num_cols, index=1, key="bb_y")
                with c3: size_col = st.selectbox("Bubble size", num_cols, index=2, key="bb_sz")
                color_col = st.selectbox("Color by", ["— none —"] + cat_cols, key="bb_color")
                if st.button("Generate Chart", key="gen_bubble"):
                    fig = px.scatter(df, x=x_col, y=y_col, size=size_col,
                                     color=color_col if color_col != "— none —" else None,
                                     title=f"Bubble Chart: {x_col} vs {y_col} (size={size_col})",
                                     size_max=50, opacity=0.8)
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

    # ── Tab 2: Animated Time Series ────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style="background:rgba(56,189,248,.05);border:1px solid rgba(56,189,248,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;">
          Animate your data over time — watch metrics evolve frame by frame.
        </div>
        """, unsafe_allow_html=True)

        all_cols = df.columns.tolist()
        c1, c2, c3 = st.columns(3)
        with c1:
            time_col = st.selectbox("Time / Frame column", all_cols, key="anim_time")
        with c2:
            y_col = st.selectbox("Y axis (metric)", num_cols if num_cols else all_cols, key="anim_y")
        with c3:
            x_col = st.selectbox("X axis", all_cols, key="anim_x", index=min(1, len(all_cols) - 1))

        color_col = st.selectbox("Color by (optional)", ["— none —"] + cat_cols, key="anim_color")
        chart_type = st.radio("Chart type", ["Bar Race", "Scatter", "Line"], horizontal=True, key="anim_type")

        if st.button("▶️ Generate Animation", key="gen_anim"):
            try:
                anim_df = df[[time_col, x_col, y_col] + ([color_col] if color_col != "— none —" else [])].dropna()
                anim_df[time_col] = anim_df[time_col].astype(str)
                color_arg = color_col if color_col != "— none —" else None

                if chart_type == "Bar Race":
                    fig = px.bar(anim_df, x=x_col, y=y_col, animation_frame=time_col,
                                 color=color_arg or x_col,
                                 title=f"Animated Bar: {y_col} over {time_col}",
                                 color_discrete_sequence=px.colors.qualitative.Bold)
                elif chart_type == "Scatter":
                    fig = px.scatter(anim_df, x=x_col, y=y_col, animation_frame=time_col,
                                     color=color_arg,
                                     title=f"Animated Scatter: {x_col} vs {y_col}",
                                     size_max=15)
                else:
                    fig = px.line(anim_df, x=x_col, y=y_col, animation_frame=time_col,
                                  color=color_arg,
                                  title=f"Animated Line: {y_col} over {x_col}")

                fig.update_layout(**PLOTLY_THEME, height=550)
                fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 600
                fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 300
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Animation error: {e}")

    # ── Tab 3: Comparison Mode ─────────────────────────────────────────────────
    with tab3:
        st.markdown("""
        <div style="background:rgba(244,114,182,.05);border:1px solid rgba(244,114,182,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;">
          Compare two metrics or groups side-by-side with synchronized axes.
        </div>
        """, unsafe_allow_html=True)

        if not num_cols:
            st.info("Need at least one numeric column.")
        else:
            mode = st.radio("Comparison mode", ["Two Metrics", "Two Groups", "Before vs After"], horizontal=True, key="cmp_mode")

            if mode == "Two Metrics":
                c1, c2, c3 = st.columns(3)
                with c1: x_col = st.selectbox("X axis", df.columns.tolist(), key="cmp_x")
                with c2: metric_a = st.selectbox("Metric A", num_cols, key="cmp_ma")
                with c3: metric_b = st.selectbox("Metric B", num_cols, index=min(1, len(num_cols) - 1), key="cmp_mb")
                chart_t = st.radio("Chart type", ["Line", "Bar", "Area"], horizontal=True, key="cmp_ct")

                if st.button("Compare", key="do_cmp_metrics"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if chart_t == "Line":
                            fig = px.line(df, x=x_col, y=metric_a, title=f"Metric A: {metric_a}",
                                          color_discrete_sequence=["#818cf8"])
                        elif chart_t == "Bar":
                            fig = px.bar(df, x=x_col, y=metric_a, title=f"Metric A: {metric_a}",
                                         color_discrete_sequence=["#818cf8"])
                        else:
                            fig = px.area(df, x=x_col, y=metric_a, title=f"Metric A: {metric_a}",
                                          color_discrete_sequence=["#818cf8"])
                        fig.update_layout(**PLOTLY_THEME)
                        st.plotly_chart(fig, use_container_width=True)

                    with col_b:
                        if chart_t == "Line":
                            fig = px.line(df, x=x_col, y=metric_b, title=f"Metric B: {metric_b}",
                                          color_discrete_sequence=["#f472b6"])
                        elif chart_t == "Bar":
                            fig = px.bar(df, x=x_col, y=metric_b, title=f"Metric B: {metric_b}",
                                         color_discrete_sequence=["#f472b6"])
                        else:
                            fig = px.area(df, x=x_col, y=metric_b, title=f"Metric B: {metric_b}",
                                          color_discrete_sequence=["#f472b6"])
                        fig.update_layout(**PLOTLY_THEME)
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown('<div style="font-weight:600;color:#f1f2f6;margin:.75rem 0 .5rem;">Stats Comparison</div>', unsafe_allow_html=True)
                    stats_df = pd.DataFrame({
                        "Metric": [metric_a, metric_b],
                        "Mean": [df[metric_a].mean(), df[metric_b].mean()],
                        "Median": [df[metric_a].median(), df[metric_b].median()],
                        "Std Dev": [df[metric_a].std(), df[metric_b].std()],
                        "Min": [df[metric_a].min(), df[metric_b].min()],
                        "Max": [df[metric_a].max(), df[metric_b].max()],
                    }).set_index("Metric").round(3)
                    st.dataframe(stats_df, use_container_width=True)

            elif mode == "Two Groups":
                if not cat_cols:
                    st.info("Need at least one categorical column to define groups.")
                else:
                    c1, c2, c3 = st.columns(3)
                    with c1: grp_col = st.selectbox("Group column", cat_cols, key="grp_col")
                    with c2:
                        groups = df[grp_col].dropna().unique().tolist()
                        grp_a = st.selectbox("Group A", groups, key="grp_a")
                    with c3:
                        grp_b = st.selectbox("Group B", [g for g in groups if g != grp_a] or groups, key="grp_b")
                    metric = st.selectbox("Metric", num_cols, key="grp_metric")

                    if st.button("Compare Groups", key="do_cmp_groups"):
                        df_a = df[df[grp_col] == grp_a][metric].dropna()
                        df_b = df[df[grp_col] == grp_b][metric].dropna()

                        col_a, col_b = st.columns(2)
                        with col_a:
                            fig = px.histogram(pd.DataFrame({metric: df_a}), x=metric, nbins=30,
                                               title=f"Group A: {grp_a}",
                                               color_discrete_sequence=["#818cf8"])
                            fig.update_layout(**PLOTLY_THEME)
                            st.plotly_chart(fig, use_container_width=True)
                            st.metric(f"{grp_a} Mean", f"{df_a.mean():.3g}")
                        with col_b:
                            fig = px.histogram(pd.DataFrame({metric: df_b}), x=metric, nbins=30,
                                               title=f"Group B: {grp_b}",
                                               color_discrete_sequence=["#f472b6"])
                            fig.update_layout(**PLOTLY_THEME)
                            st.plotly_chart(fig, use_container_width=True)
                            st.metric(f"{grp_b} Mean", f"{df_b.mean():.3g}")

            else:
                c1, c2, c3 = st.columns(3)
                with c1: split_col = st.selectbox("Split column", df.columns.tolist(), key="ba_split")
                with c2: split_val = st.text_input("Split value (before ≤ this)", key="ba_val")
                with c3: metric = st.selectbox("Metric", num_cols, key="ba_metric")

                if st.button("Compare Before vs After", key="do_ba") and split_val:
                    try:
                        s = df[split_col]
                        if pd.api.types.is_numeric_dtype(s):
                            mask = s <= float(split_val)
                        else:
                            mask = s <= split_val
                        before = df[mask][metric].dropna()
                        after = df[~mask][metric].dropna()
                        col_a, col_b = st.columns(2)
                        with col_a:
                            fig = px.histogram(pd.DataFrame({metric: before}), x=metric, nbins=30,
                                               title=f"Before (≤ {split_val})", color_discrete_sequence=["#818cf8"])
                            fig.update_layout(**PLOTLY_THEME)
                            st.plotly_chart(fig, use_container_width=True)
                            st.metric("Before Mean", f"{before.mean():.3g}")
                        with col_b:
                            fig = px.histogram(pd.DataFrame({metric: after}), x=metric, nbins=30,
                                               title=f"After (> {split_val})", color_discrete_sequence=["#f472b6"])
                            fig.update_layout(**PLOTLY_THEME)
                            st.plotly_chart(fig, use_container_width=True)
                            st.metric("After Mean", f"{after.mean():.3g}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Tab 4: Heatmap Calendar ────────────────────────────────────────────────
    with tab4:
        st.markdown("""
        <div style="background:rgba(74,222,128,.05);border:1px solid rgba(74,222,128,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;">
          GitHub-style calendar heatmap — visualize daily values across weeks and months.
          Select a date column and a numeric metric.
        </div>
        """, unsafe_allow_html=True)

        all_candidate_dates = date_cols[:]
        for col in cat_cols:
            try:
                test = pd.to_datetime(df[col].head(20), errors="coerce")
                if test.notna().mean() > 0.7:
                    all_candidate_dates.append(col)
            except Exception:
                pass

        if not all_candidate_dates:
            st.info("No date column detected. Make sure you have a date/datetime column. You can cast a column to datetime in Data Overview → Cleaning Tools.")
        elif not num_cols:
            st.info("Need at least one numeric column for the calendar values.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                date_col = st.selectbox("Date column", all_candidate_dates, key="cal_date")
            with c2:
                val_col = st.selectbox("Value column", num_cols, key="cal_val")
            with c3:
                agg_fn = st.selectbox("Aggregation", ["sum", "mean", "count", "max"], key="cal_agg")

            color_scale = st.selectbox("Color scale", ["Greens", "Blues", "Plasma", "Viridis", "Reds", "YlOrRd"], key="cal_cscale")

            if st.button("📅 Generate Calendar Heatmap", key="gen_cal"):
                try:
                    cal_df = df[[date_col, val_col]].copy()
                    cal_df[date_col] = pd.to_datetime(cal_df[date_col], errors="coerce")
                    cal_df = cal_df.dropna(subset=[date_col])
                    cal_df["date"] = cal_df[date_col].dt.date
                    cal_df["week"] = cal_df[date_col].dt.isocalendar().week.astype(int)
                    cal_df["weekday"] = cal_df[date_col].dt.weekday
                    cal_df["month"] = cal_df[date_col].dt.strftime("%b %Y")

                    daily = cal_df.groupby(["date", "week", "weekday", "month"])[val_col].agg(agg_fn).reset_index()

                    fig = px.density_heatmap(
                        daily, x="week", y="weekday", z=val_col,
                        color_continuous_scale=color_scale,
                        title=f"Calendar Heatmap — {agg_fn.capitalize()} of {val_col} per Day",
                        labels={"weekday": "Day of Week", "week": "Week of Year"},
                        nbinsx=53, nbinsy=7,
                    )
                    fig.update_yaxes(
                        tickvals=list(range(7)),
                        ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    )
                    fig.update_layout(**PLOTLY_THEME, height=320)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")
                    st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.5rem;">Monthly Summary</div>', unsafe_allow_html=True)
                    monthly = cal_df.groupby("month")[val_col].agg(agg_fn).reset_index()
                    monthly.columns = ["Month", f"{agg_fn.capitalize()} of {val_col}"]
                    fig2 = px.bar(monthly, x="Month", y=f"{agg_fn.capitalize()} of {val_col}",
                                  color_discrete_sequence=["#4ade80"],
                                  title="Monthly Totals")
                    fig2.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig2, use_container_width=True)

                except Exception as e:
                    st.error(f"Calendar heatmap error: {e}")
