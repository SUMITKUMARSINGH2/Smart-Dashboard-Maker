import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import textwrap
from difflib import get_close_matches


# ── helpers ────────────────────────────────────────────────────────────────

def _ph(title, sub):
    st.markdown(f"""
    <div class='ph-wrap'>
        <div class='ph-eyebrow'>Natural Language Query</div>
        <h2 class='ph-title'>{title}</h2>
        <div class='ph-bar'></div>
        <p class='ph-sub'>{sub}</p>
    </div>""", unsafe_allow_html=True)


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).strip()


def _find_columns(query: str, cols: list[str]) -> list[str]:
    """Return column names mentioned (or closely matching) in the query."""
    found = []
    qn = _normalize(query)
    for col in cols:
        cn = _normalize(col)
        # exact token match
        if cn in qn or cn.replace("_", " ") in qn:
            found.append(col)
            continue
        # fuzzy partial: each word of col appears in query
        words = cn.replace("_", " ").split()
        if len(words) > 1 and all(w in qn for w in words):
            found.append(col)
            continue
        # single-word fuzzy via difflib
        qwords = qn.split()
        matches = get_close_matches(cn.replace("_", " "), qwords, n=1, cutoff=0.82)
        if matches:
            found.append(col)
    return list(dict.fromkeys(found))   # preserve order, dedupe


def _find_top_n(query: str) -> int | None:
    m = re.search(r"\btop\s+(\d+)\b", query, re.I)
    if m:
        return int(m.group(1))
    if re.search(r"\btop\b", query, re.I):
        return 5
    if re.search(r"\bbottom\s+(\d+)\b", query, re.I):
        return -int(re.search(r"\bbottom\s+(\d+)\b", query, re.I).group(1))
    return None


def _find_agg(query: str) -> str:
    q = query.lower()
    if re.search(r"\b(total|sum)\b", q): return "sum"
    if re.search(r"\b(average|avg|mean)\b", q): return "mean"
    if re.search(r"\b(count|number of|how many)\b", q): return "count"
    if re.search(r"\b(max|maximum|highest|largest|biggest)\b", q): return "max"
    if re.search(r"\b(min|minimum|lowest|smallest)\b", q): return "min"
    return "mean"   # default


def _find_by_col(query: str, cat_cols: list[str], dt_cols: list[str]) -> str | None:
    """Find the grouping dimension from 'by X', 'per X', 'across X', 'for each X'."""
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
            cands = cat_cols + dt_cols
            matches = _find_columns(mention, cands)
            if matches:
                return matches[0]
    return None


def _find_chart_hint(query: str) -> str | None:
    q = query.lower()
    # High-specificity hints first to avoid false positives
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
    """Return True only when the query explicitly asks for a time-based view."""
    return bool(re.search(
        r"\bover time\b|\btrend\b|\bmonthly\b|\bweekly\b|\bdaily\b|\btimeline\b"
        r"|\btime series\b|\bby month\b|\bby week\b|\bby day\b|\bhistorical\b"
        r"|\bper month\b|\bper week\b|\bper day\b|\byearly\b|\bannual\b",
        query, re.I
    ))


# ── main decision engine ────────────────────────────────────────────────────

