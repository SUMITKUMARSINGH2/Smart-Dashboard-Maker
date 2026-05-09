import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats as sc_stats


def _header(title, sub):
    st.markdown(f"<div class='page-header'><h2>{title}</h2><p>{sub}</p></div>",
                unsafe_allow_html=True)


def cleaning_page():
    _header("Data Cleaning", "Remove duplicates, handle missing values, fix outliers, and reshape columns")

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{df.shape[0]:,}")
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing cells", f"{df.isnull().sum().sum():,}")
    c4.metric("Duplicate rows", f"{df.duplicated().sum():,}")

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Duplicates", "Missing Values", "Outliers", "Column Ops", "Reset"]
    )

    with tab1:
        n_dup = df.duplicated().sum()
        if n_dup == 0:
            st.success("No duplicate rows found.")
        else:
            st.warning(f"**{n_dup}** duplicate rows ({n_dup/len(df)*100:.1f}% of data)")
            subset_cols = st.multiselect("Check duplicates on columns (empty = all)", df.columns.tolist())
            keep = st.radio("Which duplicate to keep", ["first", "last", "Drop all"], horizontal=True)
            keep_val = False if keep == "Drop all" else keep
            if st.button("Remove Duplicates"):
                sub = subset_cols if subset_cols else None
                st.session_state.df = df.drop_duplicates(subset=sub, keep=keep_val).reset_index(drop=True)
                st.success(f"Removed {n_dup} rows.")
                st.rerun()

    with tab2:
        miss = df.isnull().sum()
        miss_cols = miss[miss > 0].index.tolist()
        if not miss_cols:
            st.success("No missing values found.")
        else:
            st.info(f"**{len(miss_cols)}** columns contain missing values.")
            target_cols = st.multiselect("Columns to fix (empty = all with nulls)", miss_cols, default=miss_cols)
            if not target_cols:
                target_cols = miss_cols

            strategy = st.selectbox("Fill Strategy", [
                "Drop rows with nulls", "Fill with Mean", "Fill with Median",
                "Fill with Mode", "Fill with Constant",
                "Forward Fill", "Backward Fill", "Interpolate (linear)",
            ])
            const_val = ""
            if strategy == "Fill with Constant":
                const_val = st.text_input("Constant value", "0")

            if st.button("Apply Fix"):
                temp = df.copy()
                num_c = [c for c in target_cols if pd.api.types.is_numeric_dtype(temp[c])]
                oth_c = [c for c in target_cols if c not in num_c]

                if strategy == "Drop rows with nulls":
                    temp = temp.dropna(subset=target_cols).reset_index(drop=True)
                elif strategy == "Fill with Mean":
                    for c in num_c:
                        temp[c] = temp[c].fillna(temp[c].mean())
                    for c in oth_c:
                        m = temp[c].mode()
                        temp[c] = temp[c].fillna(m.iloc[0] if not m.empty else "Unknown")
                elif strategy == "Fill with Median":
                    for c in num_c:
                        temp[c] = temp[c].fillna(temp[c].median())
                    for c in oth_c:
                        m = temp[c].mode()
                        temp[c] = temp[c].fillna(m.iloc[0] if not m.empty else "Unknown")
                elif strategy == "Fill with Mode":
                    for c in target_cols:
                        m = temp[c].mode()
                        if not m.empty:
                            temp[c] = temp[c].fillna(m.iloc[0])
                elif strategy == "Fill with Constant":
                    for c in target_cols:
                        try:
                            v = float(const_val) if pd.api.types.is_numeric_dtype(temp[c]) else const_val
                        except ValueError:
                            v = const_val
                        temp[c] = temp[c].fillna(v)
                elif strategy == "Forward Fill":
                    temp[target_cols] = temp[target_cols].ffill()
                elif strategy == "Backward Fill":
                    temp[target_cols] = temp[target_cols].bfill()
                elif strategy == "Interpolate (linear)":
                    for c in num_c:
                        temp[c] = temp[c].interpolate(method="linear", limit_direction="both")
                    for c in oth_c:
                        temp[c] = temp[c].ffill().bfill()

                st.session_state.df = temp
                st.success("Missing values handled.")
                st.rerun()

    with tab3:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if not num_cols:
            st.info("No numeric columns available.")
        else:
            col = st.selectbox("Column", num_cols)
            method = st.radio("Detection method", ["IQR", "Z-Score"], horizontal=True)
            action = st.radio("Action on outliers",
                              ["Highlight Only", "Remove Rows", "Cap (Winsorize)"], horizontal=True)

            s = df[col].dropna()
            if method == "IQR":
                factor = st.slider("IQR multiplier", 1.0, 3.0, 1.5, 0.1)
                Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
                low, high = Q1 - factor * (Q3 - Q1), Q3 + factor * (Q3 - Q1)
                mask = (df[col] < low) | (df[col] > high)
            else:
                threshold = st.slider("Z-Score threshold", 1.5, 4.0, 3.0, 0.1)
                z = np.abs(sc_stats.zscore(s))
                mask = pd.Series(False, index=df.index)
                mask.loc[s.index[:len(z)]] = z > threshold
                low = float(s.mean() - threshold * s.std())
                high = float(s.mean() + threshold * s.std())

            n_out = int(mask.sum())
            ca, cb, cc = st.columns(3)
            ca.metric("Outliers found", n_out)
            cb.metric("Lower bound", f"{low:.3g}")
            cc.metric("Upper bound", f"{high:.3g}")

            if action != "Highlight Only" and st.button("Apply to Dataset") and n_out > 0:
                temp = df.copy()
                if action == "Remove Rows":
                    temp = temp[~mask].reset_index(drop=True)
                    st.success(f"Removed {n_out} rows.")
                else:
                    temp[col] = temp[col].clip(lower=low, upper=high)
                    st.success(f"Capped {n_out} values.")
                st.session_state.df = temp
                st.rerun()

    with tab4:
        st.markdown("**Rename Column**")
        rc = st.selectbox("Column to rename", df.columns.tolist(), key="rc")
        rn = st.text_input("New name", value=rc, key="rn")
        if st.button("Rename") and rn != rc:
            st.session_state.df = df.rename(columns={rc: rn})
            st.success(f"Renamed `{rc}` → `{rn}`")
            st.rerun()

        st.markdown("---")
        st.markdown("**Drop Columns**")
        drop_cols = st.multiselect("Select columns to remove", df.columns.tolist())
        if st.button("Drop Selected") and drop_cols:
            st.session_state.df = df.drop(columns=drop_cols)
            st.success(f"Dropped: {drop_cols}")
            st.rerun()

        st.markdown("---")
        st.markdown("**Change Data Type**")
        dc = st.selectbox("Column", df.columns.tolist(), key="dc")
        dt = st.selectbox("Convert to", ["int64", "float64", "str", "datetime", "bool"])
        if st.button("Convert"):
            try:
                temp = df.copy()
                if dt == "datetime":
                    temp[dc] = pd.to_datetime(temp[dc])
                elif dt == "bool":
                    temp[dc] = temp[dc].astype(bool)
                else:
                    temp[dc] = temp[dc].astype(dt)
                st.session_state.df = temp
                st.success(f"`{dc}` converted to {dt}")
                st.rerun()
            except Exception as e:
                st.error(f"Conversion failed: {e}")

        st.markdown("---")
        st.markdown("**String Operations**")
        str_cols = df.select_dtypes(include="object").columns.tolist()
        if str_cols:
            sc_ = st.selectbox("String column", str_cols)
            sop = st.selectbox("Operation",
                               ["Strip whitespace", "Lowercase", "Uppercase",
                                "Title Case", "Remove special chars"])
            if st.button("Apply"):
                temp = df.copy()
                if sop == "Strip whitespace":
                    temp[sc_] = temp[sc_].str.strip()
                elif sop == "Lowercase":
                    temp[sc_] = temp[sc_].str.lower()
                elif sop == "Uppercase":
                    temp[sc_] = temp[sc_].str.upper()
                elif sop == "Title Case":
                    temp[sc_] = temp[sc_].str.title()
                else:
                    temp[sc_] = temp[sc_].str.replace(r"[^a-zA-Z0-9\s]", "", regex=True)
                st.session_state.df = temp
                st.success(f"Applied `{sop}` to `{sc_}`")
                st.rerun()

    with tab5:
        st.warning("This will undo ALL cleaning operations and restore the original uploaded data.")
        r1, r2 = st.columns(2)
        r1.metric("Current rows", f"{df.shape[0]:,}",
                  delta=str(df.shape[0] - st.session_state.raw_df.shape[0]))
        r2.metric("Original rows", f"{st.session_state.raw_df.shape[0]:,}")
        if st.button("Reset to Original", type="primary"):
            st.session_state.df = st.session_state.raw_df.copy()
            st.success("Data reset to original.")
            st.rerun()
