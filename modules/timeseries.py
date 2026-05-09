import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def timeseries_page():
    st.markdown("""
    <div class="main-header">
        <h1>📅 Time Series Analysis</h1>
        <p>Analyze trends, seasonality, rolling averages, and growth rates over time.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
        return

    df = st.session_state.df

    dt_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    possible = [c for c in df.columns if c not in dt_cols]
    for c in possible:
        try:
            parsed = pd.to_datetime(df[c], infer_datetime_format=True, errors="coerce")
            if parsed.notnull().sum() / len(df) > 0.7:
                dt_cols.append(c)
        except Exception:
            pass
    dt_cols = list(dict.fromkeys(dt_cols))

    if not dt_cols:
        st.info("No datetime columns detected. Try converting a column to datetime in **Data Cleaning → Change Column Type**.")
        return

    num_cols = df.select_dtypes(include="number").columns.tolist()
    if not num_cols:
        st.info("No numeric columns found for time series analysis.")
        return

    with st.sidebar:
        pass

    c1, c2 = st.columns(2)
    with c1:
        date_col = st.selectbox("📅 Date/Time column", dt_cols)
    with c2:
        value_col = st.selectbox("📊 Value column", num_cols)

    temp = df[[date_col, value_col]].copy()
    temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
    temp = temp.dropna().sort_values(date_col)

    if temp.empty:
        st.warning("No valid data after filtering.")
        return

    resample_opts = {"Raw (no resampling)": None, "Daily": "D", "Weekly": "W",
                     "Monthly": "ME", "Quarterly": "QE", "Yearly": "YE"}
    resample = st.selectbox("⏱️ Resample frequency", list(resample_opts.keys()), index=2)
    agg_func = st.radio("Aggregation", ["mean", "sum", "max", "min"], horizontal=True)

    freq = resample_opts[resample]
    if freq:
        try:
            temp = temp.set_index(date_col).resample(freq)[value_col].agg(agg_func).reset_index()
        except Exception:
            pass

    temp.columns = ["Date", "Value"]

    span_days = (temp["Date"].max() - temp["Date"].min()).days
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Data points", f"{len(temp):,}")
    m2.metric("Time span", f"{span_days:,} days")
    m3.metric("Max value", f"{temp['Value'].max():.3g}")
    m4.metric("Min value", f"{temp['Value'].min():.3g}")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trend", "📉 Rolling Average", "📊 Periodicity", "📐 Growth Rate"])

    with tab1:
        add_trend = st.checkbox("Add OLS trend line", True)
        fill_area = st.checkbox("Fill area under curve", False)
        template = st.selectbox("Theme", ["plotly_white", "plotly_dark", "ggplot2", "seaborn"], key="ts_tmpl")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=temp["Date"], y=temp["Value"],
            mode="lines+markers" if len(temp) < 100 else "lines",
            name=value_col,
            line=dict(color="#667eea", width=2),
            fill="tozeroy" if fill_area else None,
            fillcolor="rgba(102,126,234,0.15)" if fill_area else None,
        ))
        if add_trend and len(temp) >= 2:
            x_num = np.arange(len(temp))
            z = np.polyfit(x_num, temp["Value"].fillna(0), 1)
            trend_line = np.poly1d(z)(x_num)
            fig.add_trace(go.Scatter(
                x=temp["Date"], y=trend_line,
                mode="lines", name="Trend",
                line=dict(color="#f093fb", width=2, dash="dash")
            ))
        fig.update_layout(
            title=f"{value_col} over Time", template=template,
            height=480, xaxis_title="Date", yaxis_title=value_col,
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        windows = st.multiselect("Rolling window(s)", [7, 14, 30, 60, 90, 180, 365],
                                 default=[7, 30])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=temp["Date"], y=temp["Value"], mode="lines",
                                  name="Actual", opacity=0.4,
                                  line=dict(color="#667eea")))
        colors = ["#f093fb", "#43e97b", "#fa709a", "#fee140", "#4facfe"]
        for w, color in zip(windows, colors):
            rolled = temp["Value"].rolling(window=w, min_periods=1).mean()
            fig2.add_trace(go.Scatter(x=temp["Date"], y=rolled,
                                      mode="lines", name=f"{w}-period MA",
                                      line=dict(color=color, width=2)))
        fig2.update_layout(title="Rolling Average Comparison", height=480,
                           template="plotly_white", hovermode="x unified",
                           xaxis_title="Date", yaxis_title=value_col)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        temp2 = temp.copy()
        temp2["Year"] = temp2["Date"].dt.year
        temp2["Month"] = temp2["Date"].dt.month
        temp2["Quarter"] = temp2["Date"].dt.quarter
        temp2["DayOfWeek"] = temp2["Date"].dt.day_name()

        period = st.radio("Breakdown by", ["Month", "Quarter", "Year", "DayOfWeek"], horizontal=True)

        agg_period = temp2.groupby(period)["Value"].agg(["mean", "sum", "count"]).reset_index()
        agg_period.columns = [period, "Mean", "Sum", "Count"]

        fig3 = px.bar(agg_period, x=period, y="Mean",
                      title=f"Average {value_col} by {period}",
                      template="plotly_white", color="Mean",
                      color_continuous_scale="viridis", text_auto=".2s")
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

        st.dataframe(agg_period.round(3), use_container_width=True)

    with tab4:
        if len(temp) >= 2:
            temp3 = temp.copy()
            temp3["PctChange"] = temp3["Value"].pct_change() * 100
            temp3["CumReturn"] = (1 + temp3["Value"].pct_change()).cumprod()

            fig4 = go.Figure()
            colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in temp3["PctChange"].fillna(0)]
            fig4.add_trace(go.Bar(x=temp3["Date"], y=temp3["PctChange"],
                                  marker_color=colors, name="Period % Change"))
            fig4.update_layout(title=f"Period-over-Period % Change: {value_col}",
                                height=400, template="plotly_white",
                                yaxis_title="% Change", xaxis_title="Date")
            st.plotly_chart(fig4, use_container_width=True)

            total_return = ((temp3["Value"].iloc[-1] / temp3["Value"].iloc[0]) - 1) * 100
            avg_change = temp3["PctChange"].mean()
            volatility = temp3["PctChange"].std()
            ca, cb, cc = st.columns(3)
            ca.metric("Total Return", f"{total_return:.2f}%")
            cb.metric("Avg Period Change", f"{avg_change:.2f}%")
            cc.metric("Volatility (σ)", f"{volatility:.2f}%")
