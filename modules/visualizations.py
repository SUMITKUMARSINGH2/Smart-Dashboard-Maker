import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io


TEMPLATES = ["plotly_white", "plotly", "plotly_dark", "ggplot2", "seaborn", "simple_white", "presentation"]
COLOR_SCALES = ["viridis", "plasma", "magma", "cividis", "turbo", "RdBu", "Blues", "Oranges", "Greens", "Purples"]


def visualizations_page():
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Chart Builder</h1>
        <p>Build any chart interactively with full control over every parameter.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    dt_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    all_cols = df.columns.tolist()

    chart_type = st.selectbox("📊 Chart Type", [
        "Bar Chart", "Grouped Bar", "Stacked Bar",
        "Line Chart", "Area Chart",
        "Scatter Plot", "Bubble Chart",
        "Pie Chart", "Donut Chart",
        "Box Plot", "Violin Plot",
        "Histogram", "2D Histogram (Heatmap)",
        "Treemap", "Sunburst",
        "Funnel Chart", "Waterfall Chart",
        "Heatmap (Correlation)", "Strip Plot"
    ])

    st.markdown("---")
    ctrl, preview = st.columns([1, 2])

    with ctrl:
        st.markdown("#### ⚙️ Parameters")
        template = st.selectbox("Theme", TEMPLATES)
        title = st.text_input("Chart title", chart_type)
        height = st.slider("Height (px)", 300, 900, 520, 20)
        color_scale = st.selectbox("Color scale", COLOR_SCALES)

        fig = None

        if chart_type in ("Bar Chart", "Grouped Bar", "Stacked Bar"):
            x = st.selectbox("X axis", all_cols)
            y = st.selectbox("Y axis", num_cols if num_cols else all_cols)
            color = st.selectbox("Color", ["None"] + cat_cols + num_cols)
            agg = st.selectbox("Aggregation", ["sum", "mean", "count", "median", "max", "min"])
            sort_by = st.radio("Sort bars", ["None", "Ascending", "Descending"], horizontal=True)
            color_val = color if color != "None" else None
            barmode = "group" if chart_type == "Grouped Bar" else ("stack" if chart_type == "Stacked Bar" else "relative")
            try:
                temp = df.groupby([x] + ([color_val] if color_val else []))[y].agg(agg).reset_index()
                if sort_by == "Ascending":
                    temp = temp.sort_values(y)
                elif sort_by == "Descending":
                    temp = temp.sort_values(y, ascending=False)
                fig = px.bar(temp, x=x, y=y, color=color_val, barmode=barmode,
                             template=template, title=title, color_continuous_scale=color_scale,
                             text_auto=True)
            except Exception as e:
                st.error(str(e))

        elif chart_type == "Line Chart":
            x = st.selectbox("X axis", dt_cols + all_cols)
            y = st.multiselect("Y axis (one or more)", num_cols, default=num_cols[:1])
            color = st.selectbox("Color", ["None"] + cat_cols)
            markers = st.checkbox("Show markers", True)
            color_val = color if color != "None" else None
            if y:
                try:
                    if len(y) == 1:
                        fig = px.line(df.sort_values(x), x=x, y=y[0], color=color_val,
                                      markers=markers, template=template, title=title)
                    else:
                        melt = df[[x] + y].melt(id_vars=x, var_name="Series", value_name="Value")
                        fig = px.line(melt.sort_values(x), x=x, y="Value", color="Series",
                                      markers=markers, template=template, title=title)
                except Exception as e:
                    st.error(str(e))

        elif chart_type == "Area Chart":
            x = st.selectbox("X axis", dt_cols + all_cols)
            y = st.multiselect("Y axis", num_cols, default=num_cols[:1])
            stack = st.checkbox("Stack areas", False)
            if y:
                try:
                    melt = df[[x] + y].melt(id_vars=x, var_name="Series", value_name="Value")
                    fig = px.area(melt.sort_values(x), x=x, y="Value", color="Series",
                                  template=template, title=title,
                                  groupnorm="fraction" if stack else None)
                except Exception as e:
                    st.error(str(e))

        elif chart_type == "Scatter Plot":
            x = st.selectbox("X axis", num_cols if num_cols else all_cols)
            y = st.selectbox("Y axis", [c for c in num_cols if c != x] or num_cols)
            color = st.selectbox("Color by", ["None"] + cat_cols + num_cols)
            tl = st.checkbox("Trend line (OLS)", False)
            opacity = st.slider("Opacity", 0.1, 1.0, 0.7)
            color_val = color if color != "None" else None
            try:
                fig = px.scatter(df, x=x, y=y, color=color_val, opacity=opacity,
                                 trendline="ols" if tl else None,
                                 template=template, title=title, color_continuous_scale=color_scale)
            except Exception as e:
                st.error(str(e))

        elif chart_type == "Bubble Chart":
            x = st.selectbox("X axis", num_cols if num_cols else all_cols)
            y = st.selectbox("Y axis", [c for c in num_cols if c != x] or num_cols)
            size = st.selectbox("Bubble size", num_cols)
            color = st.selectbox("Color", ["None"] + cat_cols + num_cols)
            color_val = color if color != "None" else None
            try:
                fig = px.scatter(df, x=x, y=y, size=size, color=color_val,
                                 template=template, title=title, color_continuous_scale=color_scale,
                                 opacity=0.7, size_max=40)
            except Exception as e:
                st.error(str(e))

        elif chart_type in ("Pie Chart", "Donut Chart"):
            names = st.selectbox("Labels", cat_cols + all_cols)
            values = st.selectbox("Values", num_cols if num_cols else all_cols)
            top_n = st.slider("Top N slices", 3, 20, 10)
            try:
                temp = df.groupby(names)[values].sum().nlargest(top_n).reset_index()
                hole = 0.45 if chart_type == "Donut Chart" else 0
                fig = px.pie(temp, names=names, values=values, hole=hole,
                             template=template, title=title, color_discrete_sequence=px.colors.qualitative.Set3)
            except Exception as e:
                st.error(str(e))

        elif chart_type == "Box Plot":
            y = st.selectbox("Value column", num_cols if num_cols else all_cols)
            x = st.selectbox("Group by", ["None"] + cat_cols)
            color = st.selectbox("Color", ["None"] + cat_cols)
            pts = st.radio("Show points", ["outliers", "all", False], horizontal=True)
            x_val = x if x != "None" else None
            color_val = color if color != "None" else None
            try:
                fig = px.box(df, x=x_val, y=y, color=color_val, points=pts,
                             template=template, title=title, notched=st.checkbox("Notched", False))
            except Exception as e:
                st.error(str(e))

        elif chart_type == "Violin Plot":
            y = st.selectbox("Value column", num_cols if num_cols else all_cols)
            x = st.selectbox("Group by", ["None"] + cat_cols)
            color = st.selectbox("Color", ["None"] + cat_cols)
            box = st.checkbox("Show box inside", True)
            pts = st.checkbox("Show points", False)
            x_val = x if x != "None" else None
            color_val = color if color != "None" else None
            try:
                fig = px.violin(df, x=x_val, y=y, color=color_val, box=box,
                                points="all" if pts else False,
                                template=template, title=title)
            except Exception as e:
                st.error(str(e))

        elif chart_type == "Histogram":
            col = st.selectbox("Column", num_cols + cat_cols)
            bins = st.slider("Bins", 5, 200, 30)
            color = st.selectbox("Color by", ["None"] + cat_cols)
            norm = st.selectbox("Normalize", ["count", "percent", "density", "probability"])
            color_val = color if color != "None" else None
            try:
                fig = px.histogram(df, x=col, color=color_val, nbins=bins,
                                   histnorm=norm if norm != "count" else None,
                                   template=template, title=title, barmode="overlay", opacity=0.75)
            except Exception as e:
                st.error(str(e))

        elif chart_type == "2D Histogram (Heatmap)":
            if len(num_cols) >= 2:
                x = st.selectbox("X axis", num_cols)
                y = st.selectbox("Y axis", [c for c in num_cols if c != x])
                nbins = st.slider("Bins", 10, 100, 30)
                try:
                    fig = px.density_heatmap(df, x=x, y=y, nbinsx=nbins, nbinsy=nbins,
                                             color_continuous_scale=color_scale,
                                             template=template, title=title)
                except Exception as e:
                    st.error(str(e))

        elif chart_type == "Treemap":
            path = st.multiselect("Hierarchy path (ordered)", cat_cols, default=cat_cols[:min(2, len(cat_cols))])
            values = st.selectbox("Values", num_cols if num_cols else all_cols)
            color = st.selectbox("Color metric", ["None"] + num_cols)
            color_val = color if color != "None" else None
            if path:
                try:
                    fig = px.treemap(df, path=[px.Constant("All")] + path, values=values,
                                     color=color_val, color_continuous_scale=color_scale,
                                     template=template, title=title)
                except Exception as e:
                    st.error(str(e))

        elif chart_type == "Sunburst":
            path = st.multiselect("Hierarchy (ordered)", cat_cols, default=cat_cols[:min(2, len(cat_cols))])
            values = st.selectbox("Values", num_cols if num_cols else all_cols)
            if path:
                try:
                    fig = px.sunburst(df, path=path, values=values,
                                      template=template, title=title,
                                      color_discrete_sequence=px.colors.qualitative.Set3)
                except Exception as e:
                    st.error(str(e))

        elif chart_type == "Funnel Chart":
            x = st.selectbox("Values (numeric)", num_cols if num_cols else all_cols)
            y = st.selectbox("Stage labels", cat_cols + all_cols)
            try:
                temp = df.groupby(y)[x].sum().reset_index().sort_values(x, ascending=False)
                fig = px.funnel(temp, x=x, y=y, template=template, title=title)
            except Exception as e:
                st.error(str(e))

        elif chart_type == "Waterfall Chart":
            x = st.selectbox("Category column", cat_cols + all_cols)
            y = st.selectbox("Value column", num_cols if num_cols else all_cols)
            try:
                temp = df.groupby(x)[y].sum().reset_index()
                fig = go.Figure(go.Waterfall(
                    x=temp[x].astype(str).tolist(),
                    y=temp[y].tolist(),
                    connector={"line": {"color": "rgb(63,63,63)"}},
                ))
                fig.update_layout(title=title, template=template, height=height)
            except Exception as e:
                st.error(str(e))

        elif chart_type == "Heatmap (Correlation)":
            sel_cols = st.multiselect("Columns", num_cols, default=num_cols[:min(10, len(num_cols))])
            method = st.selectbox("Method", ["pearson", "spearman", "kendall"])
            if sel_cols and len(sel_cols) >= 2:
                try:
                    corr = df[sel_cols].corr(method=method)
                    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                                    zmin=-1, zmax=1, template=template, title=title,
                                    aspect="auto")
                except Exception as e:
                    st.error(str(e))

        elif chart_type == "Strip Plot":
            y = st.selectbox("Value", num_cols if num_cols else all_cols)
            x = st.selectbox("Group by", ["None"] + cat_cols)
            color = st.selectbox("Color", ["None"] + cat_cols)
            x_val = x if x != "None" else None
            color_val = color if color != "None" else None
            try:
                fig = px.strip(df, x=x_val, y=y, color=color_val,
                               template=template, title=title)
            except Exception as e:
                st.error(str(e))

    with preview:
        if fig is not None:
            fig.update_layout(height=height, title_font_size=15)
            st.plotly_chart(fig, use_container_width=True)

            buf = io.StringIO()
            fig.write_html(buf)
            html_bytes = buf.getvalue().encode()
            st.download_button(
                "📥 Download Chart as HTML",
                data=html_bytes,
                file_name=f"{title.replace(' ', '_')}.html",
                mime="text/html"
            )
        else:
            st.info("Configure the chart parameters on the left to generate a preview.")
