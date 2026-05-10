import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import textwrap

_PLOTLY_DARK = dict(
    paper_bgcolor="#0A0F1E",
    plot_bgcolor="#0D1526",
    font=dict(color="#94A3B8", family="Space Grotesk"),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    title_font=dict(size=14, color="#E2E8F0"),
)

TEMPLATES = ["plotly_dark", "plotly_white", "plotly", "ggplot2", "seaborn", "simple_white"]
COLOR_SCALES = ["plasma", "viridis", "magma", "cividis", "turbo",
                "RdBu", "Blues", "Purples", "teal", "sunset"]
NEON = ["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#0EA5E9","#A855F7","#14B8A6"]

CHART_TYPES = [
    "Bar Chart", "Grouped Bar", "Stacked Bar",
    "Line Chart", "Area Chart",
    "Scatter Plot", "Bubble Chart",
    "Pie Chart", "Donut Chart",
    "Box Plot", "Violin Plot",
    "Histogram", "2D Density Heatmap",
    "Treemap", "Sunburst",
    "Funnel Chart", "Waterfall Chart",
    "Correlation Heatmap", "Strip Plot",
]


def _header(title, sub):
    st.markdown(f"""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// chart builder</div>
        <h2>{title}</h2>
        <div class='page-header-bar'></div>
        <p>{sub}</p>
    </div>""", unsafe_allow_html=True)


def _code_block(code: str):
    with st.expander("View / Copy Python Code", expanded=False):
        st.code(code.strip(), language="python")


