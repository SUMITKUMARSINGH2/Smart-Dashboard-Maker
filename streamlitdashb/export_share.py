import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import base64
import datetime
from .styles import DARK_CSS, section_header, kpi_row_html


def _df_to_b64_csv(df: pd.DataFrame) -> str:
    return base64.b64encode(df.to_csv(index=False).encode()).decode()


def _generate_html_report(df: pd.DataFrame, fname: str) -> str:
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    missing = int(df.isnull().sum().sum())
    dups = int(df.duplicated().sum())
    now = datetime.datetime.now().strftime("%B %d, %Y %H:%M")

    col_info_rows = ""
    for col in df.columns:
        s = df[col]
        null_p = round(s.isnull().mean() * 100, 1)
        uniq = s.nunique()
        sample = str(s.dropna().iloc[0]) if s.notna().any() else "—"
        col_info_rows += f"""
        <tr>
          <td>{col}</td>
          <td>{str(s.dtype)}</td>
          <td>{null_p}%</td>
          <td>{uniq:,}</td>
          <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;">{sample[:60]}</td>
        </tr>"""

    stats_rows = ""
    if num_cols:
        desc = df[num_cols].describe().T
        for col, row in desc.iterrows():
            stats_rows += f"""
            <tr>
              <td>{col}</td>
              <td>{row.get('mean', 0):.4g}</td>
              <td>{row.get('std', 0):.4g}</td>
              <td>{row.get('min', 0):.4g}</td>
              <td>{row.get('50%', 0):.4g}</td>
              <td>{row.get('max', 0):.4g}</td>
            </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>DataViz Pro — Report: {fname}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #07090f; color: #e8eaf6; padding: 2rem; }}
  h1 {{ font-size: 2rem; font-weight: 900; margin-bottom: .25rem;
        background: linear-gradient(90deg,#ff0066,#ff6600,#ffcc00,#00ff88,#00cfff,#6600ff,#ff00cc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  h2 {{ font-size: 1.1rem; font-weight: 700; color: #818cf8; margin: 2rem 0 .75rem;
        border-bottom: 1px solid rgba(255,255,255,.08); padding-bottom: .4rem; }}
  .meta {{ color: #7c7f96; font-size: .82rem; margin-bottom: 2rem; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: .75rem; margin-bottom: 1.5rem; }}
  .kpi {{ background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
          border-radius: 12px; padding: 1rem 1.25rem; }}
  .kpi-val {{ font-size: 1.6rem; font-weight: 800; color: #818cf8; }}
  .kpi-lab {{ font-size: .65rem; color: #7c7f96; text-transform: uppercase; letter-spacing: .1em; margin-top: 3px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .82rem; margin-bottom: 1rem; }}
  th {{ background: rgba(129,140,248,.1); color: #818cf8; padding: .5rem .75rem; text-align: left;
        font-weight: 600; font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; }}
  td {{ padding: .45rem .75rem; color: #94A3B8; border-bottom: 1px solid rgba(255,255,255,.04); }}
  tr:hover td {{ background: rgba(255,255,255,.02); }}
  .footer {{ margin-top: 3rem; color: #3d3f52; font-size: .72rem; text-align: center; }}
</style>
</head>
<body>
  <h1>DataViz Pro</h1>
  <div class="meta">Dataset: <b style="color:#f1f2f6;">{fname}</b> &nbsp;·&nbsp; Generated: {now}</div>

  <div class="kpi-grid">
    <div class="kpi"><div class="kpi-val">{df.shape[0]:,}</div><div class="kpi-lab">Total Rows</div></div>
    <div class="kpi"><div class="kpi-val">{df.shape[1]}</div><div class="kpi-lab">Columns</div></div>
    <div class="kpi"><div class="kpi-val">{missing:,}</div><div class="kpi-lab">Missing Values</div></div>
    <div class="kpi"><div class="kpi-val">{dups:,}</div><div class="kpi-lab">Duplicates</div></div>
  </div>

  <h2>Column Overview</h2>
  <table>
    <tr><th>Column</th><th>Type</th><th>Null %</th><th>Unique</th><th>Sample Value</th></tr>
    {col_info_rows}
  </table>

  {"<h2>Numeric Statistics</h2><table><tr><th>Column</th><th>Mean</th><th>Std Dev</th><th>Min</th><th>Median</th><th>Max</th></tr>" + stats_rows + "</table>" if num_cols else ""}

  <div class="footer">⬡ DataViz Pro — v2.0 · Automatically generated report</div>
</body>
</html>"""
    return html


def _snapshot_state() -> dict:
    snap = {}
    df = st.session_state.get("clean_data")
    if df is not None:
        snap["dataframe"] = df.to_json(orient="split", date_format="iso")
    snap["filename"] = st.session_state.get("filename", "")
    snap["exported_at"] = datetime.datetime.now().isoformat()
    snap["shape"] = list(df.shape) if df is not None else [0, 0]
    return snap


