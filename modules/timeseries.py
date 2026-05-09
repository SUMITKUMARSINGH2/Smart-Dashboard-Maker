import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def _header(title, sub):
    st.markdown(f"<div class='page-header'><h2>{title}</h2><p>{sub}</p></div>", unsafe_allow_html=True)


def timeseries_page():
    _header("Time Series Analysis", "Trends, rolling averages, seasonality breakdowns, and growth rate analysis")

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df

    dt_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    for c in df.columns:
        if c not in dt_cols:
            try:
                parsed = pd.to_datetime(df[c], infer_datetime_format=True, errors="coerce")
                if parsed.notnull().sum() / len(df) > 0.7:
                    dt_cols.append(c)
            except Exception:
                pass
    dt_cols = list(dict.fromkeys(dt_cols))

    if not dt_cols:
        st.info("No datetime columns detected. Convert a column in **Data Cleaning → Change Data Type** first.")
        return

    num_cols = df.select_dtypes(include="number").columns.tolist()
    if not num_cols:
        st.info("No numeric columns for time series analysis.")
        return

    c1, c2 = st.columns(2)
    date_col = c1.selectbox("Date / time column", dt_cols)
    value_col = c2.selectbox("Value column", num_cols)

    temp = df[[date_col, value_col]].copy()
    temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
    temp = temp.dropna().sort_values(date_col)

    if temp.empty:
        st.warning("No valid data after filtering.")
        return

    resample_opts = {"Raw": None, "Daily": "D", "Weekly": "W", "Monthly": "ME",
                     "Quarterly": "QE", "Yearly": "YE"}
    c3, c4 = st.columns(2)
    resample = c3.selectbox("Resample frequency", list(resample_opts.keys()), index=3)
    agg_func = c4.radio("Aggregation", ["mean", "sum", "max", "min"], horizontal=True)

    freq = resample_opts[resample]
    if freq:
        try:
            temp = temp.set_index(date_col).resample(freq)[value_col].agg(agg_func).reset_index()
        except Exception:
            pass
    temp.columns = ["Date", "Value"]

    span = (temp["Date"].max() - temp["Date"].min()).days
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Data points", f"{len(temp):,}")
    m2.metric("Time span", f"{span:,} days")
    m3.metric("Max", f"{temp['Value'].max():.3g}")
    m4.metric("Min", f"{temp['Value'].min():.3g}")

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Trend", "Rolling Average", "Periodicity", "Growth Rate"])

    LAYOUT = dict(plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF",
                  xaxis=dict(gridcolor="#F1F5F9"), yaxis=dict(gridcolor="#F1F5F9"),
                  hovermode="x unified", font=dict(color="#334155"))

    with tab1:
        add_trend = st.checkbox("OLS trend line", True)
        fill = st.checkbox("Fill area under curve", False)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=temp["Date"], y=temp["Value"],
            mode="lines+markers" if len(temp) < 80 else "lines",
            name=value_col, line=dict(color="#0EA5E9", width=2),
            fill="tozeroy" if fill else None,
            fillcolor="rgba(14,165,233,0.12)" if fill else None,
        ))
        if add_trend and len(temp) >= 2:
            xn = np.arange(len(temp))
            z = np.polyfit(xn, temp["Value"].fillna(0), 1)
            fig.add_trace(go.Scatter(
                x=temp["Date"], y=np.poly1d(z)(xn),
                mode="lines", name="Trend",
                line=dict(color="#F59E0B", width=2, dash="dash")
            ))
        fig.update_layout(title=f"{value_col} over Time", height=480,
                          xaxis_title="Date", yaxis_title=value_col, **LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        windows = st.multiselect("Rolling window(s)", [7, 14, 30, 60, 90, 180, 365], default=[7, 30])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=temp["Date"], y=temp["Value"], mode="lines",
                                  name="Actual", opacity=0.35, line=dict(color="#0EA5E9")))
        colors = ["#F59E0B", "#10B981", "#8B5CF6", "#EF4444", "#06B6D4"]
        for w, color in zip(windows, colors):
            rolled = temp["Value"].rolling(window=w, min_periods=1).mean()
            fig2.add_trace(go.Scatter(x=temp["Date"], y=rolled, mode="lines",
                                       name=f"{w}-period MA", line=dict(color=color, width=2)))
        fig2.update_layout(title="Rolling Average Comparison", height=480,
                           xaxis_title="Date", yaxis_title=value_col, **LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        temp2 = temp.copy()
        temp2["Year"]      = temp2["Date"].dt.year
        temp2["Month"]     = temp2["Date"].dt.month
        temp2["Quarter"]   = temp2["Date"].dt.quarter
        temp2["DayOfWeek"] = temp2["Date"].dt.day_name()

        period = st.radio("Group by", ["Month", "Quarter", "Year", "DayOfWeek"], horizontal=True)
        agg_p = temp2.groupby(period)["Value"].agg(["mean", "sum", "count"]).reset_index()
        agg_p.columns = [period, "Mean", "Sum", "Count"]

        fig3 = px.bar(agg_p, x=period, y="Mean", title=f"Avg {value_col} by {period}",
                      template="plotly_white", color="Mean", color_continuous_scale="Blues",
                      text_auto=".2s")
        fig3.update_layout(height=400, plot_bgcolor="#F8FAFC", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig3, use_container_width=True)
        st.dataframe(agg_p.round(3), use_container_width=True)

    with tab4:
        if len(temp) >= 2:
            temp3 = temp.copy()
            temp3["PctChange"] = temp3["Value"].pct_change() * 100

            fig4 = go.Figure()
            colors_bar = ["#10B981" if v >= 0 else "#EF4444"
                          for v in temp3["PctChange"].fillna(0)]
            fig4.add_trace(go.Bar(x=temp3["Date"], y=temp3["PctChange"],
                                   marker_color=colors_bar, name="% Change"))
            fig4.update_layout(title=f"Period-over-Period % Change — {value_col}",
                               height=420, yaxis_title="% Change",
                               xaxis_title="Date", **LAYOUT)
            st.plotly_chart(fig4, use_container_width=True)

            total = ((temp3["Value"].iloc[-1] / temp3["Value"].iloc[0]) - 1) * 100
            ca, cb, cc = st.columns(3)
            ca.metric("Total Return", f"{total:.2f}%")
            cb.metric("Avg Period Change", f"{temp3['PctChange'].mean():.2f}%")
            cc.metric("Volatility (σ)", f"{temp3['PctChange'].std():.2f}%")