def _interpret(query: str, df: pd.DataFrame):
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    dt_cols  = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    mentioned  = _find_columns(query, df.columns.tolist())
    top_n      = _find_top_n(query)
    agg        = _find_agg(query)
    by_col     = _find_by_col(query, cat_cols, dt_cols)
    chart_hint = _find_chart_hint(query)

    # Pull numeric and categorical from mentioned
    men_num = [c for c in mentioned if c in num_cols]
    men_cat = [c for c in mentioned if c in cat_cols]
    men_dt  = [c for c in mentioned if c in dt_cols]

    metric    = men_num[0] if men_num else (num_cols[0] if num_cols else None)
    dimension = men_cat[0] if men_cat else (by_col or (cat_cols[0] if cat_cols else None))
    date_col  = men_dt[0]  if men_dt  else (dt_cols[0] if dt_cols else None)

    TMPL = "plotly_white"
    fig  = None
    code = None
    title = query.strip().rstrip("?").capitalize()

    LAYOUT = dict(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFAF9",
        font=dict(color="#374151"),
        title_font=dict(size=14, color="#1C1917"),
    )

    # ── TOP N without explicit chart hint → always bar ─────────────────────
    top_n_val = _find_top_n(query)
    if top_n_val and chart_hint is None:
        chart_hint = "bar"

    # ── "ranked / per / by" with cat+num and no time intent → bar ─────────
    if chart_hint is None and dimension and metric and not _has_time_intent(query):
        chart_hint = "bar"

    # ── time trend ──────────────────────────────────────────────────────────
    if chart_hint == "line" or (date_col and _has_time_intent(query)):
        if date_col and metric:
            freq_map = {"month": "ME", "week": "W", "day": "D", "quarter": "QE", "year": "YE"}
            freq = "ME"
            for k, v in freq_map.items():
                if k in query.lower():
                    freq = v; break
            ts = df[[date_col, metric]].dropna()
            ts = ts.set_index(date_col).resample(freq)[metric].agg(agg).reset_index()
            ts.columns = ["Date", metric]
            fig = px.line(ts, x="Date", y=metric, markers=True,
                          template=TMPL, title=title,
                          color_discrete_sequence=["#7C3AED"])
            fig.add_scatter(x=ts["Date"], y=ts[metric].rolling(3, min_periods=1).mean(),
                            mode="lines", line=dict(color="#F43F5E", dash="dash", width=1.5),
                            name="3-period avg")
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv", parse_dates=["{date_col}"])
                ts = df.set_index("{date_col}").resample("{freq}")["{metric}"].{agg}().reset_index()
                fig = px.line(ts, x="{date_col}", y="{metric}", markers=True)
                fig.show()
            """)
            return fig, code, LAYOUT, f"Showing **{metric}** {agg} over time (resampled {freq})"

    # ── correlation / scatter ────────────────────────────────────────────────
    _non_scatter = ("histogram", "bar", "pie", "box", "heatmap", "treemap", "line")
    if chart_hint == "scatter" or (len(men_num) >= 2 and chart_hint not in _non_scatter):
        x_col = men_num[0] if len(men_num) >= 2 else (num_cols[0] if num_cols else None)
        y_col = men_num[1] if len(men_num) >= 2 else (num_cols[1] if len(num_cols) >= 2 else None)
        if x_col and y_col:
            color = dimension if dimension and dimension in cat_cols else None
            fig = px.scatter(df, x=x_col, y=y_col, color=color,
                             trendline="ols", template=TMPL, title=title,
                             opacity=0.7,
                             color_discrete_sequence=px.colors.qualitative.Bold)
            corr = df[[x_col, y_col]].dropna().corr().iloc[0, 1]
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv")
                fig = px.scatter(df, x="{x_col}", y="{y_col}", trendline="ols")
                fig.show()
            """)
            return fig, code, LAYOUT, f"Scatter of **{y_col}** vs **{x_col}** | Pearson r = {corr:.3f}"

    # ── correlation heatmap ──────────────────────────────────────────────────
    if chart_hint == "heatmap":
        cols_to_use = men_num if len(men_num) >= 2 else num_cols[:min(8, len(num_cols))]
        if len(cols_to_use) >= 2:
            corr = df[cols_to_use].corr()
            fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                            zmin=-1, zmax=1, template=TMPL, title=title, aspect="auto")
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv")
                corr = df[{cols_to_use}].corr()
                fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r")
                fig.show()
            """)
            return fig, code, LAYOUT, f"Correlation matrix for {len(cols_to_use)} numeric columns"

    # ── distribution ─────────────────────────────────────────────────────────
    if chart_hint == "histogram":
        col = metric
        if col:
            color = dimension if dimension and dimension in cat_cols else None
            fig = px.histogram(df, x=col, color=color, nbins=40, template=TMPL,
                               title=title, barmode="overlay", opacity=0.75,
                               color_discrete_sequence=["#7C3AED","#F43F5E","#059669","#D97706","#0EA5E9"])
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv")
                fig = px.histogram(df, x="{col}", nbins=40)
                fig.show()
            """)
            return fig, code, LAYOUT, f"Distribution of **{col}**"

    # ── box plot ─────────────────────────────────────────────────────────────
    if chart_hint == "box":
        col = metric
        if col:
            fig = px.box(df, x=dimension, y=col, color=dimension, template=TMPL,
                         title=title, points="outliers",
                         color_discrete_sequence=px.colors.qualitative.Bold)
            code = textwrap.dedent(f"""
                import pandas as pd, plotly.express as px
                df = pd.read_csv("your_file.csv")
                fig = px.box(df, x="{dimension}", y="{col}", color="{dimension}")
                fig.show()
            """)
            return fig, code, LAYOUT, f"Box plot of **{col}** grouped by **{dimension}**"

    # ── treemap ──────────────────────────────────────────────────────────────
    if chart_hint == "treemap" and len(cat_cols) >= 1 and metric:
        path_cols = men_cat if men_cat else cat_cols[:min(2, len(cat_cols))]
        fig = px.treemap(df, path=[px.Constant("All")] + path_cols, values=metric,
                         color=metric, color_continuous_scale=["#EDE9FE","#7C3AED"],
                         template=TMPL, title=title)
        code = textwrap.dedent(f"""
            import pandas as pd, plotly.express as px
            df = pd.read_csv("your_file.csv")
            fig = px.treemap(df, path=[px.Constant("All")] + {path_cols},
                             values="{metric}")
            fig.show()
        """)
        return fig, code, LAYOUT, f"Treemap of **{metric}** by {' → '.join(path_cols)}"

    # ── pie / breakdown ───────────────────────────────────────────────────────
    if chart_hint == "pie" and dimension and metric:
        temp = df.groupby(dimension)[metric].agg(agg)
        if top_n and top_n > 0:
            temp = temp.nlargest(top_n)
        temp = temp.reset_index()
        fig = px.pie(temp, names=dimension, values=metric, hole=0.42,
                     template=TMPL, title=title,
                     color_discrete_sequence=px.colors.qualitative.Bold)
        code = textwrap.dedent(f"""
            import pandas as pd, plotly.express as px
            df = pd.read_csv("your_file.csv")
            temp = df.groupby("{dimension}")["{metric}"].{agg}().reset_index()
            fig = px.pie(temp, names="{dimension}", values="{metric}", hole=0.42)
            fig.show()
        """)
        return fig, code, LAYOUT, f"**{metric}** {agg} share by **{dimension}**"

    # ── bar (default for grouped/ranked/top queries) ──────────────────────────
    if dimension and metric:
        temp = df.groupby(dimension)[metric].agg(agg).reset_index()
        ascending = False
        if top_n is not None:
            if top_n > 0:
                temp = temp.nlargest(top_n, metric)
            else:
                temp = temp.nsmallest(abs(top_n), metric)
                ascending = True
        else:
            temp = temp.sort_values(metric, ascending=ascending)

        n_label = f"Top {top_n}" if top_n and top_n > 0 else (f"Bottom {abs(top_n)}" if top_n else "All")
        fig = px.bar(temp, x=metric, y=dimension, orientation="h",
                     color=metric, color_continuous_scale=["#EDE9FE","#7C3AED"],
                     template=TMPL, title=title, text_auto=".3s")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        code = textwrap.dedent(f"""
            import pandas as pd, plotly.express as px
            df = pd.read_csv("your_file.csv")
            temp = df.groupby("{dimension}")["{metric}"].{agg}()\\
                      .nlargest({top_n or 10}).reset_index()
            fig = px.bar(temp, x="{metric}", y="{dimension}", orientation="h", text_auto=True)
            fig.show()
        """)
        return fig, code, LAYOUT, f"**{metric}** {agg} per **{dimension}** ({n_label} shown)"

    # ── single numeric: histogram fallback ───────────────────────────────────
    if metric:
        fig = px.histogram(df, x=metric, nbins=40, template=TMPL, title=title,
                           color_discrete_sequence=["#7C3AED"])
        code = textwrap.dedent(f"""
            import pandas as pd, plotly.express as px
            df = pd.read_csv("your_file.csv")
            fig = px.histogram(df, x="{metric}", nbins=40)
            fig.show()
        """)
        return fig, code, LAYOUT, f"Distribution of **{metric}**"

    return None, None, LAYOUT, "Could not understand the query. Please try rephrasing."


