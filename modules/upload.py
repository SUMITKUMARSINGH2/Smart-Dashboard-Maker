import streamlit as st
import pandas as pd
import io


@st.cache_data(show_spinner=False)
def _parse_file(data: bytes, name: str) -> pd.DataFrame:
    ext = name.rsplit(".", 1)[-1].lower()
    buf = io.BytesIO(data)
    if ext == "csv":
        raw = data[:4096].decode("utf-8", errors="replace")
        sep = ";" if raw.count(";") > raw.count(",") else ","
        df = pd.read_csv(buf, sep=sep, low_memory=False)
    elif ext in ("xlsx", "xls"):
        xl = pd.ExcelFile(buf)
        sheet = xl.sheet_names[0]
        df = pd.read_excel(buf, sheet_name=sheet)
    elif ext == "json":
        df = pd.read_json(buf)
    elif ext == "parquet":
        df = pd.read_parquet(buf)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    for col in df.columns:
        if df[col].dtype == object:
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notnull().mean() > 0.7:
                    df[col] = parsed
            except Exception:
                pass
    return df


def _header(title, sub):
    st.markdown(f"""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// data ingestion</div>
        <h2>{title}</h2>
        <div class='page-header-bar'></div>
        <p>{sub}</p>
    </div>""", unsafe_allow_html=True)


def upload_page():
    _header("Upload Data", "Load your dataset — CSV, Excel, JSON or Parquet")

    uploaded = st.file_uploader(
        "Drop your file here or click to browse",
        type=["csv", "xlsx", "xls", "json", "parquet"],
    )

    st.markdown("""
    <div style='background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.15);
                border-radius:10px;padding:.75rem 1rem;margin:.5rem 0 1rem;
                font-size:.81rem;color:#64748B;font-family:"JetBrains Mono",monospace;'>
        <span style='color:#00D4FF;font-weight:600;'>Supported:</span>
        &nbsp;CSV &nbsp;·&nbsp; Excel .xlsx/.xls &nbsp;·&nbsp;
        JSON &nbsp;·&nbsp; Parquet
    </div>
    """, unsafe_allow_html=True)

    if uploaded:
        with st.spinner("Parsing file…"):
            try:
                file_bytes = uploaded.read()
                df = _parse_file(file_bytes, uploaded.name)
                st.session_state.raw_df = df.copy()
                st.session_state.df = df.copy()
                st.session_state.filename = uploaded.name
                st.success(f"Loaded **{uploaded.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")
            except Exception as e:
                st.error(f"Failed to read file: {e}")
                return

    if st.session_state.df is None:
        st.markdown("""
        <div style='text-align:center;padding:3.5rem 1rem;color:#2D3748;
                    border:1px dashed rgba(255,255,255,0.05);border-radius:16px;
                    background:rgba(255,255,255,0.01);margin-top:1rem;'>
            <div style='font-size:2.5rem;margin-bottom:.8rem;opacity:.4;'>⬆</div>
            <div style='font-size:.95rem;font-weight:600;color:#4A5568;'>Upload a file above to get started</div>
            <div style='font-size:.82rem;margin-top:.4rem;color:#2D3748;'>
                Your data stays in your session — it is never saved or shared.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    df = st.session_state.df

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Rows", f"{df.shape[0]:,}")
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing", f"{df.isnull().sum().sum():,}")
    c4.metric("Duplicates", f"{df.duplicated().sum():,}")
    mem = df.memory_usage(deep=True).sum()
    c5.metric("Memory", f"{mem/1024:.1f} KB" if mem < 1024**2 else f"{mem/1024/1024:.1f} MB")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span style='color:#A0AEC0;font-weight:600;font-size:.83rem;'>Data Preview</span>", unsafe_allow_html=True)
    ca, cb = st.columns([3, 1])
    with ca:
        n_rows = st.slider("Rows to show", 5, min(200, df.shape[0]), 10)
    with cb:
        view = st.radio("From", ["Head", "Tail", "Random"], horizontal=True)

    if view == "Head":
        disp = df.head(n_rows)
    elif view == "Tail":
        disp = df.tail(n_rows)
    else:
        disp = df.sample(min(n_rows, len(df)))
    st.dataframe(disp, use_container_width=True, height=300)

    st.markdown("<br><span style='color:#A0AEC0;font-weight:600;font-size:.83rem;'>Column Info</span>", unsafe_allow_html=True)
    col_info = pd.DataFrame({
        "Column": df.columns,
        "Dtype": df.dtypes.values,
        "Non-Null": df.notnull().sum().values,
        "Null %": (df.isnull().mean() * 100).round(2).values,
        "Unique": df.nunique().values,
        "Sample": [str(df[c].dropna().iloc[0]) if df[c].dropna().shape[0] > 0 else "—"
                   for c in df.columns],
    })
    st.dataframe(col_info, use_container_width=True)

    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        st.markdown("<br><span style='color:#A0AEC0;font-weight:600;font-size:.83rem;'>Numeric Summary</span>", unsafe_allow_html=True)
        st.dataframe(num_df.describe().T.round(4), use_container_width=True)
