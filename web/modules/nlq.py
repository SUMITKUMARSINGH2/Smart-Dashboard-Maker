import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import textwrap
from difflib import get_close_matches

_PLOTLY_DARK = dict(
    paper_bgcolor="#0A0F1E",
    plot_bgcolor="#0D1526",
    font=dict(color="#94A3B8", family="Space Grotesk"),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    title_font=dict(size=14, color="#E2E8F0"),
)

NEON_COLORS = ["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#0EA5E9","#A855F7","#14B8A6"]


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()


def _find_columns(query: str, cols: list[str]) -> list[str]:
    found = []
    qn = _normalize(query)
    for col in cols:
        cn = _normalize(col)
        if cn in qn or cn.replace("_", " ") in qn:
            found.append(col); continue
        words = cn.replace("_", " ").split()
        if len(words) > 1 and all(w in qn for w in words):
            found.append(col); continue
        qwords = qn.split()
        matches = get_close_matches(cn.replace("_", " "), qwords, n=1, cutoff=0.82)
        if matches:
            found.append(col)
    return list(dict.fromkeys(found))


def _find_top_n(query: str) -> int | None:
    m = re.search(r"\btop\s+(\d+)\b", query, re.I)
    if m: return int(m.group(1))
    if re.search(r"\btop\b", query, re.I): return 5
    m2 = re.search(r"\bbottom\s+(\d+)\b", query, re.I)
    if m2: return -int(m2.group(1))
    return None


def _find_agg(query: str) -> str:
    q = query.lower()
    if re.search(r"\b(total|sum)\b", q): return "sum"
    if re.search(r"\b(average|avg|mean)\b", q): return "mean"
    if re.search(r"\b(count|number of|how many)\b", q): return "count"
    if re.search(r"\b(max|maximum|highest|largest|biggest)\b", q): return "max"
    if re.search(r"\b(min|minimum|lowest|smallest)\b", q): return "min"
    return "mean"


def _find_by_col(query: str, cat_cols: list[str], dt_cols: list[str]) -> str | None:
    patterns = [
        r"\bby\s+([\w ]+?)(?:\s+and|\s+vs|\s+vs\.|\s+over|\s*$|,)",
        r"\bper\s+([\w ]+?)(?:\s+and|\s+vs|\s*$|,)",
        r"\bacross\s+([\w ]+?)(?:\s*$|,|\band\b)",
        r"\bfor each\s+([\w ]+?)(?:\s*$|,|\band\b)",
        r"\bgroup(?:ed)? by\s+([\w ]+?)(?:\s*$|,|\band\b)",
    ]
    for pat in patterns:
        m = re.search(pat, query, re.I)
        if m:
            mention = m.group(1).strip()
            matches = _find_columns(mention, cat_cols + dt_cols)
            if matches: return matches[0]
    return None


def _find_chart_hint(query: str) -> str | None:
    q = query.lower()
    if re.search(r"\bheatmap\b|\bcorrelation matrix\b|\bmatrix\b", q): return "heatmap"
    if re.search(r"\btreemap\b|\bhierarch", q): return "treemap"
    if re.search(r"\bbox plot\b|\bbox chart\b|\bboxplot\b|\boutlier\b", q): return "box"
    if re.search(r"\bpie\b|\bbreakdown\b|\bshare\b|\bproportion\b|\bcomposition\b", q): return "pie"
    if re.search(r"\bscatter\b|\bvs\b|\bversus\b|\bcorrelation between\b|\brelation between\b", q): return "scatter"
    if re.search(r"\bhistogram\b|\bfrequency\b|\bspread\b", q): return "histogram"
    if re.search(r"\bdistribution\b", q) and not re.search(r"\bby\b", q): return "histogram"
    if re.search(r"\btrend\b|\bover time\b|\bmonthly\b|\bweekly\b|\bdaily\b|\btimeline\b|\btime series\b", q): return "line"
    if re.search(r"\bbox\b", q): return "box"
    if re.search(r"\bbar\b|\bcompare\b|\branked?\b|\btop \d\b|\bbottom \d\b", q): return "bar"
    return None


def _has_time_intent(query: str) -> bool:
    return bool(re.search(
        r"\bover time\b|\btrend\b|\bmonthly\b|\bweekly\b|\bdaily\b|\btimeline\b"
        r"|\btime series\b|\bby month\b|\bby week\b|\bby day\b|\bhistorical\b"
        r"|\bper month\b|\bper week\b|\bper day\b|\byearly\b|\bannual\b",
        query, re.I
    ))


