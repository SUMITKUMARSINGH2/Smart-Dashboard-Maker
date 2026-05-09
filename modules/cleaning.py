import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats


def cleaning_page():
    st.markdown("""
    <div class="main-header">
        <h1>🧹 Data Cleaning</h1>
        <p>Remove duplicates, handle missing values, fix outliers, and reshape your data.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
        return

    df = st.session_state.df

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{df.shape[0]:,}")
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing", f"{df.isnull().sum().sum():,}")
    c4.metric("Duplicates", f"{df.duplicated().sum():,}")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗑️ Duplicates", "🕳️ Missing Values", "📉 Outliers", "🏗️ Column Ops", "↩️ Reset"
    ])

    with tab1:
        n_dup = df.duplicated().sum()
        if n_dup == 0:
            st.success("✅ No duplicate rows found!")
        else:
            st.warning(f"Found **{n_dup}** duplicate rows ({n_dup/len(df)*100:.1f}%)")
            subset_cols = st.multiselect("Check duplicates based on columns (leave empty = all)", df.columns.tolist())
            keep = st.radio("Keep", ["first", "last", "none (drop all)"], horizontal=True)
            keep_val = False if keep == "none (drop all)" else keep
            if st.button("🗑️ Remove Duplicates"):
                sub = subset_cols if subset_cols else None
                st.session_state.df = df.drop_duplicates(subset=sub, keep=keep_val).reset_index(drop=True)
                st.success(f"Removed {n_dup} duplicate rows.")
                st.rerun()

    with tab2:
        miss = df.isnull().sum()
        miss_cols = miss[miss > 0].index.tolist()
        if not miss_cols:
            st.success("✅ No missing values found!")
        else:
            st.info(f"**{len(miss_cols)}** columns have missing values.")
            target_cols = st.multiselect("Columns to fix (leave empty = all with nulls)", miss_cols, default=miss_cols)
            if not target_cols:
                target_cols = miss_cols

            strategy = st.selectbox("Fill Strategy", [
                "Drop rows with nulls",
                "Fill with Mean",
                "Fill with Median",
                "Fill with Mode",
                "Fill with Constant",
                "Forward Fill",
                "Backward Fill",
                "Interpolate (linear)",
            ])

            const_val = ""
            if strategy == "Fill with Constant":
                const_val = st.text_input("Constant value", "0")

            if st.button("🔧 Apply Missing Value Fix"):
                temp = df.copy()
                num_cols = [c for c in target_cols if pd.api.types.is_numeric_dtype(temp[c])]
                other_cols = [c for c in target_cols if c not in num_cols]

                if strategy == "Drop rows with nulls":
                    temp = temp.dropna(subset=target_cols).reset_index(drop=True)
                elif strategy == "Fill with Mean":
                    for c in num_cols:
                        temp[c] = temp[c].fillna(temp[c].mean())
                    for c in other_cols:
                        temp[c] = temp[c].fillna(temp[c].mode().iloc[0] if not temp[c].mode().empty else "Unknown")
                elif strategy == "Fill with Median":
                    for c in num_cols:
                        temp[c] = temp[c].fillna(temp[c].median())
                    for c in other_cols:
                        temp[c] = temp[c].fillna(temp[c].mode().iloc[0] if not temp[c].mode().empty else "Unknown")
                elif strategy == "Fill with Mode":
                    for c in target_cols:
                        mode_val = temp[c].mode()
                        if not mode_val.empty:
                            temp[c] = temp[c].fillna(mode_val.iloc[0])
                elif strategy == "Fill with Constant":
                    for c in target_cols:
                        try:
                            v = float(const_val) if pd.api.types.is_numeric_dtype(temp[c]) else const_val
                        except Exception:
                            v = const_val
                        temp[c] = temp[c].fillna(v)
                elif strategy == "Forward Fill":
                    temp[target_cols] = temp[target_cols].ffill()
                elif strategy == "Backward Fill":
                    temp[target_cols] = temp[target_cols].bfill()
                elif strategy == "Interpolate (linear)":
                    for c in num_cols:
                        temp[c] = temp[c].interpolate(method="linear", limit_direction="both")
                    for c in other_cols:
                        temp[c] = temp[c].ffill().bfill()

                st.session_state.df = temp
                st.success("✅ Missing values handled successfully!")
                st.rerun()

    with tab3:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if not num_cols:
            st.info("No numeric columns for outlier analysis.")
        else:
            col = st.selectbox("Select column to analyze", num_cols)
            method = st.radio("Detection Method", ["IQR (Interquartile Range)", "Z-Score"], horizontal=True)
            action = st.radio("Action", ["Highlight Only", "Remove Outlier Rows", "Cap (Winsorize)"], horizontal=True)

            s = df[col].dropna()
            if method == "IQR (Interquartile Range)":
                Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
                IQR = Q3 - Q1
                factor = st.slider("IQR factor", 1.0, 3.0, 1.5, 0.1)
                low, high = Q1 - factor * IQR, Q3 + factor * IQR
                mask = (df[col] < low) | (df[col] > high)
            else:
                threshold = st.slider("Z-Score threshold", 1.5, 4.0, 3.0, 0.1)
                z = np.abs(stats.zscore(s))
                mask = pd.Series(False, index=df.index)
                mask.iloc[s.index] = z > threshold
                low, high = s.mean() - threshold * s.std(), s.mean() + threshold * s.std()

            n_out = mask.sum()
            c_a, c_b, c_c = st.columns(3)
            c_a.metric("Outliers Detected", n_out)
            c_b.metric("Lower Bound", f"{low:.3g}")
            c_c.metric("Upper Bound", f"{high:.3g}")

            if st.button("✂️ Apply Outlier Action") and n_out > 0:
                temp = df.copy()
                if action == "Remove Outlier Rows":
                    temp = temp[~mask].reset_index(drop=True)
                    st.success(f"Removed {n_out} rows.")
                elif action == "Cap (Winsorize)":
                    temp[col] = temp[col].clip(lower=low, upper=high)
                    st.success(f"Capped {n_out} values.")
                st.session_state.df = temp
                st.rerun()

    with tab4:
        st.markdown("#### ✏️ Rename Columns")
        rename_col = st.selectbox("Column to rename", df.columns.tolist(), key="rename_sel")
        new_name = st.text_input("New name", value=rename_col, key="rename_val")
        if st.button("Rename") and new_name and new_name != rename_col:
            st.session_state.df = df.rename(columns={rename_col: new_name})
            st.success(f"Renamed `{rename_col}` → `{new_name}`")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🗑️ Drop Columns")
        drop_cols = st.multiselect("Columns to drop", df.columns.tolist(), key="drop_sel")
        if st.button("Drop Selected Columns") and drop_cols:
            st.session_state.df = df.drop(columns=drop_cols)
            st.success(f"Dropped: {drop_cols}")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🔄 Change Column Data Type")
        dtype_col = st.selectbox("Column", df.columns.tolist(), key="dtype_sel")
        target_type = st.selectbox("Convert to", ["int64", "float64", "str", "datetime", "bool"], key="dtype_type")
        if st.button("Convert Type"):
            try:
                temp = df.copy()
                if target_type == "datetime":
                    temp[dtype_col] = pd.to_datetime(temp[dtype_col])
                elif target_type == "bool":
                    temp[dtype_col] = temp[dtype_col].astype(bool)
                else:
                    temp[dtype_col] = temp[dtype_col].astype(target_type)
                st.session_state.df = temp
                st.success(f"Converted `{dtype_col}` to {target_type}")
                st.rerun()
            except Exception as e:
                st.error(f"Conversion failed: {e}")

        st.markdown("---")
        st.markdown("#### 🔡 String Cleaning")
        str_cols = df.select_dtypes(include="object").columns.tolist()
        if str_cols:
            str_col = st.selectbox("String column", str_cols, key="str_col")
            str_op = st.selectbox("Operation", ["Strip whitespace", "Lowercase", "Uppercase", "Title Case", "Remove special chars"])
            if st.button("Apply String Op"):
                temp = df.copy()
                if str_op == "Strip whitespace":
                    temp[str_col] = temp[str_col].str.strip()
                elif str_op == "Lowercase":
                    temp[str_col] = temp[str_col].str.lower()
                elif str_op == "Uppercase":
                    temp[str_col] = temp[str_col].str.upper()
                elif str_op == "Title Case":
                    temp[str_col] = temp[str_col].str.title()
                elif str_op == "Remove special chars":
                    temp[str_col] = temp[str_col].str.replace(r"[^a-zA-Z0-9\s]", "", regex=True)
                st.session_state.df = temp
                st.success(f"Applied `{str_op}` to `{str_col}`")
                st.rerun()

    with tab5:
        st.warning("⚠️ This will reset the working data to the original uploaded file.")
        if st.button("↩️ Reset to Original Data", type="primary"):
            st.session_state.df = st.session_state.raw_df.copy()
            st.success("Data reset to original.")
            st.rerun()
        st.markdown("**Current vs Original:**")
        c1, c2 = st.columns(2)
        c1.metric("Current rows", f"{df.shape[0]:,}", delta=str(df.shape[0] - st.session_state.raw_df.shape[0]))
        c2.metric("Original rows", f"{st.session_state.raw_df.shape[0]:,}")
