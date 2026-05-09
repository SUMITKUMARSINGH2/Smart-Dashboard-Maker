import streamlit as st
import pandas as pd
import io


def _header(title, sub):
    st.markdown(f"<div class='page-header'><h2>{title}</h2><p>{sub}</p></div>", unsafe_allow_html=True)


def upload_page():
    _header("Upload Data", "Load your dataset — CSV, Excel, JSON or Parquet")

    upload_col, info_col = st.columns([3, 1])
    with upload_col:
        uploaded = st.file_uploader(
            "Drop your file here or click to browse",
            type=["csv", "xlsx", "xls", "json", "parquet"],
        )
    with info_col:
        st.markdown("""
        <div style='background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:1rem;margin-top:1.6rem;font-size:0.82rem;color:#475569;'>
            <b style='color:#0F172A;'>Supported formats</b><br><br>
            📄 CSV (comma / semicolon)<br>
            📊 Excel .xlsx / .xls<br>
            🗂️ JSON (records / split)<br>
            🗃️ Parquet
        </div>
        """, unsafe_allow_html=True)

    if uploaded:
        with st.spinner("Parsing file…"):
            try:
                ext = uploaded.name.rsplit(".", 1)[-1].lower()
                if ext == "csv":
                    raw = uploaded.read(4096).decode("utf-8", errors="replace")
                    uploaded.seek(0)
                    sep = ";" if raw.count(";") > raw.count(",") else ","
                    df = pd.read_csv(uploaded, sep=sep, low_memory=False)
                elif ext in ("xlsx", "xls"):
                    xl = pd.ExcelFile(uploaded)
                    sheet = xl.sheet_names[0] if len(xl.sheet_names) == 1 else st.selectbox("Sheet", xl.sheet_names)
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
                st.session_state.filename = uploaded.name
                st.success(f"Loaded **{uploaded.name}** successfully.")
            except Exception as e:
                st.error(f"Failed to read file: {e}")
                return

    if st.session_state.df is None:
        st.markdown("<div style='text-align:center;padding:3rem;color:#94A3B8;'>Upload a file above to get started.</div>", unsafe_allow_html=True)
        return

    df = st.session_state.df
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Rows", f"{df.shape[0]:,}")
    m2.metric("Columns", df.shape[1])
    m3.metric("Missing cells", f"{df.isnull().sum().sum():,}")
    m4.metric("Duplicates", f"{df.duplicated().sum():,}")
    mem = df.memory_usage(deep=True).sum()
    m5.metric("Memory", f"{mem/1024:.1f} KB" if mem < 1024**2 else f"{mem/1024/1024:.1f} MB")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Data Preview**")

    c1, c2 = st.columns([3, 1])
    with c1:
        n_rows = st.slider("Rows to show", 5, min(200, df.shape[0]), 10)
    with c2:
        view = st.radio("From", ["Head", "Tail", "Random"], horizontal=True)

    disp = df.head(n_rows) if view == "Head" else df.tail(n_rows) if view == "Tail" else df.sample(min(n_rows, len(df)))
    st.dataframe(disp, use_container_width=True, height=320)

    st.markdown("<br>**Column Info**", unsafe_allow_html=True)
    col_info = pd.DataFrame({
        "Column": df.columns,
        "Dtype": df.dtypes.values,
        "Non-Null": df.notnull().sum().values,
        "Null %": (df.isnull().mean() * 100).round(2).values,
        "Unique": df.nunique().values,
        "Sample": [str(df[c].dropna().iloc[0]) if df[c].dropna().shape[0] > 0 else "—" for c in df.columns],
    })
    st.dataframe(col_info, use_container_width=True)

    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        st.markdown("<br>**Numeric Summary**", unsafe_allow_html=True)
        st.dataframe(num_df.describe().T.round(4), use_container_width=True)