def _restore_snapshot(snap: dict):
    if "dataframe" in snap:
        df = pd.read_json(snap["dataframe"], orient="split")
        st.session_state["raw_data"] = df.copy()
        st.session_state["clean_data"] = df.copy()
    if "filename" in snap:
        st.session_state["filename"] = snap["filename"]


def export_share_page():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header(
        "📤", "Export & Share",
        "PDF report, shareable snapshots & data refresh"
    ), unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📄 PDF Report", "💾 Snapshot", "🔄 Data Refresh"])

    # ── Tab 1: PDF / HTML Report ───────────────────────────────────────────────
    with tab1:
        st.markdown("""
        <div style="background:rgba(129,140,248,.05);border:1px solid rgba(129,140,248,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;">
          Generate a rich HTML report with KPIs, column profiles and numeric statistics.
          Download and open in any browser — or print to PDF from there.
        </div>
        """, unsafe_allow_html=True)

        if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
            st.warning("⚠️ No data loaded. Please upload a file first.")
        else:
            df = st.session_state["clean_data"]
            fname = st.session_state.get("filename", "dataset")

            st.markdown(f"""
            <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem;">
              <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                          border-radius:10px;padding:.75rem 1.1rem;min-width:130px;">
                <div style="font-size:1.3rem;font-weight:800;color:#818cf8;">{df.shape[0]:,}</div>
                <div style="font-size:.65rem;color:#7c7f96;text-transform:uppercase;letter-spacing:.08em;">Rows</div>
              </div>
              <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                          border-radius:10px;padding:.75rem 1.1rem;min-width:130px;">
                <div style="font-size:1.3rem;font-weight:800;color:#f472b6;">{df.shape[1]}</div>
                <div style="font-size:.65rem;color:#7c7f96;text-transform:uppercase;letter-spacing:.08em;">Columns</div>
              </div>
              <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                          border-radius:10px;padding:.75rem 1.1rem;min-width:130px;">
                <div style="font-size:1.3rem;font-weight:800;color:#4ade80;">{len(df.select_dtypes('number').columns)}</div>
                <div style="font-size:.65rem;color:#7c7f96;text-transform:uppercase;letter-spacing:.08em;">Numeric Cols</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📄 Generate HTML Report", use_container_width=True, key="gen_html_rpt"):
                html_content = _generate_html_report(df, fname)
                b64 = base64.b64encode(html_content.encode()).decode()
                report_name = f"datavizpro_report_{fname.rsplit('.', 1)[0]}.html"
                st.download_button(
                    label="⬇️ Download Report",
                    data=html_content.encode("utf-8"),
                    file_name=report_name,
                    mime="text/html",
                    use_container_width=True,
                    key="dl_html_rpt"
                )
                st.success("✅ Report ready! Click Download Report above.")
                with st.expander("Preview report"):
                    st.components.v1.html(html_content, height=600, scrolling=True)

            st.markdown("---")
            st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.5rem;">Download Cleaned Data</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button(
                    "⬇️ CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    file_name=f"cleaned_{fname.rsplit('.', 1)[0]}.csv",
                    mime="text/csv", use_container_width=True, key="dl_csv"
                )
            with c2:
                buf = io.BytesIO()
                df.to_excel(buf, index=False, engine="openpyxl")
                st.download_button(
                    "⬇️ Excel",
                    buf.getvalue(),
                    file_name=f"cleaned_{fname.rsplit('.', 1)[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, key="dl_xlsx"
                )
            with c3:
                buf2 = io.BytesIO()
                df.to_parquet(buf2, index=False)
                st.download_button(
                    "⬇️ Parquet",
                    buf2.getvalue(),
                    file_name=f"cleaned_{fname.rsplit('.', 1)[0]}.parquet",
                    mime="application/octet-stream",
                    use_container_width=True, key="dl_parquet"
                )

    # ── Tab 2: Snapshot ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style="background:rgba(74,222,128,.05);border:1px solid rgba(74,222,128,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;">
          Save the current dataset and session state as a JSON snapshot.
          Restore it later to pick up exactly where you left off.
        </div>
        """, unsafe_allow_html=True)

        col_save, col_load = st.columns(2)

        with col_save:
            st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.75rem;">💾 Save Snapshot</div>', unsafe_allow_html=True)
            if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
                st.info("No data loaded to snapshot.")
            else:
                snap_name = st.text_input("Snapshot name", value=f"snapshot_{datetime.date.today()}", key="snap_name")
                if st.button("📸 Save Snapshot", use_container_width=True, key="save_snap"):
                    snap = _snapshot_state()
                    snap["name"] = snap_name
                    snap_json = json.dumps(snap, indent=2)
                    st.download_button(
                        "⬇️ Download Snapshot JSON",
                        snap_json.encode("utf-8"),
                        file_name=f"{snap_name}.dvp.json",
                        mime="application/json",
                        use_container_width=True,
                        key="dl_snap"
                    )
                    st.success(f"✅ Snapshot '{snap_name}' ready to download!")
                    df = st.session_state["clean_data"]
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
                                border-radius:8px;padding:.65rem 1rem;margin-top:.5rem;font-size:.8rem;color:#7c7f96;">
                      Contains: <b style="color:#f1f2f6;">{df.shape[0]:,} rows × {df.shape[1]} cols</b>
                      &nbsp;·&nbsp; Filename: <b style="color:#f1f2f6;">{st.session_state.get('filename','')}</b>
                    </div>
                    """, unsafe_allow_html=True)

        with col_load:
            st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.75rem;">📂 Restore Snapshot</div>', unsafe_allow_html=True)
            snap_file = st.file_uploader("Upload .dvp.json snapshot", type=["json"], key="snap_upload", label_visibility="collapsed")
            if snap_file:
                try:
                    snap = json.loads(snap_file.read().decode("utf-8"))
                    rows, cols = snap.get("shape", [0, 0])
                    exported = snap.get("exported_at", "unknown")[:19]
                    st.markdown(f"""
                    <div style="background:rgba(74,222,128,.06);border:1px solid rgba(74,222,128,.2);
                                border-radius:8px;padding:.65rem 1rem;font-size:.82rem;color:#7c7f96;margin-bottom:.75rem;">
                      <b style="color:#4ade80;">Snapshot found:</b> {snap.get('name', 'unnamed')}<br>
                      {rows:,} rows · {cols} cols · Saved: {exported}
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("✅ Restore This Snapshot", use_container_width=True, key="restore_snap"):
                        _restore_snapshot(snap)
                        st.success("✅ Snapshot restored! Your dataset is now active.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Could not read snapshot: {e}")

    # ── Tab 3: Data Refresh ────────────────────────────────────────────────────
    with tab3:
        st.markdown("""
        <div style="background:rgba(56,189,248,.05);border:1px solid rgba(56,189,248,.15);
                    border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;font-size:.83rem;color:#7c7f96;">
          Configure a URL data source and refresh the dataset manually or on a timer.
          Useful for keeping live API/CSV feeds up-to-date.
        </div>
        """, unsafe_allow_html=True)

        refresh_url = st.text_input(
            "Data source URL",
            value=st.session_state.get("refresh_url", ""),
            placeholder="https://example.com/live_data.csv",
            key="refresh_url_input"
        )
        c1, c2 = st.columns(2)
        with c1:
            refresh_fmt = st.selectbox("Format", ["CSV", "JSON"], key="refresh_fmt")
        with c2:
            refresh_interval = st.selectbox(
                "Auto-refresh interval",
                ["Manual only", "30 seconds", "1 minute", "5 minutes", "15 minutes"],
                key="refresh_interval"
            )

        if st.button("🔄 Refresh Now", use_container_width=True, key="do_refresh"):
            url = refresh_url.strip()
            if not url:
                st.error("Please enter a URL.")
            else:
                import requests
                try:
                    with st.spinner("Fetching latest data…"):
                        resp = requests.get(url, timeout=30)
                        resp.raise_for_status()
                        if refresh_fmt == "CSV":
                            df = pd.read_csv(io.StringIO(resp.text))
                        else:
                            data = resp.json()
                            df = pd.DataFrame(data if isinstance(data, list) else [data])

                    df.columns = [str(c).strip() for c in df.columns]
                    st.session_state["raw_data"] = df.copy()
                    st.session_state["clean_data"] = df.copy()
                    st.session_state["refresh_url"] = url
                    st.session_state["last_refresh"] = datetime.datetime.now().strftime("%H:%M:%S")
                    st.success(f"✅ Data refreshed — {df.shape[0]:,} rows × {df.shape[1]} cols")
                    st.dataframe(df.head(20), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Refresh failed: {e}")

        if "last_refresh" in st.session_state:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
                        border-radius:8px;padding:.6rem 1rem;margin-top:.5rem;font-size:.8rem;color:#7c7f96;">
              Last refreshed at <b style="color:#4ade80;">{st.session_state['last_refresh']}</b>
            </div>
            """, unsafe_allow_html=True)

        if refresh_interval != "Manual only":
            interval_map = {
                "30 seconds": 30, "1 minute": 60,
                "5 minutes": 300, "15 minutes": 900
            }
            secs = interval_map[refresh_interval]
            st.markdown(f"""
            <div style="background:rgba(251,191,36,.05);border:1px solid rgba(251,191,36,.15);
                        border-radius:8px;padding:.6rem 1rem;margin-top:.75rem;font-size:.82rem;color:#7c7f96;">
              ⏱ Auto-refresh set to every <b style="color:#fbbf24;">{refresh_interval}</b>.
              The page will reload automatically.
            </div>
            """, unsafe_allow_html=True)
            import time
            time.sleep(0.5)
            st.rerun()