def visualizations_page():
    _header("Chart Builder", "19 interactive chart types with live preview, HTML export, and Python code copy")

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    dt_cols  = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    all_cols = df.columns.tolist()

    chart_type = st.selectbox("Chart Type", CHART_TYPES, label_visibility="collapsed")
    st.markdown("---")
    ctrl, preview = st.columns([1, 2])

    with ctrl:
        st.markdown("<span style='color:#00D4FF;font-size:.65rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;font-family:\"JetBrains Mono\",monospace;'>Configuration</span>", unsafe_allow_html=True)
        template    = st.selectbox("Theme", TEMPLATES)
        title       = st.text_input("Title", chart_type)
        height      = st.slider("Height (px)", 300, 900, 520, 20)
        color_scale = st.selectbox("Color scale", COLOR_SCALES)

        fig  = None
        code = None

        if chart_type in ("Bar Chart", "Grouped Bar", "Stacked Bar"):
            x = st.selectbox("X axis", all_cols)
            y = st.selectbox("Y axis", num_cols or all_cols)
            color = st.selectbox("Color", ["None"] + cat_cols + num_cols)
            agg = st.selectbox("Aggregation", ["sum", "mean", "count", "median", "max", "min"])
            sort_by = st.radio("Sort", ["None", "Ascending", "Descending"], horizontal=True)
            color_val = color if color != "None" else None
            barmode = "group" if chart_type == "Grouped Bar" else ("stack" if chart_type == "Stacked Bar" else "relative")
            try:
                grp = [x] + ([color_val] if color_val else [])
                temp = df.groupby(grp)[y].agg(agg).reset_index()
                if sort_by == "Ascending":  temp = temp.sort_values(y)
                if sort_by == "Descending": temp = temp.sort_values(y, ascending=False)
                fig = px.bar(temp, x=x, y=y, color=color_val, barmode=barmode,
                             template=template, title=title,
                             color_continuous_scale=color_scale,
                             color_discrete_sequence=NEON, text_auto=True)
            except Exception as e: st.error(str(e))

        elif chart_type == "Line Chart":
            x = st.selectbox("X axis", dt_cols + all_cols)
            y = st.multiselect("Y axis (one or more)", num_cols, default=num_cols[:1])
            color = st.selectbox("Color", ["None"] + cat_cols)
            markers = st.checkbox("Markers", True)
            color_val = color if color != "None" else None
            if y:
                try:
                    if len(y) == 1:
                        fig = px.line(df.sort_values(x), x=x, y=y[0], color=color_val,
                                      markers=markers, template=template, title=title,
                                      color_discrete_sequence=NEON)
                    else:
                        melt = df[[x]+y].melt(id_vars=x, var_name="Series", value_name="Value")
                        fig = px.line(melt.sort_values(x), x=x, y="Value", color="Series",
                                      markers=markers, template=template, title=title,
                                      color_discrete_sequence=NEON)
                except Exception as e: st.error(str(e))

        elif chart_type == "Area Chart":
            x = st.selectbox("X axis", dt_cols + all_cols)
            y = st.multiselect("Y axis", num_cols, default=num_cols[:1])
            stack = st.checkbox("Stack areas", False)
            if y:
                try:
                    melt = df[[x]+y].melt(id_vars=x, var_name="Series", value_name="Value")
                    fig = px.area(melt.sort_values(x), x=x, y="Value", color="Series",
                                  template=template, title=title,
                                  groupnorm="fraction" if stack else None,
                                  color_discrete_sequence=NEON)
                except Exception as e: st.error(str(e))

        elif chart_type == "Scatter Plot":
            x = st.selectbox("X axis", num_cols or all_cols)
            y = st.selectbox("Y axis", ([c for c in num_cols if c != x] or num_cols))
            color = st.selectbox("Color by", ["None"] + cat_cols + num_cols)
            tl = st.checkbox("Trend line (OLS)", False)
            opacity = st.slider("Opacity", 0.1, 1.0, 0.7)
            color_val = color if color != "None" else None
            try:
                fig = px.scatter(df, x=x, y=y, color=color_val, opacity=opacity,
                                 trendline="ols" if tl else None,
                                 template=template, title=title,
                                 color_continuous_scale=color_scale,
                                 color_discrete_sequence=NEON)
            except Exception as e: st.error(str(e))

        elif chart_type == "Bubble Chart":
            x = st.selectbox("X axis", num_cols or all_cols)
            y = st.selectbox("Y axis", ([c for c in num_cols if c != x] or num_cols))
            size = st.selectbox("Bubble size", num_cols)
            color = st.selectbox("Color", ["None"] + cat_cols + num_cols)
            color_val = color if color != "None" else None
            try:
                fig = px.scatter(df, x=x, y=y, size=size, color=color_val,
                                 template=template, title=title,
                                 color_continuous_scale=color_scale,
                                 color_discrete_sequence=NEON,
                                 opacity=0.7, size_max=45)
            except Exception as e: st.error(str(e))

        elif chart_type in ("Pie Chart", "Donut Chart"):
            names  = st.selectbox("Labels", cat_cols + all_cols)
            values = st.selectbox("Values", num_cols or all_cols)
            top_n  = st.slider("Top N slices", 3, 20, 10)
            hole   = 0.45 if chart_type == "Donut Chart" else 0
            try:
                temp = df.groupby(names)[values].sum().nlargest(top_n).reset_index()
                fig = px.pie(temp, names=names, values=values, hole=hole,
                             template=template, title=title,
                             color_discrete_sequence=NEON)
            except Exception as e: st.error(str(e))

        elif chart_type == "Box Plot":
            y = st.selectbox("Value column", num_cols or all_cols)
            x = st.selectbox("Group by", ["None"] + cat_cols)
            color = st.selectbox("Color", ["None"] + cat_cols)
            pts = st.radio("Points", ["outliers", "all", "False"], horizontal=True)
            notched = st.checkbox("Notched", False)
            x_val = x if x != "None" else None
            color_val = color if color != "None" else None
            pts_val = False if pts == "False" else pts
            try:
                fig = px.box(df, x=x_val, y=y, color=color_val, points=pts_val,
                             notched=notched, template=template, title=title,
                             color_discrete_sequence=NEON)
            except Exception as e: st.error(str(e))

        elif chart_type == "Violin Plot":
            y = st.selectbox("Value column", num_cols or all_cols)
            x = st.selectbox("Group by", ["None"] + cat_cols)
            color = st.selectbox("Color", ["None"] + cat_cols)
            box = st.checkbox("Inner box", True)
            pts = st.checkbox("Show points", False)
            x_val = x if x != "None" else None
            color_val = color if color != "None" else None
            try:
                fig = px.violin(df, x=x_val, y=y, color=color_val, box=box,
                                points="all" if pts else False,
                                template=template, title=title,
                                color_discrete_sequence=NEON)
            except Exception as e: st.error(str(e))

        elif chart_type == "Histogram":
            col   = st.selectbox("Column", num_cols + cat_cols)
            bins  = st.slider("Bins", 5, 200, 30)
            color = st.selectbox("Color by", ["None"] + cat_cols)
            norm  = st.selectbox("Normalize", ["count", "percent", "density", "probability"])
            color_val = color if color != "None" else None
            try:
                fig = px.histogram(df, x=col, color=color_val, nbins=bins,
                                   histnorm=norm if norm != "count" else None,
                                   template=template, title=title,
                                   barmode="overlay", opacity=0.8,
                                   color_discrete_sequence=NEON)
            except Exception as e: st.error(str(e))

        elif chart_type == "2D Density Heatmap":
            if len(num_cols) >= 2:
                x = st.selectbox("X axis", num_cols)
                y = st.selectbox("Y axis", [c for c in num_cols if c != x])
                nbins = st.slider("Bins", 10, 100, 30)
                try:
                    fig = px.density_heatmap(df, x=x, y=y, nbinsx=nbins, nbinsy=nbins,
                                             color_continuous_scale=color_scale,
                                             template=template, title=title)
                except Exception as e: st.error(str(e))

        elif chart_type == "Treemap":
            path = st.multiselect("Hierarchy (ordered)", cat_cols,
                                  default=cat_cols[:min(2, len(cat_cols))])
            values = st.selectbox("Values", num_cols or all_cols)
            color  = st.selectbox("Color metric", ["None"] + num_cols)
            color_val = color if color != "None" else None
            if path:
                try:
                    fig = px.treemap(df, path=[px.Constant("All")] + path,
                                     values=values, color=color_val,
                                     color_continuous_scale=color_scale,
                                     template=template, title=title)
                except Exception as e: st.error(str(e))

        elif chart_type == "Sunburst":
            path   = st.multiselect("Hierarchy", cat_cols, default=cat_cols[:min(2, len(cat_cols))])
            values = st.selectbox("Values", num_cols or all_cols)
            if path:
                try:
                    fig = px.sunburst(df, path=path, values=values,
                                      template=template, title=title,
                                      color_discrete_sequence=NEON)
                except Exception as e: st.error(str(e))

        elif chart_type == "Funnel Chart":
            x = st.selectbox("Values (numeric)", num_cols or all_cols)
            y = st.selectbox("Stage labels", cat_cols + all_cols)
            try:
                temp = df.groupby(y)[x].sum().reset_index().sort_values(x, ascending=False)
                fig = px.funnel(temp, x=x, y=y, template=template, title=title,
                                color_discrete_sequence=NEON)
            except Exception as e: st.error(str(e))

        elif chart_type == "Waterfall Chart":
            x = st.selectbox("Category column", cat_cols + all_cols)
            y = st.selectbox("Value column", num_cols or all_cols)
            try:
                temp = df.groupby(x)[y].sum().reset_index()
                fig = go.Figure(go.Waterfall(
                    x=temp[x].astype(str).tolist(),
                    y=temp[y].tolist(),
                    connector={"line": {"color": "#1E293B"}},
                    increasing={"marker": {"color": "#10B981"}},
                    decreasing={"marker": {"color": "#FF006E"}},
                    totals={"marker": {"color": "#00D4FF"}},
                    name=title,
                ))
                fig.update_layout(title=title, template=template)
            except Exception as e: st.error(str(e))

        elif chart_type == "Correlation Heatmap":
            sel_cols = st.multiselect("Columns", num_cols, default=num_cols[:min(8, len(num_cols))])
            method = st.radio("Method", ["pearson", "spearman"], horizontal=True)
            if sel_cols and len(sel_cols) >= 2:
                try:
                    corr = df[sel_cols].corr(method=method)
                    fig = px.imshow(corr, text_auto=".2f",
                                    color_continuous_scale=["#FF006E","#0D1526","#00D4FF"],
                                    zmin=-1, zmax=1, template=template,
                                    title=f"{method.capitalize()} Correlation", aspect="auto")
                except Exception as e: st.error(str(e))

        elif chart_type == "Strip Plot":
            y = st.selectbox("Value column", num_cols or all_cols)
            x = st.selectbox("Group by", ["None"] + cat_cols)
            color = st.selectbox("Color", ["None"] + cat_cols)
            x_val = x if x != "None" else None
            color_val = color if color != "None" else None
            try:
                fig = px.strip(df, x=x_val, y=y, color=color_val,
                               template=template, title=title,
                               color_discrete_sequence=NEON)
            except Exception as e: st.error(str(e))

    with preview:
        if fig:
            fig.update_layout(height=height, **_PLOTLY_DARK)
            st.plotly_chart(fig, use_container_width=True)
            c1, c2 = st.columns(2)
            buf = io.StringIO()
            fig.write_html(buf)
            c1.download_button("Download Chart HTML", data=buf.getvalue().encode(),
                               file_name=f"{chart_type.lower().replace(' ','_')}.html",
                               mime="text/html", use_container_width=True)
            if code:
                with st.expander("Python Code", expanded=False):
                    st.code(code.strip(), language="python")
        else:
            st.markdown("""
            <div style='height:300px;display:flex;align-items:center;justify-content:center;
                        border:1px dashed rgba(0,212,255,0.15);border-radius:14px;
                        color:#2D3748;font-size:.85rem;'>
                Configure chart options on the left to preview
            </div>
            """, unsafe_allow_html=True)