# ── example queries ─────────────────────────────────────────────────────────

EXAMPLES = [
    ("📊 Bar",        "Show top 5 categories by total revenue"),
    ("📈 Trend",      "Show revenue trend over time monthly"),
    ("🔵 Scatter",    "Correlation between revenue and profit"),
    ("🥧 Pie",        "Breakdown of revenue by region"),
    ("📦 Box",        "Distribution of revenue by channel box plot"),
    ("🌡️ Heatmap",    "Correlation heatmap of all numeric columns"),
    ("🌳 Treemap",    "Treemap of revenue by region and category"),
    ("📉 Histogram",  "Distribution of customer age"),
    ("🏆 Ranking",    "Average profit per sales rep ranked"),
    ("📅 Monthly",    "Total profit monthly trend"),
]


# ── page ────────────────────────────────────────────────────────────────────

def nlq_page():
    _ph("Ask Your Data", "Type any analytics question in plain English — get a chart instantly")

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
    dt_cols  = df.select_dtypes(include=["datetime","datetimetz"]).columns.tolist()

    # ── query input ──────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:#FFFFFF;border-radius:16px;padding:1.5rem 1.8rem;
                border:1.5px solid #EDE9FE;box-shadow:0 4px 20px rgba(124,58,237,.08);
                margin-bottom:1.5rem;'>
        <div style='font-size:.8rem;font-weight:700;color:#7C3AED;margin-bottom:.6rem;
                    letter-spacing:.04em;text-transform:uppercase;'>Ask a question about your data</div>
    """, unsafe_allow_html=True)

    query = st.text_input(
        label="query",
        label_visibility="collapsed",
        placeholder='e.g. "Show top 5 categories by total revenue" or "Revenue trend monthly"',
        key="nlq_input",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── example chips ─────────────────────────────────────────────────────
    st.markdown("<div style='font-size:.75rem;font-weight:700;color:#6B7280;margin-bottom:.5rem;'>Try an example</div>",
                unsafe_allow_html=True)
    row1, row2 = st.columns(5), st.columns(5)
    for i, (icon_label, example) in enumerate(EXAMPLES):
        target = row1[i % 5] if i < 5 else row2[i % 5]
        if target.button(icon_label, key=f"ex_{i}", use_container_width=True):
            st.session_state["nlq_input"] = example
            query = example

    # ── available columns hint ─────────────────────────────────────────────
    with st.expander("Available columns in your dataset"):
        c1, c2, c3 = st.columns(3)
        c1.markdown("**Numeric**\n" + "\n".join(f"- `{c}`" for c in num_cols))
        c2.markdown("**Categorical**\n" + "\n".join(f"- `{c}`" for c in cat_cols))
        c3.markdown("**Date/Time**\n" + "\n".join(f"- `{c}`" for c in dt_cols) if dt_cols else "- None detected")

    # ── run query ──────────────────────────────────────────────────────────
    if not query:
        st.markdown("""
        <div style='text-align:center;padding:3rem 2rem;color:#9CA3AF;'>
            <div style='font-size:3rem;margin-bottom:.8rem;'>💬</div>
            <div style='font-size:1rem;font-weight:600;'>Ask anything about your data</div>
            <div style='font-size:.85rem;margin-top:.4rem;'>Examples above, or type your own question</div>
        </div>""", unsafe_allow_html=True)
        return

    with st.spinner("Interpreting your query…"):
        fig, code, layout, description = _interpret(query, df)

    if fig is None:
        st.error("Could not generate a chart for that query. Try rephrasing or use one of the examples.")
        with st.expander("Tips for better queries"):
            st.markdown("""
            - **Mention column names** from your dataset, e.g. *"revenue by region"*
            - **Use keywords** like: `top 5`, `average`, `total`, `trend`, `distribution`, `correlation`, `breakdown`
            - **Specify chart type** optionally: `bar chart`, `scatter plot`, `pie`, `histogram`, `box plot`, `heatmap`, `treemap`
            - **Time queries**: include `monthly`, `weekly`, `daily`, `over time`
            """)
        return

    # ── result banner ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#F5F3FF,#FDF2F8);
                border:1.5px solid #DDD6FE;border-radius:12px;
                padding:.8rem 1.2rem;margin-bottom:1rem;
                display:flex;align-items:center;gap:.8rem;'>
        <div style='font-size:1.4rem;'>✨</div>
        <div style='font-size:.88rem;color:#374151;'>{description}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── chart ──────────────────────────────────────────────────────────────
    fig.update_layout(height=500, **layout)
    st.plotly_chart(fig, use_container_width=True)

    # ── actions row ────────────────────────────────────────────────────────
    dl_col, _ = st.columns([1, 2])
    import io
    buf = io.StringIO()
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

    # ── query history ──────────────────────────────────────────────────────
    if "nlq_history" not in st.session_state:
        st.session_state["nlq_history"] = []
    if query and (not st.session_state["nlq_history"] or st.session_state["nlq_history"][-1] != query):
        st.session_state["nlq_history"].append(query)

    if len(st.session_state["nlq_history"]) > 1:
        st.markdown("---")
        st.markdown("<div style='font-size:.8rem;font-weight:700;color:#6B7280;margin-bottom:.4rem;'>Query history</div>",
                    unsafe_allow_html=True)
        for prev in reversed(st.session_state["nlq_history"][:-1][-5:]):
            if st.button(f"↩ {prev}", key=f"hist_{prev}", use_container_width=False):
                st.session_state["nlq_input"] = prev
                st.rerun()
