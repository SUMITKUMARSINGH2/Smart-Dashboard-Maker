import streamlit as st
import pandas as pd

def data_overview():
    st.header("📊 Data Overview & Cleaning", divider="rainbow")

    # Check if data is uploaded
    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data uploaded yet. Please upload a file first in the **Files Upload** page.")
        return

    df = st.session_state["clean_data"]

    # Tabs
    tabs = st.tabs(["👀 Data Preview", "ℹ️ Dataset Info", "📊 Data Description", "🧹 Cleaning Tools", "🧾 Cleaned Data Preview"])

    # Data Preview Tab
    with tabs[0]:
        st.dataframe(df,hide_index=True, width="stretch", on_select="ignore", use_container_width=True, height=600)

    # Dataset Info Tab
    with tabs[1]:
        st.write(f"**Rows:** {df.shape[0]}, **Columns:** {df.shape[1]}")
        st.write("**Columns Names:**", list(df.columns))
        st.write("**Data Types:**")
        st.dataframe(pd.DataFrame(df.dtypes, columns=["Type"]))
        st.write("**Sum of Null Values per Column:**")
        st.dataframe(df.isnull().sum())
        st.write("**Number of Duplicate Rows:**", df.duplicated().sum())

    # Data Description Tab
    with tabs[2]:
        st.dataframe(df.describe(),hide_index=True, width="stretch", on_select="ignore")

    # Cleaning Tools Tab
    with tabs[3]:
        st.subheader("Duplicate Rows")
        st.write(f"Total duplicate rows in dataset: {df.duplicated().sum()}")
        remove_dupes_cols = st.multiselect("Select columns to consider for duplicates (leave empty for all):", df.columns)
        if st.button("Remove Duplicate Rows"):
            before = df.shape[0]
            if remove_dupes_cols:
                df = df.drop_duplicates(subset=remove_dupes_cols)
            else:
                df = df.drop_duplicates()
            after = df.shape[0]
            st.session_state["clean_data"] = df
            st.success(f"✅ Removed {before - after} duplicate rows")

        st.markdown("---")
        st.subheader("Null Values")
        st.write(f"Total null values in dataset: {df.isnull().sum().sum()}")

        fill_columns = st.multiselect("Select columns to fill null values:", df.columns)
        fill_value = st.text_input("Enter value to fill nulls with:")
        fill_all = st.checkbox("Apply fill to all columns with nulls")
        if st.button("Fill Nulls"):
            if fill_value:
                if fill_all:
                    df = df.fillna(fill_value)
                elif fill_columns:
                    df[fill_columns] = df[fill_columns].fillna(fill_value)
                st.session_state["clean_data"] = df
                st.success(f"✅ Nulls replaced with '{fill_value}'")

        drop_null_cols = st.multiselect("Select columns to drop rows if null present:", df.columns)
        if st.button("Drop Null Rows"):
            before = df.shape[0]
            if drop_null_cols:
                df = df.dropna(subset=drop_null_cols)
            else:
                df = df.dropna()
            after = df.shape[0]
            st.session_state["clean_data"] = df
            st.success(f"✅ Dropped {before - after} rows with null values")

        if st.button("Reset to Original Data"):
            df = st.session_state["raw_data"].copy()
            st.session_state["clean_data"] = df
            st.info("🔄 Data reset to original uploaded file")

    # Cleaned Data Preview Tab
    with tabs[4]:
        st.dataframe(st.session_state["clean_data"],hide_index=True, width="stretch", on_select="ignore", use_container_width=True, height=600)

    # Download cleaned data
    st.download_button(
        label="💾 Download Cleaned Data as CSV",
        data=st.session_state["clean_data"].to_csv(index=False).encode("utf-8"),
        file_name="cleaned_data.csv",
        mime="text/csv",
    )
