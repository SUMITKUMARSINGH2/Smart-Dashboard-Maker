import streamlit as st
import pandas as pd
import plotly.express as px
import io


def export_page():
    st.markdown("""
    <div class="main-header">
        <h1>📤 Export</h1>
        <p>Download your cleaned data, charts, and full HTML data reports.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
        return

    df = st.session_state.df
    raw = st.session_state.raw_df
    filename = st.session_state.filename or "data"
    base = filename.rsplit(".", 1)[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Current Rows", f"{df.shape[0]:,}")
    m2.metric("Original Rows", f"{raw.shape[0]:,}")
    diff = df.shape[0] - raw.shape[0]
    m3.metric("Rows Changed", str(diff), delta=str(diff))

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["💾 Data Export", "📊 Chart Export", "📄 Full Report"])

    with tab1:
        st.markdown("### 💾 Export Cleaned Data")

        fmt = st.radio("Format", ["CSV", "Excel (.xlsx)", "JSON"], horizontal=True)
        include_index = st.checkbox("Include row index", False)
        sep = ","
        if fmt == "CSV":
            sep = st.selectbox("Separator", [",", ";", "\t", "|"])

        if fmt == "CSV":
            csv_buf = io.BytesIO()
            df.to_csv(csv_buf, index=include_index, sep=sep)
            csv_buf.seek(0)
            st.download_button("📥 Download CSV", data=csv_buf,
                               file_name=f"{base}_cleaned.csv", mime="text/csv")

        elif fmt == "Excel (.xlsx)":
            xl_buf = io.BytesIO()
            with pd.ExcelWriter(xl_buf, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=include_index, sheet_name="Cleaned Data")
                if st.checkbox("Include original data on second sheet", True):
                    raw.to_excel(writer, index=include_index, sheet_name="Original Data")
            xl_buf.seek(0)
            st.download_button("📥 Download Excel", data=xl_buf,
                               file_name=f"{base}_cleaned.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        elif fmt == "JSON":
            orient = st.selectbox("JSON orientation", ["records", "split", "index", "columns"])
            json_str = df.to_json(orient=orient, indent=2)
            st.download_button("📥 Download JSON", data=json_str.encode(),
                               file_name=f"{base}_cleaned.json", mime="application/json")

        st.markdown("---")
        st.markdown("#### Preview of export")
        st.dataframe(df.head(10), use_container_width=True)

    with tab2:
        st.markdown("### 📊 Quick Chart Export")
        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Pie", "Box", "Histogram"])
        template = st.selectbox("Theme", ["plotly_white", "plotly", "plotly_dark", "ggplot2"])

        fig = None
        if chart_type == "Bar" and cat_cols and num_cols:
            x = st.selectbox("X", cat_cols)
            y = st.selectbox("Y", num_cols)
            fig = px.bar(df.groupby(x)[y].mean().reset_index(), x=x, y=y, template=template, text_auto=True)
        elif chart_type == "Line" and num_cols:
            x = st.selectbox("X", df.columns.tolist())
            y = st.selectbox("Y", num_cols)
            fig = px.line(df.sort_values(x), x=x, y=y, template=template)
        elif chart_type == "Scatter" and len(num_cols) >= 2:
            x = st.selectbox("X", num_cols)
            y = st.selectbox("Y", [c for c in num_cols if c != x])
            fig = px.scatter(df, x=x, y=y, template=template, opacity=0.7)
        elif chart_type == "Pie" and cat_cols and num_cols:
            names = st.selectbox("Labels", cat_cols)
            values = st.selectbox("Values", num_cols)
            fig = px.pie(df.groupby(names)[values].sum().reset_index(), names=names, values=values, template=template)
        elif chart_type == "Box" and num_cols:
            y = st.selectbox("Column", num_cols)
            fig = px.box(df, y=y, template=template)
        elif chart_type == "Histogram" and num_cols:
            col = st.selectbox("Column", num_cols)
            fig = px.histogram(df, x=col, nbins=40, template=template)

        if fig:
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)
            buf = io.StringIO()
            fig.write_html(buf)
            st.download_button("📥 Download Chart HTML", data=buf.getvalue().encode(),
                               file_name=f"{base}_chart.html", mime="text/html")

    with tab3:
        st.markdown("### 📄 Full HTML Data Report")
        st.info("Generates a comprehensive HTML report with statistics, missing value analysis, and charts.")

        if st.button("🔨 Generate Report", type="primary"):
            with st.spinner("Building report..."):
                num_cols = df.select_dtypes(include="number").columns.tolist()
                cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                miss = df.isnull().sum()

                parts = ["""
<html><head>
<title>Data Report</title>
<style>
  body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 20px; color: #333; }
  h1 { background: linear-gradient(135deg,#667eea,#764ba2); color: white; padding: 20px 30px; border-radius: 10px; }
  h2 { color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 6px; }
  .card { background: white; border-radius: 10px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  .kpi-row { display: flex; gap: 12px; flex-wrap: wrap; }
  .kpi { background: #667eea; color: white; border-radius: 8px; padding: 14px 20px; min-width: 120px; }
  .kpi h3 { margin: 0; font-size: 1.6rem; }
  .kpi p { margin: 0; opacity: 0.85; font-size: 0.8rem; }
  table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
  th { background: #667eea; color: white; padding: 8px 10px; text-align: left; }
  td { padding: 7px 10px; border-bottom: 1px solid #eee; }
  tr:nth-child(even) { background: #f9f9f9; }
</style>
</head><body>
"""]
                parts.append(f"<h1>📊 Data Report: {filename}</h1>")
                parts.append('<div class="card"><div class="kpi-row">')
                kpis = [("Rows", f"{df.shape[0]:,}"), ("Columns", df.shape[1]),
                        ("Missing %", f"{df.isnull().mean().mean()*100:.1f}%"),
                        ("Duplicates", df.duplicated().sum()),
                        ("Numeric cols", len(num_cols)), ("Categorical cols", len(cat_cols))]
                for label, val in kpis:
                    parts.append(f'<div class="kpi"><h3>{val}</h3><p>{label}</p></div>')
                parts.append("</div></div>")

                if num_cols:
                    desc = df[num_cols].describe().T
                    parts.append('<div class="card"><h2>📐 Numeric Statistics</h2>')
                    parts.append(desc.round(3).to_html())
                    parts.append("</div>")

                miss_pos = miss[miss > 0]
                if not miss_pos.empty:
                    parts.append('<div class="card"><h2>🕳️ Missing Values</h2>')
                    miss_html = pd.DataFrame({"Count": miss_pos, "Pct": (miss_pos/len(df)*100).round(2)}).to_html()
                    parts.append(miss_html)
                    parts.append("</div>")

                if num_cols:
                    corr = df[num_cols].corr()
                    fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                                         zmin=-1, zmax=1, title="Correlation Matrix")
                    parts.append('<div class="card"><h2>🔥 Correlation Matrix</h2>')
                    parts.append(fig_corr.to_html(full_html=False, include_plotlyjs="cdn"))
                    parts.append("</div>")

                    for nc in num_cols[:4]:
                        fig_h = px.histogram(df, x=nc, nbins=40, title=f"Distribution: {nc}",
                                             color_discrete_sequence=["#667eea"])
                        parts.append(f'<div class="card"><h2>📊 {nc}</h2>')
                        parts.append(fig_h.to_html(full_html=False, include_plotlyjs=False))
                        parts.append("</div>")

                parts.append("</body></html>")
                full_report = "\n".join(parts)
                st.success("Report generated!")
                st.download_button("📥 Download Full Report HTML", data=full_report.encode(),
                                   file_name=f"{base}_report.html", mime="text/html")
