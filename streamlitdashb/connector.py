import streamlit as st
import pandas as pd
import requests
import io
import json
from .styles import DARK_CSS, section_header, kpi_row_html

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,21,40,1)",
    font=dict(family="Inter", color="#E2E8F0"),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
)


def _save(df, fname):
    df.columns = [str(c).strip() for c in df.columns]
    st.session_state["raw_data"] = df.copy()
    st.session_state["clean_data"] = df.copy()
    st.session_state["filename"] = fname
    return df


def connect_page():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header(
        "🔌", "Connect & Import",
        "Load data from URLs, APIs, Google Sheets, databases, or merge multiple files"
    ), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌐 URL / API", "📊 Google Sheets", "🗄️ Database", "🔗 Merge Files"
    ])

    # ── Tab 1: URL / API ───────────────────────────────────────────────────────
    with tab1:
        st.markdown("""
        <div style="background:rgba(56,189,248,.05);border:1px solid rgba(56,189,248,.15);
                    border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.25rem;
                    color:#6b7280;font-size:.86rem;line-height:1.7;">
          <b style="color:#38bdf8;">Paste any public URL</b> that returns CSV, JSON, Excel, or Parquet.
          You can also call REST APIs that return JSON arrays. Add auth headers if needed.
        </div>
        """, unsafe_allow_html=True)

        url = st.text_input(
            "Data URL",
            placeholder="https://example.com/data.csv  or  https://api.example.com/records",
            key="conn_url"
        )
        c1, c2 = st.columns(2)
        with c1:
            fmt = st.selectbox("Format", ["Auto-detect", "CSV", "JSON", "Excel", "Parquet"], key="conn_fmt")
        with c2:
            json_key = st.text_input("JSON data key (optional)", placeholder="results, data, items…", key="conn_jkey",
                                     help="If the API returns {data: [...]} enter 'data' here")

        headers_raw = st.text_area(
            "HTTP Headers (JSON, optional)",
            placeholder='{"Authorization": "Bearer YOUR_TOKEN", "X-Api-Key": "key"}',
            height=70, key="conn_headers"
        )

        if st.button("🔗 Fetch Data", key="url_fetch", use_container_width=True):
            if not url.strip():
                st.error("Please enter a URL.")
            else:
                try:
                    hdrs = {}
                    if headers_raw.strip():
                        hdrs = json.loads(headers_raw)
                    with st.spinner("Fetching…"):
                        resp = requests.get(url.strip(), headers=hdrs, timeout=30)
                        resp.raise_for_status()

                    ct = resp.headers.get("content-type", "")
                    ext = url.split("?")[0].rsplit(".", 1)[-1].lower()

                    if fmt == "CSV" or (fmt == "Auto-detect" and (ext in ("csv", "tsv") or "text/csv" in ct or "text/plain" in ct)):
                        df = pd.read_csv(io.StringIO(resp.text))
                    elif fmt == "JSON" or (fmt == "Auto-detect" and (ext == "json" or "json" in ct)):
                        data = resp.json()
                        if json_key and json_key in data:
                            data = data[json_key]
                        if isinstance(data, list):
                            df = pd.DataFrame(data)
                        elif isinstance(data, dict):
                            found = False
                            for v in data.values():
                                if isinstance(v, list) and v:
                                    df = pd.DataFrame(v)
                                    found = True
                                    break
                            if not found:
                                df = pd.DataFrame([data])
                        else:
                            st.error("Unrecognized JSON structure.")
                            st.stop()
                    elif fmt == "Parquet" or ext == "parquet":
                        df = pd.read_parquet(io.BytesIO(resp.content))
                    elif fmt == "Excel" or ext in ("xlsx", "xls"):
                        df = pd.read_excel(io.BytesIO(resp.content))
                    else:
                        try:
                            df = pd.read_csv(io.StringIO(resp.text))
                        except Exception:
                            data = resp.json()
                            df = pd.DataFrame(data if isinstance(data, list) else [data])

                    fname = url.split("?")[0].rsplit("/", 1)[-1] or "api_data.csv"
                    df = _save(df, fname)
                    st.success(f"✅ Loaded **{df.shape[0]:,} rows × {df.shape[1]} columns** from URL")
                    st.markdown(kpi_row_html([
                        ("Rows", f"{df.shape[0]:,}"), ("Columns", df.shape[1]),
                        ("Numeric", df.select_dtypes("number").shape[1]),
                        ("Missing", int(df.isnull().sum().sum())),
                    ]), unsafe_allow_html=True)
                    st.dataframe(df.head(50), use_container_width=True, hide_index=True)
                except requests.exceptions.HTTPError as e:
                    st.error(f"HTTP error {e.response.status_code}: {e}")
                except Exception as e:
                    st.error(f"Failed to fetch: {e}")

        st.markdown("---")
        st.markdown("""
        <div style="font-size:.78rem;color:#475569;line-height:1.8;">
          <b style="color:#94A3B8;">Example public URLs to try:</b><br>
          • <code>https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv</code><br>
          • <code>https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv</code><br>
          • <code>https://jsonplaceholder.typicode.com/users</code> (JSON API)
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 2: Google Sheets ───────────────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style="background:rgba(74,222,128,.05);border:1px solid rgba(74,222,128,.15);
                    border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.25rem;
                    color:#6b7280;font-size:.86rem;line-height:1.7;">
          <b style="color:#4ade80;">Works with public Google Sheets.</b>
          Share your sheet → "Anyone with the link can view", then paste the URL below.
        </div>
        """, unsafe_allow_html=True)

        sheets_url = st.text_input(
            "Google Sheets URL",
            placeholder="https://docs.google.com/spreadsheets/d/SHEET_ID/edit...",
            key="gsheets_url"
        )
        sheet_idx = st.number_input("Sheet index (0 = first sheet)", min_value=0, max_value=20, value=0, key="gsheets_idx")

        if st.button("📊 Import from Google Sheets", key="gsheets_fetch", use_container_width=True):
            if not sheets_url.strip():
                st.error("Please enter a Google Sheets URL.")
            else:
                try:
                    import re
                    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheets_url)
                    if not match:
                        st.error("Could not extract Sheet ID from URL. Make sure it's a valid Google Sheets link.")
                        st.stop()

                    sheet_id = match.group(1)
                    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={sheet_idx}"

                    with st.spinner("Connecting to Google Sheets…"):
                        resp = requests.get(export_url, timeout=30)
                        if resp.status_code == 403:
                            st.error("Access denied. Make sure the sheet is shared as 'Anyone with the link can view'.")
                            st.stop()
                        resp.raise_for_status()
                        df = pd.read_csv(io.StringIO(resp.text))

                    fname = f"sheets_{sheet_id[:8]}.csv"
                    df = _save(df, fname)
                    st.success(f"✅ Imported **{df.shape[0]:,} rows × {df.shape[1]} columns** from Google Sheets")
                    st.markdown(kpi_row_html([
                        ("Rows", f"{df.shape[0]:,}"), ("Columns", df.shape[1]),
                        ("Numeric", df.select_dtypes("number").shape[1]),
                        ("Missing", int(df.isnull().sum().sum())),
                    ]), unsafe_allow_html=True)
                    st.dataframe(df.head(50), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Import failed: {e}")

    # ── Tab 3: Database ────────────────────────────────────────────────────────
    with tab3:
        st.markdown("""
        <div style="background:rgba(168,85,247,.05);border:1px solid rgba(168,85,247,.15);
                    border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.25rem;
                    color:#6b7280;font-size:.86rem;line-height:1.7;">
          <b style="color:#a855f7;">Connect to a database</b> and run a SQL query to load data.
          Supports SQLite (local file) and PostgreSQL.
        </div>
        """, unsafe_allow_html=True)

        db_type = st.selectbox("Database type", ["SQLite", "PostgreSQL", "MySQL"], key="db_type")

        if db_type == "SQLite":
            sqlite_path = st.text_input("SQLite file path", placeholder="/path/to/database.db", key="sqlite_path")
            conn_str_final = f"sqlite:///{sqlite_path}" if sqlite_path else ""
        elif db_type == "PostgreSQL":
            c1, c2, c3 = st.columns(3)
            with c1:
                pg_host = st.text_input("Host", "localhost", key="pg_host")
                pg_db = st.text_input("Database", key="pg_db")
            with c2:
                pg_port = st.number_input("Port", value=5432, key="pg_port")
                pg_user = st.text_input("Username", key="pg_user")
            with c3:
                pg_pass = st.text_input("Password", type="password", key="pg_pass")
            conn_str_final = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                my_host = st.text_input("Host", "localhost", key="my_host")
                my_db = st.text_input("Database", key="my_db")
            with c2:
                my_port = st.number_input("Port", value=3306, key="my_port")
                my_user = st.text_input("Username", key="my_user")
            with c3:
                my_pass = st.text_input("Password", type="password", key="my_pass")
            conn_str_final = f"mysql+pymysql://{my_user}:{my_pass}@{my_host}:{my_port}/{my_db}"

        sql_query = st.text_area("SQL Query", value="SELECT * FROM table_name LIMIT 1000", height=100, key="db_sql")

        if st.button("🗄️ Run Query", key="db_run", use_container_width=True):
            if not conn_str_final or conn_str_final.endswith("///"):
                st.error("Please fill in connection details.")
            else:
                try:
                    from sqlalchemy import create_engine, text
                    with st.spinner("Connecting and running query…"):
                        engine = create_engine(conn_str_final)
                        with engine.connect() as conn:
                            df = pd.read_sql(text(sql_query), conn)
                    df = _save(df, f"db_query_{db_type.lower()}.csv")
                    st.success(f"✅ Query returned **{df.shape[0]:,} rows × {df.shape[1]} columns**")
                    st.dataframe(df.head(100), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Database error: {e}")

        if db_type == "SQLite" and conn_str_final and conn_str_final != "sqlite:///":
            if st.button("List Tables", key="db_list_tables"):
                try:
                    from sqlalchemy import create_engine, inspect
                    engine = create_engine(conn_str_final)
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                                border-radius:8px;padding:.75rem 1rem;font-size:.85rem;color:#94A3B8;">
                      <b style="color:#f1f2f6;">Tables:</b> {", ".join(tables) if tables else "No tables found"}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Could not list tables: {e}")

    # ── Tab 4: Merge Files ─────────────────────────────────────────────────────
    with tab4:
        st.markdown("""
        <div style="background:rgba(251,191,36,.05);border:1px solid rgba(251,191,36,.15);
                    border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.25rem;
                    color:#6b7280;font-size:.86rem;line-height:1.7;">
          <b style="color:#fbbf24;">Upload two files</b> and join them on a shared column — like SQL JOIN.
          The merged result becomes your active dataset.
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.5rem;">File A (Left)</div>', unsafe_allow_html=True)
            file_a = st.file_uploader("Upload File A", type=["csv", "xlsx", "json", "parquet"], key="merge_a", label_visibility="collapsed")
        with col_b:
            st.markdown('<div style="font-weight:600;color:#f1f2f6;margin-bottom:.5rem;">File B (Right)</div>', unsafe_allow_html=True)
            file_b = st.file_uploader("Upload File B", type=["csv", "xlsx", "json", "parquet"], key="merge_b", label_visibility="collapsed")

        if file_a and file_b:
            def _read_up(f):
                ext = f.name.rsplit(".", 1)[-1].lower()
                if ext == "csv":     return pd.read_csv(f)
                if ext in ("xlsx", "xls"): return pd.read_excel(f)
                if ext == "json":   return pd.read_json(f)
                if ext == "parquet": return pd.read_parquet(f)
                return pd.read_csv(f)

            df_a = _read_up(file_a)
            df_b = _read_up(file_b)

            st.markdown(f"""
            <div style="display:flex;gap:1rem;margin:.75rem 0;">
              <div style="flex:1;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                          border-radius:10px;padding:.75rem 1rem;">
                <div style="font-weight:700;color:#f1f2f6;font-size:.85rem;">A: {file_a.name}</div>
                <div style="color:#818cf8;font-size:.75rem;margin-top:2px;">{df_a.shape[0]:,} rows · {df_a.shape[1]} cols</div>
              </div>
              <div style="flex:1;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
                          border-radius:10px;padding:.75rem 1rem;">
                <div style="font-weight:700;color:#f1f2f6;font-size:.85rem;">B: {file_b.name}</div>
                <div style="color:#818cf8;font-size:.75rem;margin-top:2px;">{df_b.shape[0]:,} rows · {df_b.shape[1]} cols</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            common_cols = list(set(df_a.columns) & set(df_b.columns))
            c1, c2, c3 = st.columns(3)
            with c1:
                join_key = st.selectbox("Join on column", common_cols if common_cols else list(df_a.columns), key="merge_key")
            with c2:
                join_type = st.selectbox("Join type", ["inner", "left", "right", "outer"], key="merge_type")
            with c3:
                merge_fname = st.text_input("Result filename", value="merged_data.csv", key="merge_fname")

            if not common_cols:
                left_col = st.selectbox("Left key column", df_a.columns, key="merge_lkey")
                right_col = st.selectbox("Right key column", df_b.columns, key="merge_rkey")
                join_key = None

            if st.button("🔗 Merge Files", key="do_merge", use_container_width=True):
                try:
                    if join_key:
                        merged = pd.merge(df_a, df_b, on=join_key, how=join_type)
                    else:
                        merged = pd.merge(df_a, df_b, left_on=left_col, right_on=right_col, how=join_type)

                    merged = _save(merged, merge_fname)
                    st.success(f"✅ Merged: **{merged.shape[0]:,} rows × {merged.shape[1]} columns** ({join_type} join)")
                    st.markdown(kpi_row_html([
                        ("Result Rows", f"{merged.shape[0]:,}"),
                        ("Columns", merged.shape[1]),
                        ("A Rows", f"{df_a.shape[0]:,}"),
                        ("B Rows", f"{df_b.shape[0]:,}"),
                    ]), unsafe_allow_html=True)
                    st.dataframe(merged.head(100), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Merge failed: {e}")
        else:
            st.markdown("""
            <div style="border:2px dashed rgba(251,191,36,.2);border-radius:12px;padding:2.5rem;
                        text-align:center;color:#475569;margin-top:.5rem;">
              <div style="font-size:2rem;margin-bottom:.5rem;">🔗</div>
              <div style="color:#94A3B8;font-size:.9rem;">Upload both files above to configure the merge</div>
            </div>
            """, unsafe_allow_html=True)
