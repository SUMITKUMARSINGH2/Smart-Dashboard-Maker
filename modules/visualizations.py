import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import textwrap


TEMPLATES = ["plotly_white", "plotly", "plotly_dark", "ggplot2", "seaborn", "simple_white"]
COLOR_SCALES = ["teal", "viridis", "plasma", "magma", "cividis", "turbo",
                "RdBu", "Blues", "Oranges", "Greens", "Purples", "sunset"]

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
    st.markdown(f"<div class='page-header'><h2>{title}</h2><p>{sub}</p></div>", unsafe_allow_html=True)


def _code_block(code: str):
    """Render a code block with built-in copy button."""
    with st.expander("View / Copy Python Code", expanded=False):
        st.code(code.strip(), language="python")


def _bar_code(x, y, color_val, agg, barmode, title, template, sort_by):
    color_arg = f', color="{color_val}"' if color_val else ""
    sort_code = ""
    if sort_by == "Ascending":
        sort_code = f'\ntemp = temp.sort_values("{y}")'
    elif sort_by == "Descending":
        sort_code = f'\ntemp = temp.sort_values("{y}", ascending=False)'
    grp = f'["{x}", "{color_val}"]' if color_val else f'["{x}"]'
    return textwrap.dedent(f"""
        import pandas as pd
        import plotly.express as px

        df = pd.read_csv("your_file.csv")

        temp = df.groupby({grp})["{y}"].agg("{agg}").reset_index(){sort_code}

        fig = px.bar(
            temp, x="{x}", y="{y}"{color_arg},
            barmode="{barmode}",
            template="{template}",
            title="{title}",
            text_auto=True,
        )
        fig.show()
    """)


def _line_code(x, y_list, color_val, markers, title, template):
    if len(y_list) == 1:
        return textwrap.dedent(f"""
            import pandas as pd
            import plotly.express as px

            df = pd.read_csv("your_file.csv")
            df = df.sort_values("{x}")

            fig = px.line(
                df, x="{x}", y="{y_list[0]}",
                markers={markers},
                template="{template}",
                title="{title}",
            )
            fig.show()
        """)
    y_str = str(y_list)
    return textwrap.dedent(f"""
        import pandas as pd
        import plotly.express as px

        df = pd.read_csv("your_file.csv")
        df = df.sort_values("{x}")

        # Melt multiple columns
        melt = df[["{x}"] + {y_str}].melt(id_vars="{x}", var_name="Series", value_name="Value")

        fig = px.line(
            melt, x="{x}", y="Value", color="Series",
            markers={markers},
            template="{template}",
            title="{title}",
        )
        fig.show()
    """)


def _scatter_code(x, y, color_val, tl, opacity, title, template, cscale):
    color_arg = f', color="{color_val}"' if color_val else ""
    tl_arg = ', trendline="ols"' if tl else ""
    return textwrap.dedent(f"""
        import pandas as pd
        import plotly.express as px

        df = pd.read_csv("your_file.csv")

        fig = px.scatter(
            df, x="{x}", y="{y}"{color_arg},
            opacity={opacity},
            color_continuous_scale="{cscale}",{tl_arg}
            template="{template}",
            title="{title}",
        )
        fig.show()
    """)


def _pie_code(names, values, top_n, hole, title, template):
    return textwrap.dedent(f"""
        import pandas as pd
        import plotly.express as px

        df = pd.read_csv("your_file.csv")

        temp = df.groupby("{names}")["{values}"].sum().nlargest({top_n}).reset_index()

        fig = px.pie(
            temp, names="{names}", values="{values}",
            hole={hole},
            template="{template}",
            title="{title}",
        )
        fig.show()
    """)


def _box_code(x_val, y, color_val, pts, notched, title, template):
    x_arg = f', x="{x_val}"' if x_val else ""
    c_arg = f', color="{color_val}"' if color_val else ""
    return textwrap.dedent(f"""
        import pandas as pd
        import plotly.express as px

        df = pd.read_csv("your_file.csv")

        fig = px.box(
            df{x_arg}, y="{y}"{c_arg},
            points="{pts}",
            notched={notched},
            template="{template}",
            title="{title}",
        )
        fig.show()
    """)


