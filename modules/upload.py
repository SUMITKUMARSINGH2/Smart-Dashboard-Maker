import streamlit as st
import pandas as pd
import io


def upload_page():
    st.markdown("""
    <div class="main-header">
        <h1>☁️ Upload Data</h1>
        <p>Upload your dataset to get started. Supports CSV, Excel, JSON, and Parquet.</p>
    </div>
    """, unsafe_allow_html=True)

    upload_col, info_col = st.columns([2, 1])

    with upload_col:
        uploaded = st.file_uploader(
            "Drop your file here or click to browse",
            type=["csv", "xlsx", "xls", "json", "parquet"],
            help="Max file size: 200 MB"
        )

    with info_col:
        st.markdown("""
        **Supported Formats**
        - 📄 CSV (comma/semicolon separated)
        - 📊 Excel (.xlsx, .xls)
        - 🗂️ JSON (records or split)
        - 🗃️ Parquet
        """)

    if uploaded:
        with st.spinner("Reading file..."):
            try:
                name = uploaded.name
                ext = name.rsplit(".", 1)[-1].lower()

                if ext == "csv":
                    sample = uploaded.read(4096).decode("utf-8", errors="replace")
                    uploaded.seek(0)
                    sep = ";" if sample.count(";") > sample.count(",") else ","
                    df = pd.read_csv(uploaded, sep=sep, low_memory=False)
                elif ext in ("xlsx", "xls"):
                    xl = pd.ExcelFile(uploaded)
                    sheets = xl.sheet_names
                    if len(sheets) > 1:
                        sheet = st.selectbox("Select sheet", sheets)
                    else:
                        sheet = sheets[0]
                    df = pd.read_excel(uploaded, sheet_name=sheet)
                elif ext == "json":
                    df = pd.read_json(uploaded)
                elif ext == "parquet":
                    df = pd.read_parquet(uploaded)
                else:
                    st.error("Unsupported file type.")
                    return

                for col in df.columns:
                    if df[col].dtype == object:
                        try:
                            df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
                        except Exception:
                            pass

                st.session_state.raw_df = df.copy()
                st.session_state.df = df.copy()
                st.session_state.filename = name
                st.success(f"✅ Loaded **{name}** successfully!")

            except Exception as e:
                st.error(f"Failed to read file: {e}")
                return

    if st.session_state.df is not None:
        df = st.session_state.df
        st.markdown("---")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Rows", f"{df.shape[0]:,}")
        m2.metric("Columns", df.shape[1])
        m3.metric("Missing Cells", f"{df.isnull().sum().sum():,}")
        m4.metric("Duplicates", f"{df.duplicated().sum():,}")
        m5.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

        st.markdown("### 👁️ Data Preview")
        n_rows = st.slider("Rows to preview", 5, min(200, df.shape[0]), 10)
        view = st.radio("View", ["Head", "Tail", "Random sample"], horizontal=True)
        if view == "Head":
            st.dataframe(df.head(n_rows), use_container_width=True)
        elif view == "Tail":
            st.dataframe(df.tail(n_rows), use_container_width=True)
        else:
            st.dataframe(df.sample(min(n_rows, len(df))), use_container_width=True)

        st.markdown("### 🔍 Column Info")
        col_info = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.values,
            "Non-Null": df.notnull().sum().values,
            "Null %": (df.isnull().mean() * 100).round(2).values,
            "Unique": df.nunique().values,
            "Sample": [str(df[c].dropna().iloc[0]) if df[c].dropna().shape[0] > 0 else "N/A" for c in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)

        st.markdown("### 📊 Quick Numeric Summary")
        num_df = df.select_dtypes(include="number")
        if not num_df.empty:
            st.dataframe(num_df.describe().T.round(3), use_container_width=True)
        else:
            st.info("No numeric columns found.")
    else:
        st.markdown("---")
        st.info("👆 Upload a file above to get started.")
