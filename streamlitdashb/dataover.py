import streamlit as st
import pandas as pd
from .styles import DARK_CSS, section_header, kpi_row_html, badge

def data_overview():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header("✦", "Data Overview & Cleaning", "Inspect and clean your dataset"), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data uploaded yet. Please upload a file first in File Upload.")
        return

    df = st.session_state["clean_data"]
    num_cols = df.select_dtypes(include=["int64","float64"]).shape[1]
    cat_cols = df.select_dtypes(include=["object","category"]).shape[1]
    missing = int(df.isnull().sum().sum())

    st.markdown(kpi_row_html([
        ("Rows", f"{df.shape[0]:,}"),
        ("Columns", df.shape[1]),
        ("Numeric", num_cols),
        ("Categorical", cat_cols),
        ("Missing", f"{missing:,}"),
        ("Duplicates", int(df.duplicated().sum())),
    ]), unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👀 Preview", "ℹ️ Info", "📊 Stats", "🧹 Cleaning Tools", "✅ Cleaned Data"])

    with tab1:
        rows_to_show = st.slider("Rows to preview", 50, min(2000, df.shape[0]), min(200, df.shape[0]), step=50)
        st.dataframe(df.head(rows_to_show), use_container_width=True, height=500, hide_index=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">Column Info</div>', unsafe_allow_html=True)
            info_rows = []
            for c in df.columns:
                dtype = str(df[c].dtype)
                null_pct = round(df[c].isna().sum() / len(df) * 100, 1)
                uniq = df[c].nunique()
                info_rows.append({"Column": c, "Type": dtype, "Nulls %": null_pct, "Unique": uniq})
            st.dataframe(pd.DataFrame(info_rows), use_container_width=True, hide_index=True)
        with col2:
            st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">Missing Values</div>', unsafe_allow_html=True)
            null_df = df.isnull().sum().reset_index()
            null_df.columns = ["Column", "Missing"]
            null_df["Missing %"] = (null_df["Missing"] / len(df) * 100).round(1)
            null_df = null_df[null_df["Missing"] > 0].sort_values("Missing", ascending=False)
            if len(null_df):
                st.dataframe(null_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No missing values in this dataset!")

    with tab3:
        st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">Descriptive Statistics</div>', unsafe_allow_html=True)
        num_df = df.select_dtypes(include=["int64","float64","int32","float32"])
        if len(num_df.columns):
            st.dataframe(num_df.describe().T.round(3), use_container_width=True)
        else:
            st.info("No numeric columns found.")

        cat_df = df.select_dtypes(include=["object","category"])
        if len(cat_df.columns):
            st.markdown('<div style="font-weight:600;color:#E2E8F0;margin:.75rem 0 .5rem;">Categorical Summary</div>', unsafe_allow_html=True)
            st.dataframe(cat_df.describe().T, use_container_width=True)

    with tab4:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">🔁 Duplicates</div>', unsafe_allow_html=True)
            n_dups = df.duplicated().sum()
            st.metric("Duplicate Rows", n_dups)
            dup_subset = st.multiselect("Consider only these columns (leave empty = all)", df.columns, key="dup_cols")
            if st.button("Remove Duplicate Rows", key="rm_dups"):
                before = len(df)
                df = df.drop_duplicates(subset=dup_subset if dup_subset else None)
                after = len(df)
                st.session_state["clean_data"] = df
                st.success(f"✅ Removed {before - after} duplicate rows")
                st.rerun()

            st.markdown("---")
            st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">✂️ Drop Column</div>', unsafe_allow_html=True)
            col_to_drop = st.selectbox("Select column to drop", ["— none —"] + list(df.columns), key="drop_col")
            if st.button("Drop Column", key="do_drop_col") and col_to_drop != "— none —":
                df = df.drop(columns=[col_to_drop])
                st.session_state["clean_data"] = df
                st.success(f"✅ Dropped column '{col_to_drop}'")
                st.rerun()

            st.markdown("---")
            st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">🔤 Rename Column</div>', unsafe_allow_html=True)
            old_name = st.selectbox("Column to rename", ["— none —"] + list(df.columns), key="rename_old")
            new_name = st.text_input("New name", key="rename_new")
            if st.button("Rename Column") and old_name != "— none —" and new_name:
                df = df.rename(columns={old_name: new_name})
                st.session_state["clean_data"] = df
                st.success(f"✅ Renamed '{old_name}' → '{new_name}'")
                st.rerun()

        with c2:
            st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">🕳️ Handle Missing Values</div>', unsafe_allow_html=True)
            fill_cols = st.multiselect("Columns to fill (empty = all numeric)", df.columns, key="fill_cols")
            fill_method = st.selectbox("Fill method", ["mean", "median", "mode", "zero", "ffill", "bfill", "custom"])
            fill_val = ""
            if fill_method == "custom":
                fill_val = st.text_input("Custom fill value")

            if st.button("Fill Missing Values", key="fill_btn"):
                cols = fill_cols if fill_cols else df.select_dtypes(include=["number"]).columns.tolist()
                for c in cols:
                    if fill_method == "mean" and pd.api.types.is_numeric_dtype(df[c]):
                        df[c] = df[c].fillna(df[c].mean())
                    elif fill_method == "median" and pd.api.types.is_numeric_dtype(df[c]):
                        df[c] = df[c].fillna(df[c].median())
                    elif fill_method == "mode":
                        mv = df[c].mode()
                        if len(mv): df[c] = df[c].fillna(mv[0])
                    elif fill_method == "zero":
                        df[c] = df[c].fillna(0)
                    elif fill_method == "ffill":
                        df[c] = df[c].ffill()
                    elif fill_method == "bfill":
                        df[c] = df[c].bfill()
                    elif fill_method == "custom" and fill_val:
                        df[c] = df[c].fillna(fill_val)
                st.session_state["clean_data"] = df
                st.success(f"✅ Filled nulls in {len(cols)} column(s) using {fill_method}")
                st.rerun()

            st.markdown("---")
            st.markdown('<div style="font-weight:600;color:#E2E8F0;margin-bottom:.75rem;">🔁 Cast Column Type</div>', unsafe_allow_html=True)
            cast_col = st.selectbox("Column", ["— none —"] + list(df.columns), key="cast_col")
            cast_type = st.selectbox("Target type", ["numeric", "string", "datetime", "bool"])
            if st.button("Cast Type") and cast_col != "— none —":
                try:
                    if cast_type == "numeric":
                        df[cast_col] = pd.to_numeric(df[cast_col], errors="coerce")
                    elif cast_type == "string":
                        df[cast_col] = df[cast_col].astype(str)
                    elif cast_type == "datetime":
                        df[cast_col] = pd.to_datetime(df[cast_col], errors="coerce")
                    elif cast_type == "bool":
                        df[cast_col] = df[cast_col].astype(bool)
                    st.session_state["clean_data"] = df
                    st.success(f"✅ Cast '{cast_col}' to {cast_type}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Cast failed: {e}")

            st.markdown("---")
            if st.button("↺ Reset to Original Data", key="reset_data"):
                if "raw_data" in st.session_state:
                    st.session_state["clean_data"] = st.session_state["raw_data"].copy()
                    st.info("🔄 Data reset to original uploaded file")
                    st.rerun()

    with tab5:
        st.dataframe(st.session_state["clean_data"], use_container_width=True, height=500, hide_index=True)
        st.download_button(
            "⬇️ Download Cleaned Data (CSV)",
            st.session_state["clean_data"].to_csv(index=False).encode("utf-8"),
            file_name="cleaned_data.csv",
            mime="text/csv",
        )
