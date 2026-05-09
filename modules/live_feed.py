import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
import time
from datetime import datetime, timezone

_PLOTLY_DARK = dict(
    paper_bgcolor="#0A0F1E",
    plot_bgcolor="#0D1526",
    font=dict(color="#94A3B8", family="Space Grotesk"),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    title_font=dict(size=13, color="#E2E8F0"),
    hovermode="x unified",
)

NEON = ["#00D4FF", "#7C3AED", "#FF006E", "#10B981", "#F59E0B",
        "#0EA5E9", "#A855F7", "#14B8A6"]

DEMO_URLS = {
    "Iris dataset (CSV)":
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
    "Titanic (CSV)":
        "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
    "Tips dataset (CSV)":
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv",
    "World happiness (CSV)":
        "https://raw.githubusercontent.com/rishidamarla/world-happiness-report/main/2023.csv",
    "BTC price history (CSV)":
        "https://raw.githubusercontent.com/datasets/bitcoin-prices/main/data/monthly.csv",
}

INTERVALS = {
    "5 seconds":  5,
    "10 seconds": 10,
    "30 seconds": 30,
    "1 minute":   60,
    "5 minutes":  300,
}

_SK = "_live_"   # session-key prefix


def _init_state():
    defaults = {
        f"{_SK}url":          "",
        f"{_SK}interval":     30,
        f"{_SK}paused":       False,
        f"{_SK}last_fetch":   0.0,
        f"{_SK}df":           None,
        f"{_SK}error":        None,
        f"{_SK}history":      [],   # list of {"ts": datetime, "df": df}
        f"{_SK}fetch_count":  0,
        f"{_SK}connected":    False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _fetch(url: str) -> pd.DataFrame:
    headers = {"User-Agent": "DataVizPro/1.0", "Accept": "text/csv,application/json,*/*"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    ct = resp.headers.get("Content-Type", "")
    raw = resp.content

    if "json" in ct or url.lower().endswith(".json"):
        try:
            df = pd.read_json(io.BytesIO(raw))
        except Exception:
            import json
            data = json.loads(raw)
            if isinstance(data, list):
                df = pd.json_normalize(data)
            elif isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        df = pd.json_normalize(v)
                        break
                else:
                    df = pd.DataFrame([data])
            else:
                raise ValueError("Unrecognised JSON structure")
    else:
        # Try different separators
        text = raw.decode("utf-8", errors="replace")
        sep = ";" if text[:1024].count(";") > text[:1024].count(",") else ","
        df = pd.read_csv(io.StringIO(text), sep=sep, low_memory=False)

    # Auto-parse dates
    for col in df.columns:
        if df[col].dtype == object:
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notnull().mean() > 0.7:
                    df[col] = parsed
            except Exception:
                pass
    return df


def _status_badge(connected: bool, paused: bool, error: str | None) -> str:
    if error:
        return """<div style='display:inline-flex;align-items:center;gap:6px;
                   background:rgba(255,0,110,0.1);border:1px solid rgba(255,0,110,0.3);
                   border-radius:20px;padding:.25rem .8rem;font-size:.72rem;
                   font-weight:600;color:#FF006E;font-family:"JetBrains Mono",monospace;'>
                   <span style='width:6px;height:6px;border-radius:50%;
                   background:#FF006E;display:inline-block;'></span>
                   ERROR
               </div>"""
    if not connected:
        return """<div style='display:inline-flex;align-items:center;gap:6px;
                   background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.2);
                   border-radius:20px;padding:.25rem .8rem;font-size:.72rem;
                   font-weight:600;color:#64748B;font-family:"JetBrains Mono",monospace;'>
                   <span style='width:6px;height:6px;border-radius:50%;
                   background:#64748B;display:inline-block;'></span>
                   NOT CONNECTED
               </div>"""
    if paused:
        return """<div style='display:inline-flex;align-items:center;gap:6px;
                   background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);
                   border-radius:20px;padding:.25rem .8rem;font-size:.72rem;
                   font-weight:600;color:#F59E0B;font-family:"JetBrains Mono",monospace;'>
                   <span style='width:6px;height:6px;border-radius:50%;
                   background:#F59E0B;display:inline-block;'></span>
                   PAUSED
               </div>"""
    return """<div style='display:inline-flex;align-items:center;gap:6px;
               background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
               border-radius:20px;padding:.25rem .8rem;font-size:.72rem;
               font-weight:600;color:#10B981;font-family:"JetBrains Mono",monospace;'>
               <span style='width:6px;height:6px;border-radius:50%;
               background:#10B981;animation:live-pulse 1.4s ease-in-out infinite;
               display:inline-block;'></span>
               LIVE
           </div>"""


def _auto_refresh_js(interval_ms: int):
    """Inject JS that reloads the Streamlit page after interval_ms."""
    st.markdown(f"""
    <script>
    (function() {{
        if (window.__dvpRefreshTimer) clearTimeout(window.__dvpRefreshTimer);
        window.__dvpRefreshTimer = setTimeout(function() {{
            // Trigger Streamlit rerun by simulating URL change
            const iframe = window.frameElement;
            if (iframe) {{
                // Inside iframe — post message up
                window.parent.postMessage({{type: 'streamlit:forceRerun'}}, '*');
            }}
            window.location.reload();
        }}, {interval_ms});
    }})();
    </script>
    <style>
    @keyframes live-pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%       {{ opacity: 0.4; transform: scale(0.7); }}
    }}
    </style>
    """, unsafe_allow_html=True)


def live_feed_page():
    _init_state()

    st.markdown("""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// live data feed</div>
        <h2>Live Data Feed</h2>
        <div class='page-header-bar'></div>
        <p>Connect to any public CSV or JSON URL — data refreshes automatically on your chosen interval</p>
    </div>""", unsafe_allow_html=True)

    # ── Connection panel ────────────────────────────────────────────────────
    with st.container():
        st.markdown("""
        <div style='background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.15);
                    border-radius:14px;padding:1.3rem 1.6rem;margin-bottom:1.2rem;'>
            <div style='font-size:.62rem;font-weight:600;letter-spacing:.15em;color:#00D4FF;
                        text-transform:uppercase;margin-bottom:.8rem;
                        font-family:"JetBrains Mono",monospace;'>
                Connection Settings
            </div>
        """, unsafe_allow_html=True)

        demo_choice = st.selectbox(
            "Quick-load a demo endpoint",
            ["— paste your own URL below —"] + list(DEMO_URLS.keys()),
            key="lf_demo",
        )
        if demo_choice != "— paste your own URL below —":
            st.session_state[f"{_SK}url"] = DEMO_URLS[demo_choice]

        url = st.text_input(
            "Data URL (CSV or JSON)",
            value=st.session_state[f"{_SK}url"],
            placeholder="https://example.com/data.csv",
            label_visibility="collapsed",
            key="lf_url_input",
        )
        st.session_state[f"{_SK}url"] = url

        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            interval_label = st.selectbox(
                "Refresh interval",
                list(INTERVALS.keys()),
                index=2,
                key="lf_interval_label",
            )
            st.session_state[f"{_SK}interval"] = INTERVALS[interval_label]

        with col_b:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            connect_btn = st.button(
                "Connect & Fetch",
                key="lf_connect",
                use_container_width=True,
                type="primary",
            )
        with col_c:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            pause_label = "Resume Feed" if st.session_state[f"{_SK}paused"] else "Pause Feed"
            if st.button(pause_label, key="lf_pause", use_container_width=True):
                st.session_state[f"{_SK}paused"] = not st.session_state[f"{_SK}paused"]
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Manual connect ──────────────────────────────────────────────────────
    if connect_btn:
        if not url.strip():
            st.warning("Please enter a URL first.")
        else:
            with st.spinner("Connecting…"):
                try:
                    df = _fetch(url.strip())
                    now = datetime.now(timezone.utc)
                    st.session_state[f"{_SK}df"]         = df
                    st.session_state[f"{_SK}error"]      = None
                    st.session_state[f"{_SK}connected"]  = True
                    st.session_state[f"{_SK}last_fetch"] = time.time()
                    st.session_state[f"{_SK}fetch_count"] += 1
                    st.session_state[f"{_SK}paused"]     = False
                    history = st.session_state[f"{_SK}history"]
                    history.append({"ts": now, "df": df.copy()})
                    if len(history) > 100:
                        history.pop(0)
                    st.session_state[f"{_SK}history"] = history
                except Exception as e:
                    st.session_state[f"{_SK}error"]     = str(e)
                    st.session_state[f"{_SK}connected"] = False
            st.rerun()

    # ── Auto-refresh logic ──────────────────────────────────────────────────
    connected  = st.session_state[f"{_SK}connected"]
    paused     = st.session_state[f"{_SK}paused"]
    error      = st.session_state[f"{_SK}error"]
    interval   = st.session_state[f"{_SK}interval"]
    last_fetch = st.session_state[f"{_SK}last_fetch"]
    df         = st.session_state[f"{_SK}df"]

    if connected and not paused and url.strip():
        elapsed = time.time() - last_fetch
        if elapsed >= interval and last_fetch > 0:
            try:
                df_new = _fetch(url.strip())
                now = datetime.now(timezone.utc)
                st.session_state[f"{_SK}df"]         = df_new
                st.session_state[f"{_SK}error"]      = None
                st.session_state[f"{_SK}last_fetch"] = time.time()
                st.session_state[f"{_SK}fetch_count"] += 1
                history = st.session_state[f"{_SK}history"]
                history.append({"ts": now, "df": df_new.copy()})
                if len(history) > 100:
                    history.pop(0)
                st.session_state[f"{_SK}history"] = history
                df = df_new
            except Exception as e:
                st.session_state[f"{_SK}error"] = str(e)
                error = str(e)

        # Inject JS auto-refresh timer
        remaining_ms = max(500, int((interval - elapsed) * 1000))
        _auto_refresh_js(remaining_ms)

    # ── Status bar ──────────────────────────────────────────────────────────
    badge = _status_badge(connected, paused, error)
    fetch_count = st.session_state[f"{_SK}fetch_count"]
    last_ts = ""
    if last_fetch > 0:
        last_dt = datetime.fromtimestamp(last_fetch)
        last_ts = last_dt.strftime("%H:%M:%S")
    elapsed_s = int(time.time() - last_fetch) if last_fetch > 0 else 0
    next_in = max(0, interval - elapsed_s) if (connected and not paused) else 0

    st.markdown(f"""
    <div style='display:flex;align-items:center;justify-content:space-between;
                background:rgba(255,255,255,0.02);
                border:1px solid rgba(255,255,255,0.06);
                border-radius:10px;padding:.7rem 1.1rem;margin-bottom:1.2rem;
                flex-wrap:wrap;gap:.6rem;'>
        <div style='display:flex;align-items:center;gap:1rem;flex-wrap:wrap;'>
            {badge}
            <span style='font-size:.75rem;color:#4A5568;font-family:"JetBrains Mono",monospace;'>
                Fetches: <span style='color:#64748B;'>{fetch_count}</span>
            </span>
            {'<span style="font-size:.75rem;color:#4A5568;font-family:\'JetBrains Mono\',monospace;">Last: <span style="color:#64748B;">' + last_ts + '</span></span>' if last_ts else ''}
            {('<span style="font-size:.75rem;color:#4A5568;font-family:\'JetBrains Mono\',monospace;">Next refresh: <span style="color:#00D4FF;">' + str(next_in) + 's</span></span>') if (connected and not paused and next_in > 0) else ''}
        </div>
        <div style='font-size:.72rem;color:#4A5568;font-family:"JetBrains Mono",monospace;'>
            Interval: <span style='color:#A0AEC0;'>{interval_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if error:
        st.error(f"Fetch error: {error}")

    if df is None or not connected:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;
                    border:1px dashed rgba(0,212,255,0.12);border-radius:16px;
                    background:rgba(0,0,0,0.15);margin-top:1rem;'>
            <div style='font-size:2.5rem;margin-bottom:.8rem;opacity:.25;'>⟳</div>
            <div style='font-size:.95rem;font-weight:600;color:#4A5568;'>Not connected</div>
            <div style='font-size:.82rem;margin-top:.4rem;color:#2D3748;'>
                Select a demo endpoint or paste a URL above, then click <b style="color:#00D4FF;">Connect & Fetch</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    dt_cols  = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    # ── KPI row ─────────────────────────────────────────────────────────────
    kpi_cols = num_cols[:5]
    if kpi_cols:
        kpi_cards = st.columns(len(kpi_cols))
        palette = ["#00D4FF","#A855F7","#10B981","#F59E0B","#FF006E"]
        for col_w, nc, color in zip(kpi_cards, kpi_cols, palette):
            s = df[nc].dropna()
            prev_val = None
            history = st.session_state[f"{_SK}history"]
            if len(history) > 1:
                try:
                    prev_val = history[-2]["df"][nc].mean()
                except Exception:
                    pass
            delta_val = None
            if prev_val is not None:
                delta_val = f"{((s.mean() - prev_val) / max(abs(prev_val), 1e-9)) * 100:+.2f}%"

            col_w.markdown(f"""
            <div style='background:rgba(255,255,255,0.025);
                        border:1px solid rgba(255,255,255,0.07);
                        border-radius:12px;padding:1.1rem 1.1rem;
                        border-top:2px solid {color};'>
                <div style='font-size:.6rem;font-weight:600;color:#4A5568;
                            text-transform:uppercase;letter-spacing:.1em;
                            font-family:"JetBrains Mono",monospace;margin-bottom:4px;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
                     title='{nc}'>{nc}</div>
                <div style='font-size:1.55rem;font-weight:700;
                            color:{color};font-family:"Space Grotesk",sans-serif;
                            line-height:1.1;'>{s.mean():.4g}</div>
                <div style='font-size:.68rem;color:#4A5568;
                            margin-top:3px;font-family:"JetBrains Mono",monospace;'>
                    {f'<span style="color:{"#10B981" if delta_val and "+" in delta_val else "#FF006E"}">{delta_val}</span> vs prev' if delta_val else f'σ = {s.std():.3g}'}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "Live Chart", "History Trend", "Data Preview", "Column Stats"
    ])

    with tab1:
        if num_cols:
            tc1, tc2 = st.columns([3, 1])
            y_col    = tc1.selectbox("Metric to chart", num_cols, key="lf_ycol")
            color_by = tc2.selectbox("Color by", ["None"] + cat_cols, key="lf_color")
            chart_type = st.radio(
                "Chart style",
                ["Bar", "Histogram", "Box", "Scatter", "Pie"],
                horizontal=True, key="lf_ctype"
            )
            color_val = color_by if color_by != "None" else None

            if chart_type == "Bar" and cat_cols:
                grp = st.selectbox("Group by", cat_cols, key="lf_grp")
                temp = df.groupby(grp)[y_col].mean().nlargest(20).reset_index()
                fig = px.bar(temp, x=y_col, y=grp, orientation="h", color=y_col,
                             color_continuous_scale=["#1E293B","#7C3AED","#00D4FF"],
                             template="plotly_dark", title=f"Avg {y_col} by {grp}",
                             text_auto=".3s")
                fig.update_layout(yaxis={"categoryorder":"total ascending"}, **_PLOTLY_DARK)
            elif chart_type == "Histogram":
                fig = px.histogram(df, x=y_col, nbins=40, color=color_val,
                                   template="plotly_dark", title=f"Distribution: {y_col}",
                                   barmode="overlay", opacity=0.8,
                                   color_discrete_sequence=NEON)
                fig.update_layout(**_PLOTLY_DARK)
            elif chart_type == "Box":
                x_box = color_val
                fig = px.box(df, x=x_box, y=y_col, color=x_box,
                             template="plotly_dark", title=f"Box: {y_col}",
                             points="outliers", color_discrete_sequence=NEON)
                fig.update_layout(**_PLOTLY_DARK)
            elif chart_type == "Scatter" and len(num_cols) >= 2:
                x2 = st.selectbox("X axis", [c for c in num_cols if c != y_col] or num_cols, key="lf_x2")
                fig = px.scatter(df, x=x2, y=y_col, color=color_val,
                                 trendline="ols", opacity=0.75,
                                 template="plotly_dark", title=f"{y_col} vs {x2}",
                                 color_discrete_sequence=NEON)
                fig.update_layout(**_PLOTLY_DARK)
            elif chart_type == "Pie" and cat_cols:
                grp_p = st.selectbox("Category", cat_cols, key="lf_pie_grp")
                temp_p = df.groupby(grp_p)[y_col].sum().nlargest(10).reset_index()
                fig = px.pie(temp_p, names=grp_p, values=y_col, hole=0.42,
                             template="plotly_dark", title=f"{y_col} by {grp_p}",
                             color_discrete_sequence=NEON)
                fig.update_layout(**_PLOTLY_DARK)
            else:
                fig = px.histogram(df, x=y_col, nbins=40, template="plotly_dark",
                                   title=f"Distribution: {y_col}",
                                   color_discrete_sequence=["#00D4FF"])
                fig.update_layout(**_PLOTLY_DARK)

            fig.update_layout(height=440)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns found in the fetched data.")

    with tab2:
        history = st.session_state[f"{_SK}history"]
        if len(history) < 2:
            st.markdown("""
            <div style='text-align:center;padding:2.5rem;
                        border:1px dashed rgba(0,212,255,0.1);border-radius:14px;
                        color:#4A5568;font-size:.85rem;'>
                <div style='font-size:2rem;opacity:.3;margin-bottom:.6rem;'>≈</div>
                Waiting for more data points…<br>
                <span style='font-size:.78rem;color:#2D3748;'>History builds up with each auto-refresh.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if num_cols:
                track_cols = st.multiselect(
                    "Metrics to track",
                    num_cols,
                    default=num_cols[:min(3, len(num_cols))],
                    key="lf_track",
                )
                agg_fn = st.radio(
                    "Aggregate each snapshot by",
                    ["mean", "sum", "max", "min"],
                    horizontal=True, key="lf_agg"
                )
                if track_cols:
                    rows = []
                    for h in history:
                        row = {"Timestamp": h["ts"]}
                        for tc in track_cols:
                            if tc in h["df"].columns:
                                s = h["df"][tc].dropna()
                                row[tc] = getattr(s, agg_fn)() if agg_fn in ("mean","sum","max","min") else s.mean()
                        rows.append(row)
                    hist_df = pd.DataFrame(rows)

                    melt = hist_df.melt(
                        id_vars="Timestamp",
                        value_vars=track_cols,
                        var_name="Metric", value_name="Value"
                    )
                    fig_h = px.line(melt, x="Timestamp", y="Value", color="Metric",
                                    markers=True, template="plotly_dark",
                                    title=f"Live History — {agg_fn} per snapshot",
                                    color_discrete_sequence=NEON)
                    fig_h.update_layout(height=420, **_PLOTLY_DARK)
                    st.plotly_chart(fig_h, use_container_width=True)

                    st.markdown(f"""
                    <div style='display:flex;gap:1rem;flex-wrap:wrap;margin-top:.5rem;'>
                        <div style='background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);
                                    border-radius:10px;padding:.7rem 1.1rem;font-size:.78rem;color:#A0AEC0;'>
                            <span style='color:#00D4FF;font-weight:700;'>{len(history)}</span>
                            &nbsp;snapshots recorded
                        </div>
                        <div style='background:rgba(168,85,247,0.06);border:1px solid rgba(168,85,247,0.15);
                                    border-radius:10px;padding:.7rem 1.1rem;font-size:.78rem;color:#A0AEC0;'>
                            From &nbsp;<span style='color:#A855F7;font-weight:700;'>{history[0]["ts"].strftime("%H:%M:%S")}</span>
                            &nbsp;→&nbsp;<span style='color:#A855F7;font-weight:700;'>{history[-1]["ts"].strftime("%H:%M:%S")}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    csv_hist = hist_df.to_csv(index=False).encode()
                    st.download_button(
                        "Download History CSV",
                        data=csv_hist,
                        file_name="live_feed_history.csv",
                        mime="text/csv",
                    )

    with tab3:
        c1h, c2h = st.columns([3, 1])
        n_rows = c1h.slider("Rows to display", 5, min(500, len(df)), min(50, len(df)), key="lf_rows")
        view   = c2h.radio("From", ["Head", "Tail"], horizontal=True, key="lf_view")
        disp   = df.head(n_rows) if view == "Head" else df.tail(n_rows)
        st.dataframe(disp, use_container_width=True, height=380)

        col_dl1, col_dl2 = st.columns(2)
        col_dl1.download_button(
            "Download Snapshot CSV",
            data=df.to_csv(index=False).encode(),
            file_name=f"live_snapshot_{datetime.now().strftime('%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        import io as _io
        buf_json = _io.BytesIO()
        df.to_json(buf_json, orient="records", indent=2)
        buf_json.seek(0)
        col_dl2.download_button(
            "Download Snapshot JSON",
            data=buf_json,
            file_name=f"live_snapshot_{datetime.now().strftime('%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
                    border-radius:10px;padding:.65rem 1rem;margin-top:.8rem;
                    display:flex;gap:1.5rem;flex-wrap:wrap;'>
            <span style='font-size:.75rem;color:#4A5568;font-family:"JetBrains Mono",monospace;'>
                <span style='color:#00D4FF;'>{df.shape[0]:,}</span> rows
            </span>
            <span style='font-size:.75rem;color:#4A5568;font-family:"JetBrains Mono",monospace;'>
                <span style='color:#A855F7;'>{df.shape[1]}</span> columns
            </span>
            <span style='font-size:.75rem;color:#4A5568;font-family:"JetBrains Mono",monospace;'>
                Missing: <span style='color:#F59E0B;'>{df.isnull().sum().sum():,}</span> cells
            </span>
            <span style='font-size:.75rem;color:#4A5568;font-family:"JetBrains Mono",monospace;'>
                Memory: <span style='color:#10B981;'>{df.memory_usage(deep=True).sum()/1024:.1f} KB</span>
            </span>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        if num_cols:
            desc = df[num_cols].describe(percentiles=[0.25, 0.5, 0.75]).T.round(4)
            desc["skewness"] = df[num_cols].skew().round(4)
            desc["missing%"] = (df[num_cols].isnull().mean() * 100).round(2)
            st.dataframe(desc, use_container_width=True, height=400)

            c1s, c2s = st.columns(2)
            selected = c1s.selectbox("Distribution preview", num_cols, key="lf_dist")
            fig_d = px.histogram(df, x=selected, nbins=40, template="plotly_dark",
                                 title=f"Distribution: {selected}",
                                 color_discrete_sequence=["#00D4FF"])
            fig_d.update_layout(height=300, **_PLOTLY_DARK)
            c2s.plotly_chart(fig_d, use_container_width=True)
        else:
            st.info("No numeric columns in this dataset.")
