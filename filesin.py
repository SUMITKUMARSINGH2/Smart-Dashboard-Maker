import streamlit as st
import pandas as pd
from styles import DARK_CSS, section_header, kpi_row_html

def file_upload():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header("⬆", "Upload Data", "Supports CSV, Excel, JSON, Parquet, TSV"), unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(0,212,255,.04);border:1px solid rgba(0,212,255,.15);
                border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.5rem;
                color:#94A3B8;font-size:.88rem;line-height:1.6;">
      <b style="color:#00D4FF;">Supported formats:</b> CSV · Excel (.xlsx, .xls) · JSON · Parquet (.parquet)<br>
      <b style="color:#00D4FF;">Tips:</b> For large files, ensure clean column headers. UTF-8 encoding is recommended.
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