def _hist_code(col, bins, color_val, norm, title, template):
    c_arg = f', color="{color_val}"' if color_val else ""
    n_arg = f', histnorm="{norm}"' if norm != "count" else ""
    return textwrap.dedent(f"""
        import pandas as pd
        import plotly.express as px

        df = pd.read_csv("your_file.csv")

        fig = px.histogram(
            df, x="{col}"{c_arg},
            nbins={bins}{n_arg},
            opacity=0.75,
            template="{template}",
            title="{title}",
        )
        fig.show()
    """)


def _corr_code(sel_cols, method):
    cols_str = str(sel_cols)
    return textwrap.dedent(f"""
        import pandas as pd
        import plotly.express as px

        df = pd.read_csv("your_file.csv")

        corr = df[{cols_str}].corr(method="{method}")

        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            title="Correlation Heatmap ({method})",
        )
        fig.show()
    """)


def _treemap_code(path, values, color_val, cscale, title, template):
    p_str = str(path)
    c_arg = f', color="{color_val}"' if color_val else ""
    return textwrap.dedent(f"""
        import pandas as pd
        import plotly.express as px

        df = pd.read_csv("your_file.csv")

        fig = px.treemap(
            df,
            path=[px.Constant("All")] + {p_str},
            values="{values}"{c_arg},
            color_continuous_scale="{cscale}",
            template="{template}",
            title="{title}",
        )
        fig.show()
    """)


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

    # ── Chart type pills ──────────────────────────────────────────────────
    chart_type = st.selectbox("Chart Type", CHART_TYPES, label_visibility="collapsed")

    st.markdown("---")
    ctrl, preview = st.columns([1, 2])

    with ctrl:
        st.markdown("<div class='section-label'>Configuration</div>", unsafe_allow_html=True)
        template    = st.selectbox("Theme", TEMPLATES)
        title       = st.text_input("Title", chart_type)
        height      = st.slider("Height (px)", 300, 900, 520, 20)
        color_scale = st.selectbox("Color scale", COLOR_SCALES)

        fig  = None
        code = None

        # ── BAR ──────────────────────────────────────────────────────────
        if chart_type in ("Bar Chart", "Grouped Bar", "Stacked Bar"):
            x   = st.selectbox("X axis", all_cols)
            y   = st.selectbox("Y axis", num_cols or all_cols)
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
                             color_continuous_scale=color_scale, text_auto=True)
                code = _bar_code(x, y, color_val, agg, barmode, title, template, sort_by)
            except Exception as e: st.error(str(e))

        # ── LINE ─────────────────────────────────────────────────────────
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
                                      markers=markers, template=template, title=title)
                    else:
                        melt = df[[x]+y].melt(id_vars=x, var_name="Series", value_name="Value")
                        fig = px.line(melt.sort_values(x), x=x, y="Value", color="Series",
                                      markers=markers, template=template, title=title)
                    code = _line_code(x, y, color_val, markers, title, template)
                except Exception as e: st.error(str(e))

        # ── AREA ─────────────────────────────────────────────────────────
        elif chart_type == "Area Chart":
            x = st.selectbox("X axis", dt_cols + all_cols)
            y = st.multiselect("Y axis", num_cols, default=num_cols[:1])
            stack = st.checkbox("Stack areas", False)
            if y:
                try:
                    melt = df[[x]+y].melt(id_vars=x, var_name="Series", value_name="Value")
                    fig = px.area(melt.sort_values(x), x=x, y="Value", color="Series",
                                  template=template, title=title,
                                  groupnorm="fraction" if stack else None)
                    code = textwrap.dedent(f"""
                        import pandas as pd
                        import plotly.express as px
                        df = pd.read_csv("your_file.csv")
                        melt = df[["{x}"]+{str(y)}].melt(id_vars="{x}", var_name="Series", value_name="Value")
                        fig = px.area(melt.sort_values("{x}"), x="{x}", y="Value", color="Series",
                                      template="{template}", title="{title}")
                        fig.show()
                    """)
                except Exception as e: st.error(str(e))

        # ── SCATTER ──────────────────────────────────────────────────────
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
                                 color_continuous_scale=color_scale)
                code = _scatter_code(x, y, color_val, tl, opacity, title, template, color_scale)
            except Exception as e: st.error(str(e))

        # ── BUBBLE ───────────────────────────────────────────────────────
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
                                 opacity=0.7, size_max=45)
                code = textwrap.dedent(f"""
                    import pandas as pd
                    import plotly.express as px
                    df = pd.read_csv("your_file.csv")
                    fig = px.scatter(df, x="{x}", y="{y}", size="{size}",
                                     color={f'"{color_val}"' if color_val else 'None'},
                                     opacity=0.7, size_max=45,
                                     template="{template}", title="{title}")
                    fig.show()
                """)
            except Exception as e: st.error(str(e))

        # ── PIE / DONUT ──────────────────────────────────────────────────
        elif chart_type in ("Pie Chart", "Donut Chart"):
            names  = st.selectbox("Labels", cat_cols + all_cols)
            values = st.selectbox("Values", num_cols or all_cols)
            top_n  = st.slider("Top N slices", 3, 20, 10)
            hole   = 0.45 if chart_type == "Donut Chart" else 0
            try:
                temp = df.groupby(names)[values].sum().nlargest(top_n).reset_index()
                fig = px.pie(temp, names=names, values=values, hole=hole,
                             template=template, title=title,
                             color_discrete_sequence=px.colors.qualitative.Set2)
                code = _pie_code(names, values, top_n, hole, title, template)
            except Exception as e: st.error(str(e))

        # ── BOX ──────────────────────────────────────────────────────────
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
                             notched=notched, template=template, title=title)
                code = _box_code(x_val, y, color_val, pts, notched, title, template)
            except Exception as e: st.error(str(e))

        # ── VIOLIN ───────────────────────────────────────────────────────
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
                                template=template, title=title)
                code = textwrap.dedent(f"""
                    import pandas as pd
                    import plotly.express as px
                    df = pd.read_csv("your_file.csv")
                    fig = px.violin(df, x={f'"{x_val}"' if x_val else None}, y="{y}",
                                    color={f'"{color_val}"' if color_val else None},
                                    box={box}, points={"'all'" if pts else False},
                                    template="{template}", title="{title}")
                    fig.show()
                """)
            except Exception as e: st.error(str(e))

        # ── HISTOGRAM ────────────────────────────────────────────────────
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
                                   barmode="overlay", opacity=0.75)
                code = _hist_code(col, bins, color_val, norm, title, template)
            except Exception as e: st.error(str(e))

        # ── 2D DENSITY ───────────────────────────────────────────────────
        elif chart_type == "2D Density Heatmap":
            if len(num_cols) >= 2:
                x = st.selectbox("X axis", num_cols)
                y = st.selectbox("Y axis", [c for c in num_cols if c != x])
                nbins = st.slider("Bins", 10, 100, 30)
                try:
                    fig = px.density_heatmap(df, x=x, y=y, nbinsx=nbins, nbinsy=nbins,
                                             color_continuous_scale=color_scale,
                                             template=template, title=title)
                    code = textwrap.dedent(f"""
                        import pandas as pd
                        import plotly.express as px
                        df = pd.read_csv("your_file.csv")
                        fig = px.density_heatmap(df, x="{x}", y="{y}",
                                                  nbinsx={nbins}, nbinsy={nbins},
                                                  color_continuous_scale="{color_scale}",
                                                  template="{template}", title="{title}")
                        fig.show()
                    """)
                except Exception as e: st.error(str(e))

        # ── TREEMAP ──────────────────────────────────────────────────────
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
                    code = _treemap_code(path, values, color_val, color_scale, title, template)
                except Exception as e: st.error(str(e))

        # ── SUNBURST ─────────────────────────────────────────────────────
        elif chart_type == "Sunburst":
            path   = st.multiselect("Hierarchy", cat_cols, default=cat_cols[:min(2, len(cat_cols))])
            values = st.selectbox("Values", num_cols or all_cols)
            if path:
                try:
                    fig = px.sunburst(df, path=path, values=values,
                                      template=template, title=title,
                                      color_discrete_sequence=px.colors.qualitative.Set2)
                    code = textwrap.dedent(f"""
                        import pandas as pd
                        import plotly.express as px
                        df = pd.read_csv("your_file.csv")
                        fig = px.sunburst(df, path={str(path)}, values="{values}",
                                          template="{template}", title="{title}")
                        fig.show()
                    """)
                except Exception as e: st.error(str(e))

        # ── FUNNEL ───────────────────────────────────────────────────────
        elif chart_type == "Funnel Chart":
            x = st.selectbox("Values (numeric)", num_cols or all_cols)
            y = st.selectbox("Stage labels", cat_cols + all_cols)
            try:
                temp = df.groupby(y)[x].sum().reset_index().sort_values(x, ascending=False)
                fig = px.funnel(temp, x=x, y=y, template=template, title=title)
                code = textwrap.dedent(f"""
                    import pandas as pd
                    import plotly.express as px
                    df = pd.read_csv("your_file.csv")
                    temp = df.groupby("{y}")["{x}"].sum().reset_index().sort_values("{x}", ascending=False)
                    fig = px.funnel(temp, x="{x}", y="{y}", template="{template}", title="{title}")
                    fig.show()
                """)
            except Exception as e: st.error(str(e))

        # ── WATERFALL ────────────────────────────────────────────────────
        elif chart_type == "Waterfall Chart":
            x = st.selectbox("Category column", cat_cols + all_cols)
            y = st.selectbox("Value column", num_cols or all_cols)
            try:
                temp = df.groupby(x)[y].sum().reset_index()
                fig = go.Figure(go.Waterfall(
                    x=temp[x].astype(str).tolist(), y=temp[y].tolist(),
                    connector={"line": {"color": "#CBD5E1"}},
                ))
                fig.update_layout(title=title, template=template, height=height)
                code = textwrap.dedent(f"""
                    import pandas as pd
                    import plotly.graph_objects as go
                    df = pd.read_csv("your_file.csv")
                    temp = df.groupby("{x}")["{y}"].sum().reset_index()
                    fig = go.Figure(go.Waterfall(x=temp["{x}"].astype(str).tolist(), y=temp["{y}"].tolist()))
                    fig.update_layout(title="{title}", template="{template}")
                    fig.show()
                """)
            except Exception as e: st.error(str(e))

        # ── CORRELATION HEATMAP ──────────────────────────────────────────
        elif chart_type == "Correlation Heatmap":
            sel_cols = st.multiselect("Columns", num_cols, default=num_cols[:min(10, len(num_cols))])
            method   = st.selectbox("Method", ["pearson", "spearman", "kendall"])
            if sel_cols and len(sel_cols) >= 2:
                try:
                    corr = df[sel_cols].corr(method=method)
                    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                                    zmin=-1, zmax=1, template=template,
                                    title=title, aspect="auto")
                    code = _corr_code(sel_cols, method)
                except Exception as e: st.error(str(e))

        # ── STRIP ────────────────────────────────────────────────────────
        elif chart_type == "Strip Plot":
            y = st.selectbox("Value", num_cols or all_cols)
            x = st.selectbox("Group by", ["None"] + cat_cols)
            color = st.selectbox("Color", ["None"] + cat_cols)
            x_val = x if x != "None" else None
            color_val = color if color != "None" else None
            try:
                fig = px.strip(df, x=x_val, y=y, color=color_val,
                               template=template, title=title)
                code = textwrap.dedent(f"""
                    import pandas as pd
                    import plotly.express as px
                    df = pd.read_csv("your_file.csv")
                    fig = px.strip(df, x={f'"{x_val}"' if x_val else None}, y="{y}",
                                   color={f'"{color_val}"' if color_val else None},
                                   template="{template}", title="{title}")
                    fig.show()
                """)
            except Exception as e: st.error(str(e))

    # ── Preview panel ─────────────────────────────────────────────────────
    with preview:
        if fig is not None:
            fig.update_layout(
                height=height,
                title_font_size=14,
                title_font_color="#0F172A",
                plot_bgcolor="#F8FAFC",
                paper_bgcolor="#FFFFFF",
                font=dict(color="#334155"),
            )
            st.plotly_chart(fig, use_container_width=True)

            col_dl, col_cp = st.columns(2)
            with col_dl:
                buf = io.StringIO()
                fig.write_html(buf)
                st.download_button(
                    "Download Chart as HTML",
                    data=buf.getvalue().encode(),
                    file_name=f"{title.replace(' ', '_')}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            with col_cp:
                if code:
                    st.markdown(
                        "<div style='margin-top:0.3rem;font-size:0.8rem;color:#64748B;'>"
                        "Click <b>View / Copy Python Code</b> below to grab the code.</div>",
                        unsafe_allow_html=True
                    )

            if code:
                _code_block(code)
        else:
            st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
                        height:400px;background:#FFFFFF;border-radius:12px;border:2px dashed #E2E8F0;
                        color:#94A3B8;'>
                <div style='font-size:3rem;margin-bottom:1rem;'>📊</div>
                <div style='font-size:1rem;font-weight:500;'>Configure chart on the left</div>
                <div style='font-size:0.85rem;margin-top:0.4rem;'>Preview will appear here</div>
            </div>""", unsafe_allow_html=True)
