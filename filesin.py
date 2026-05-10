import streamlit as st
import pandas as pd
from styles import DARK_CSS, section_header, kpi_row_html
from shared_store import save_shared, load_shared, get_meta as bridge_meta, bridge_exists

def file_upload():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header("⬆", "Upload Data", "Supports CSV, Excel, JSON, Parquet, TSV"), unsafe_allow_html=True)

    # Bridge banner — sync from Flask if available
    if bridge_exists():
        meta = bridge_meta()
        if meta and meta.get("source") == "flask":
            bridge_file = meta.get("filename", "")
            session_file = st.session_state.get("filename", "")
            if bridge_file != session_file:
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"""
                    <div style="background:linear-gradient(90deg,rgba(124,58,237,.1),rgba(0,212,255,.07));
                                border:1px solid rgba(0,212,255,.2);border-radius:7px;
                                padding:.55rem .9rem;font-size:.82rem;color:#CBD5E1;">
                      <span style="color:#00D4FF;">⟳</span>
                      Flask loaded <b style="color:#E2E8F0;">{bridge_file}</b>
                      ({meta.get('rows',0):,} rows). Click to sync.
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    if st.button("Sync", use_container_width=True, key="filesin_sync_btn"):
                        df_b, _ = load_shared()
                        if df_b is not None:
                            st.session_state["raw_data"]   = df_b.copy()
                            st.session_state["clean_data"] = df_b.copy()
                            st.session_state["filename"]   = bridge_file
                            st.rerun()

    st.markdown("""
    <div style="background:rgba(56,189,248,.05);border:1px solid rgba(56,189,248,.15);
                border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.5rem;
                color:#6b7280;font-size:.86rem;line-height:1.7;">
      <b style="color:#38bdf8;">Supported formats:</b> CSV · Excel (.xlsx, .xls) · JSON · Parquet (.parquet)<br>
      <b style="color:#38bdf8;">Tips:</b> For large files, ensure clean column headers. UTF-8 encoding is recommended.
    </div>
    """, unsafe_allow_html=True)

    col_opt, col_main = st.columns([1, 3])

    with col_opt:
        st.markdown('<div style="font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:#475569;margin-bottom:.5rem;">Options</div>', unsafe_allow_html=True)
        sep = st.selectbox("CSV Separator", [",", ";", "\\t", "|"], help="Delimiter for CSV files")
        enc = st.selectbox("Encoding", ["utf-8", "latin-1", "cp1252", "iso-8859-1"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:#475569;margin-bottom:.5rem;">Sample Datasets</div>', unsafe_allow_html=True)
        samples = ["titanic", "tips", "iris", "diamonds", "penguins", "mpg", "flights"]
        sample_choice = st.selectbox("Load sample", ["— choose —"] + samples)
        if st.button("Load Sample", use_container_width=True) and sample_choice != "— choose —":
            try:
                import seaborn as sns
                df = sns.load_dataset(sample_choice)
                st.session_state["raw_data"] = df.copy()
                st.session_state["clean_data"] = df.copy()
                st.session_state["filename"] = f"{sample_choice}.csv"
                save_shared(df, f"{sample_choice}.csv", source="streamlit")
                st.success(f"✅ Loaded '{sample_choice}' — {df.shape[0]:,} rows, {df.shape[1]} cols")
                st.rerun()
            except Exception as e:
                st.error(f"Could not load sample: {e}")

    with col_main:
        uploaded = st.file_uploader(
            "Drop your file here, or click to browse",
            type=["csv", "xlsx", "xls", "json", "parquet", "tsv"],
            label_visibility="collapsed",
        )

        if uploaded is not None:
            try:
                ext = uploaded.name.rsplit(".", 1)[-1].lower()
                sep_val = "\t" if sep == "\\t" else sep

                with st.spinner("Reading file..."):
                    if ext == "csv":
                        df = pd.read_csv(uploaded, sep=sep_val, encoding=enc)
                    elif ext in ("xlsx", "xls"):
                        df = pd.read_excel(uploaded)
                    elif ext == "json":
                        df = pd.read_json(uploaded)
                    elif ext == "parquet":
                        df = pd.read_parquet(uploaded)
                    elif ext == "tsv":
                        df = pd.read_csv(uploaded, sep="\t", encoding=enc)
                    else:
                        st.error(f"Unsupported format: {ext}")
                        return

                df.columns = [str(c).strip() for c in df.columns]
                st.session_state["raw_data"] = df.copy()
                st.session_state["clean_data"] = df.copy()
                st.session_state["filename"] = uploaded.name
                save_shared(df, uploaded.name, source="streamlit")

            except Exception as e:
                st.error(f"Failed to read file: {e}")
                return

        if "clean_data" in st.session_state and st.session_state["clean_data"] is not None:
            df = st.session_state["clean_data"]
            fname = st.session_state.get("filename", "dataset")

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:.5rem;padding:.6rem 0;
                        color:#10B981;font-size:.9rem;font-weight:600;">
              ✓ {fname} loaded successfully
            </div>
            """, unsafe_allow_html=True)

            num_cols = df.select_dtypes(include=["int64","float64"]).shape[1]
            cat_cols = df.select_dtypes(include=["object","category"]).shape[1]
            missing = int(df.isnull().sum().sum())

            st.markdown(kpi_row_html([
                ("Rows", f"{df.shape[0]:,}"),
                ("Columns", df.shape[1]),
                ("Numeric", num_cols),
                ("Categorical", cat_cols),
                ("Missing", missing),
                ("Duplicates", int(df.duplicated().sum())),
            ]), unsafe_allow_html=True)

            st.markdown('<div style="font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:#475569;margin:1rem 0 .5rem;">Data Preview</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, height=420, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("◎ Profile Data →", use_container_width=True):
                    st.session_state["nav"] = "Data Profiling"
                    st.rerun()
            with col2:
                if st.button("✦ Clean Data →", use_container_width=True):
                    st.session_state["nav"] = "Data Overview"
                    st.rerun()
            with col3:
                if st.button("⚡ Auto Dashboard →", use_container_width=True):
                    st.session_state["nav"] = "Dashboard Generator"
                    st.rerun()
        else:
            st.markdown("""
            <div style="border:2px dashed #1E293B;border-radius:10px;padding:3rem 2rem;
                        text-align:center;color:#475569;margin-top:1rem;">
              <div style="font-size:2.5rem;margin-bottom:.75rem;">📂</div>
              <div style="font-size:.95rem;font-weight:600;color:#94A3B8;margin-bottom:.4rem;">No file uploaded yet</div>
              <div style="font-size:.82rem;">Use the file uploader above or load a sample dataset</div>
            </div>
            """, unsafe_allow_html=True)