def _interpret(query: str, df: pd.DataFrame):
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    dt_cols  = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    mentioned  = _find_columns(query, df.columns.tolist())
    top_n      = _find_top_n(query)
    agg        = _find_agg(query)
    by_col     = _find_by_col(query, cat_cols, dt_cols)
    chart_hint = _find_chart_hint(query)

    men_num = [c for c in mentioned if c in num_cols]
    men_cat = [c for c in mentioned if c in cat_cols]
    men_dt  = [c for c in mentioned if c in dt_cols]

    metric    = men_num[0] if men_num else (num_cols[0] if num_cols else None)
    dimension = men_cat[0] if men_cat else (by_col or (cat_cols[0] if cat_cols else None))
    date_col  = men_dt[0]  if men_dt  else (dt_cols[0] if dt_cols else None)

    fig  = None
    code = None
    title = query.strip().rstrip("?").capitalize()

    top_n_val = _find_top_n(query)
    if top_n_val and chart_hint is None: chart_hint = "bar"
    if chart_hint is None and dimension and metric and not _has_time_intent(query): chart_hint = "bar"

    if chart_hint == "line" or (date_col and _has_time_intent(query)):
        if date_col and metric:
            freq_map = {"month": "ME", "week": "W", "day": "D", "quarter": "QE", "year": "YE"}
            freq = "ME"
            for k, v in freq_map.items():
                if k in query.lower(): freq = v; break
            ts = df[[date_col, metric]].dropna()
            ts = ts.set_index(date_col).resample(freq)[metric].agg(agg).reset_index()
            ts.columns = ["Date", metric]
            fig = px.line(ts, x="Date", y=metric, markers=True,
                          template="plotly_dark", title=title,
                          color_discrete_sequence=["#00D4FF"])
            fig.add_scatter(x=ts["Date"], y=ts[metric].rolling(3, min_periods=1).mean(),
                            mode="lines", line=dict(color="#FF006E", dash="dash", width=1.5),
                            name="3-period avg")
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv", parse_dates=["{date_col}"])
                ts = df.set_index("{date_col}").resample("{freq}")["{metric}"].{agg}().reset_index()
                fig = px.line(ts, x="{date_col}", y="{metric}", markers=True)
                fig.show()
            """)
            return fig, code, f"Showing **{metric}** {agg} over time (resampled {freq})"

    _non_scatter = ("histogram", "bar", "pie", "box", "heatmap", "treemap", "line")
    if chart_hint == "scatter" or (len(men_num) >= 2 and chart_hint not in _non_scatter):
        x_col = men_num[0] if len(men_num) >= 2 else (num_cols[0] if num_cols else None)
        y_col = men_num[1] if len(men_num) >= 2 else (num_cols[1] if len(num_cols) >= 2 else None)
        if x_col and y_col:
            color = dimension if dimension and dimension in cat_cols else None
            fig = px.scatter(df, x=x_col, y=y_col, color=color,
                             trendline="ols", template="plotly_dark", title=title,
                             opacity=0.7, color_discrete_sequence=NEON_COLORS)
            corr = df[[x_col, y_col]].dropna().corr().iloc[0, 1]
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv")
                fig = px.scatter(df, x="{x_col}", y="{y_col}", trendline="ols")
                fig.show()
            """)
            return fig, code, f"Scatter of **{y_col}** vs **{x_col}** | Pearson r = {corr:.3f}"

    if chart_hint == "heatmap":
        cols_to_use = men_num if len(men_num) >= 2 else num_cols[:min(8, len(num_cols))]
        if len(cols_to_use) >= 2:
            corr = df[cols_to_use].corr()
            fig = px.imshow(corr, text_auto=".2f",
                            color_continuous_scale=["#FF006E","#0D1526","#00D4FF"],
                            zmin=-1, zmax=1, template="plotly_dark", title=title, aspect="auto")
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv")
                corr = df[{cols_to_use}].corr()
                fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r")
                fig.show()
            """)
            return fig, code, f"Correlation matrix for {len(cols_to_use)} numeric columns"

    if chart_hint == "histogram":
        col = metric
        if col:
            color = dimension if dimension and dimension in cat_cols else None
            fig = px.histogram(df, x=col, color=color, nbins=40, template="plotly_dark",
                               title=title, barmode="overlay", opacity=0.8,
                               color_discrete_sequence=NEON_COLORS)
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv")
                fig = px.histogram(df, x="{col}", nbins=40)
                fig.show()
            """)
            return fig, code, f"Distribution of **{col}**"

    if chart_hint == "box":
        col = metric
        if col:
            fig = px.box(df, x=dimension, y=col, color=dimension,
                         template="plotly_dark", title=title, points="outliers",
                         color_discrete_sequence=NEON_COLORS)
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv")
                fig = px.box(df, x="{dimension}", y="{col}", color="{dimension}")
                fig.show()
            """)
            return fig, code, f"Box plot of **{col}** grouped by **{dimension}**"

    if chart_hint == "treemap" and len(cat_cols) >= 1 and metric:
        path_cols = men_cat if men_cat else cat_cols[:min(2, len(cat_cols))]
        fig = px.treemap(df, path=[px.Constant("All")] + path_cols, values=metric,
                         color=metric,
                         color_continuous_scale=["#1E293B","#7C3AED","#00D4FF"],
                         template="plotly_dark", title=title)
        code = textwrap.dedent(f"""
            import pandas as pd, plotly.express as px
            df = pd.read_csv("your_file.csv")
            fig = px.treemap(df, path=[px.Constant("All")] + {path_cols}, values="{metric}")
            fig.show()
        """)
        return fig, code, f"Treemap of **{metric}** by {' → '.join(path_cols)}"

    if chart_hint == "pie" and dimension and metric:
        temp = df.groupby(dimension)[metric].agg(agg)
        if top_n and top_n > 0: temp = temp.nlargest(top_n)
        temp = temp.reset_index()
        fig = px.pie(temp, names=dimension, values=metric, hole=0.42,
                     template="plotly_dark", title=title,
                     color_discrete_sequence=NEON_COLORS)
        code = textwrap.dedent(f"""
            import pandas as pd, plotly.express as px
            df = pd.read_csv("your_file.csv")
            temp = df.groupby("{dimension}")["{metric}"].{agg}().reset_index()
            fig = px.pie(temp, names="{dimension}", values="{metric}", hole=0.42)
            fig.show()
        """)
        return fig, code, f"**{metric}** {agg} share by **{dimension}**"

    if dimension and metric:
        temp = df.groupby(dimension)[metric].agg(agg).reset_index()
        ascending = False
        if top_n is not None:
            if top_n > 0: temp = temp.nlargest(top_n, metric)
            else: temp = temp.nsmallest(abs(top_n), metric); ascending = True
        else:
            temp = temp.sort_values(metric, ascending=ascending)

        n_label = f"Top {top_n}" if top_n and top_n > 0 else (f"Bottom {abs(top_n)}" if top_n else "All")
        fig = px.bar(temp, x=metric, y=dimension, orientation="h",
                     color=metric,
                     color_continuous_scale=["#1E293B","#7C3AED","#00D4FF"],
                     template="plotly_dark", title=title, text_auto=".3s")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        code = textwrap.dedent(f"""
            import pandas as pd, plotly.express as px
            df = pd.read_csv("your_file.csv")
            temp = df.groupby("{dimension}")["{metric}"].{agg}()\\
                      .nlargest({top_n or 10}).reset_index()
            fig = px.bar(temp, x="{metric}", y="{dimension}", orientation="h", text_auto=True)
            fig.show()
        """)
        return fig, code, f"**{metric}** {agg} per **{dimension}** ({n_label} shown)"

    if metric:
        fig = px.histogram(df, x=metric, nbins=40, template="plotly_dark", title=title,
                           color_discrete_sequence=["#00D4FF"])
        code = textwrap.dedent(f"""
            import pandas as pd, plotly.express as px
            df = pd.read_csv("your_file.csv")
            fig = px.histogram(df, x="{metric}", nbins=40)
            fig.show()
        """)
        return fig, code, f"Distribution of **{metric}**"

    return None, None, "Could not understand the query. Please try rephrasing."


EXAMPLES = [
    ("▦ Bar",       "Show top 5 categories by total revenue"),
    ("∿ Trend",     "Show revenue trend over time monthly"),
    ("◉ Scatter",   "Correlation between revenue and profit"),
    ("◔ Pie",       "Breakdown of revenue by region"),
    ("▭ Box",       "Distribution of revenue by channel box plot"),
    ("▦ Heatmap",   "Correlation heatmap of all numeric columns"),
    ("⬡ Treemap",   "Treemap of revenue by region and category"),
    ("≈ Histogram", "Distribution of customer age"),
    ("⊞ Ranking",   "Average profit per sales rep ranked"),
    ("⏱ Monthly",   "Total profit monthly trend"),
]


def nlq_page():
    st.markdown("""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// natural language queries</div>
        <h2>Ask Your Data</h2>
        <div class='page-header-bar'></div>
        <p>Type any analytics question in plain English — get a chart instantly</p>
    </div>""", unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
    dt_cols  = df.select_dtypes(include=["datetime","datetimetz"]).columns.tolist()

    st.markdown("""
    <div style='background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.2);
                border-radius:14px;padding:1.3rem 1.6rem;margin-bottom:1.2rem;'>
        <div style='font-size:.65rem;font-weight:600;color:#00D4FF;margin-bottom:.5rem;
                    letter-spacing:.12em;text-transform:uppercase;font-family:"JetBrains Mono",monospace;'>
            Ask a question about your data
        </div>
    """, unsafe_allow_html=True)

    query = st.text_input(
        label="query",
        label_visibility="collapsed",
        placeholder='e.g. "Show top 5 categories by total revenue" or "Revenue trend monthly"',
        key="nlq_input",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:.72rem;font-weight:600;color:#4A5568;margin-bottom:.5rem;font-family:\"JetBrains Mono\",monospace;'>// Try an example</div>",
                unsafe_allow_html=True)
    row1, row2 = st.columns(5), st.columns(5)
    for i, (icon_label, example) in enumerate(EXAMPLES):
        target = row1[i % 5] if i < 5 else row2[i % 5]
        if target.button(icon_label, key=f"ex_{i}", use_container_width=True):
            st.session_state["nlq_input"] = example
            query = example

    with st.expander("Available columns in your dataset"):
        c1, c2, c3 = st.columns(3)
        c1.markdown("**Numeric**\n" + "\n".join(f"- `{c}`" for c in num_cols))
        c2.markdown("**Categorical**\n" + "\n".join(f"- `{c}`" for c in cat_cols))
        c3.markdown("**Date/Time**\n" + ("\n".join(f"- `{c}`" for c in dt_cols) if dt_cols else "- None detected"))

    if not query:
        st.markdown("""
        <div style='text-align:center;padding:3rem 2rem;color:#2D3748;
                    border:1px dashed rgba(0,212,255,0.1);border-radius:16px;margin-top:1rem;'>
            <div style='font-size:2.5rem;margin-bottom:.8rem;opacity:.3;'>◐</div>
            <div style='font-size:.95rem;font-weight:600;color:#4A5568;'>Ask anything about your data</div>
            <div style='font-size:.82rem;margin-top:.4rem;'>Examples above, or type your own question</div>
        </div>""", unsafe_allow_html=True)
        return

    with st.spinner("Interpreting your query…"):
        fig, code, description = _interpret(query, df)

    if fig is None:
        st.error("Could not generate a chart for that query. Try rephrasing or use one of the examples.")
        with st.expander("Tips for better queries"):
            st.markdown("""
            - **Mention column names** from your dataset, e.g. *"revenue by region"*
            - **Use keywords**: `top 5`, `average`, `total`, `trend`, `distribution`, `correlation`, `breakdown`
            - **Specify chart type** optionally: `bar chart`, `scatter`, `pie`, `histogram`, `box plot`, `heatmap`, `treemap`
            - **Time queries**: include `monthly`, `weekly`, `daily`, `over time`
            """)
        return

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(0,212,255,0.06),rgba(124,58,237,0.06));
                border:1px solid rgba(0,212,255,0.18);border-radius:12px;
                padding:.75rem 1.2rem;margin-bottom:1rem;
                display:flex;align-items:center;gap:.8rem;'>
        <div style='font-size:1.2rem;'>✦</div>
        <div style='font-size:.86rem;color:#A0AEC0;'>{description}</div>
    </div>
    """, unsafe_allow_html=True)

    fig.update_layout(height=500, **_PLOTLY_DARK)
    st.plotly_chart(fig, use_container_width=True)

    dl_col, _ = st.columns([1, 2])
    import io as _io
    buf = _io.StringIO()
    fig.write_html(buf)
    dl_col.download_button(
        "Download Chart as HTML",
        data=buf.getvalue().encode(),
        file_name="nlq_chart.html",
        mime="text/html",
        use_container_width=True,
    )

    if code:
        with st.expander("View / Copy Python Code", expanded=False):
            st.code(code.strip(), language="python")

    if "nlq_history" not in st.session_state:
        st.session_state["nlq_history"] = []
    if query and (not st.session_state["nlq_history"] or st.session_state["nlq_history"][-1] != query):
        st.session_state["nlq_history"].append(query)

    if len(st.session_state["nlq_history"]) > 1:
        st.markdown("---")
        st.markdown("<div style='font-size:.72rem;font-weight:600;color:#4A5568;margin-bottom:.4rem;font-family:\"JetBrains Mono\",monospace;'>// Query history</div>",
                    unsafe_allow_html=True)
        for prev in reversed(st.session_state["nlq_history"][:-1][-5:]):
            if st.button(f"↩ {prev}", key=f"hist_{prev}", use_container_width=False):
                st.session_state["nlq_input"] = prev
                st.rerun()
