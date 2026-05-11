import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
from difflib import get_close_matches
from styles import DARK_CSS, section_header

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,21,40,1)",
    font=dict(family="Inter", color="#E2E8F0"),
    margin=dict(l=20, r=20, t=50, b=20),
    colorway=["#818cf8", "#f472b6", "#4ade80", "#fbbf24", "#38bdf8", "#a855f7", "#f87171"],
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
)

EXAMPLE_QUERIES = [
    "show top 10 rows by revenue",
    "average salary by department",
    "distribution of age",
    "correlation between price and quantity",
    "count rows by category",
    "trend of sales over date",
    "sum of revenue by region",
    "show rows where country is USA",
    "compare revenue and profit",
    "what is the total sales",
    "minimum and maximum of price",
    "percentage breakdown of status",
    "scatter plot of age vs salary",
    "heatmap of correlations",
    "outliers in price",
]


def _fuzzy_col(query_word: str, columns: list, cutoff: float = 0.55) -> str | None:
    query_word = query_word.lower().replace("_", " ").replace("-", " ")
    col_map = {c.lower().replace("_", " ").replace("-", " "): c for c in columns}
    matches = get_close_matches(query_word, col_map.keys(), n=1, cutoff=cutoff)
    if matches:
        return col_map[matches[0]]
    for norm, orig in col_map.items():
        if query_word in norm or norm in query_word:
            return orig
    return None


def _find_columns_in_query(q: str, columns: list) -> list:
    found = []
    words = re.split(r"[\s,]+", q.lower())
    for col in columns:
        col_norm = col.lower().replace("_", " ").replace("-", " ")
        if col_norm in q.lower():
            found.append(col)
            continue
        for w in words:
            if len(w) >= 3:
                match = _fuzzy_col(w, [col])
                if match:
                    found.append(col)
                    break
    return list(dict.fromkeys(found))


def _extract_number(q: str, default: int = 10) -> int:
    nums = re.findall(r"\b(\d+)\b", q)
    return int(nums[0]) if nums else default


def _extract_filter_value(q: str) -> tuple[str | None, str | None]:
    patterns = [
        r"where\s+(\w[\w\s]*?)\s+(?:is|=|==|equals?)\s+[\"']?([^\"']+)[\"']?",
        r"filter\s+(\w[\w\s]*?)\s+(?:is|=|==|equals?)\s+[\"']?([^\"']+)[\"']?",
    ]
    for pat in patterns:
        m = re.search(pat, q, re.IGNORECASE)
        if m:
            return m.group(1).strip(), m.group(2).strip()
    return None, None


def _parse_and_execute(query: str, df: pd.DataFrame):
    q = query.lower().strip()
    cols = list(df.columns)
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    found_cols = _find_columns_in_query(q, cols)

    results = []

    # ── FILTER queries ─────────────────────────────────────────────────────────
    if any(kw in q for kw in ["where", "filter", "only", "show rows"]):
        col_name, val = _extract_filter_value(q)
        target_col = _fuzzy_col(col_name, cols) if col_name else (found_cols[0] if found_cols else None)
        if target_col and val:
            s = df[target_col]
            if pd.api.types.is_numeric_dtype(s):
                try:
                    filtered = df[s == float(val)]
                except Exception:
                    filtered = df[s.astype(str).str.lower() == val.lower()]
            else:
                filtered = df[s.astype(str).str.lower() == val.lower()]
                if filtered.empty:
                    filtered = df[s.astype(str).str.lower().str.contains(val.lower(), na=False)]
            results.append({
                "type": "filter",
                "title": f"Rows where {target_col} = '{val}'",
                "data": filtered,
            })
            return results
        elif found_cols:
            results.append({"type": "error", "msg": f"Could not parse filter condition. Try: 'show rows where {found_cols[0]} is VALUE'"})
            return results

    # ── CORRELATION / SCATTER ──────────────────────────────────────────────────
    if any(kw in q for kw in ["correlat", "scatter", "vs", " vs ", "versus", "relationship"]):
        num_found = [c for c in found_cols if c in num_cols]
        if len(num_found) >= 2:
            color_col = next((c for c in found_cols if c in cat_cols), None)
            results.append({
                "type": "scatter",
                "x": num_found[0], "y": num_found[1],
                "color": color_col,
                "title": f"Scatter: {num_found[0]} vs {num_found[1]}",
            })
            return results
        elif "heatmap" in q or "all" in q:
            results.append({"type": "corr_heatmap", "cols": num_cols[:12]})
            return results
        elif len(num_cols) >= 2:
            results.append({
                "type": "corr_heatmap",
                "cols": num_cols[:12],
                "title": "Correlation Heatmap",
            })
            return results

    # ── HEATMAP ───────────────────────────────────────────────────────────────
    if "heatmap" in q:
        results.append({"type": "corr_heatmap", "cols": num_cols[:12]})
        return results

    # ── DISTRIBUTION / HISTOGRAM ───────────────────────────────────────────────
    if any(kw in q for kw in ["distribution", "histogram", "spread", "density", "dist of", "hist"]):
        target = next((c for c in found_cols if c in num_cols), None)
        if not target and num_cols:
            target = num_cols[0]
        if target:
            results.append({"type": "histogram", "col": target, "title": f"Distribution of {target}"})
            return results

    # ── OUTLIERS ──────────────────────────────────────────────────────────────
    if any(kw in q for kw in ["outlier", "anomal", "unusual"]):
        target = next((c for c in found_cols if c in num_cols), None) or (num_cols[0] if num_cols else None)
        if target:
            results.append({"type": "outliers", "col": target})
            return results

    # ── TREND / LINE CHART ────────────────────────────────────────────────────
    if any(kw in q for kw in ["trend", "over time", "time series", "over", "by date", "by month", "by year", "by week"]):
        y_col = next((c for c in found_cols if c in num_cols), None) or (num_cols[0] if num_cols else None)
        x_col = next((c for c in found_cols if c not in num_cols or c != y_col), None)
        if not x_col:
            date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
            x_col = date_cols[0] if date_cols else (cols[0] if cols else None)
        if y_col and x_col:
            results.append({
                "type": "line",
                "x": x_col, "y": y_col,
                "title": f"Trend of {y_col} over {x_col}",
            })
            return results

    # ── COMPARE (multi-metric) ────────────────────────────────────────────────
    if any(kw in q for kw in ["compare", "comparison", "side by side", "versus", "both"]):
        targets = [c for c in found_cols if c in num_cols]
        if len(targets) >= 2:
            x_col = next((c for c in found_cols if c not in num_cols), None) or cols[0]
            results.append({
                "type": "multi_line",
                "x": x_col, "y_cols": targets[:4],
                "title": f"Comparison: {', '.join(targets[:4])}",
            })
            return results

    # ── PERCENTAGE / PIE ──────────────────────────────────────────────────────
    if any(kw in q for kw in ["percent", "proportion", "share", "pie", "breakdown", "composition"]):
        cat_col = next((c for c in found_cols if c in cat_cols), cat_cols[0] if cat_cols else None)
        val_col = next((c for c in found_cols if c in num_cols), None)
        if cat_col:
            results.append({"type": "pie", "cat": cat_col, "val": val_col})
            return results

    # ── AGGREGATION queries (sum/total/average/mean/count) ────────────────────
    agg_kws = {
        "sum": "sum", "total": "sum", "add up": "sum",
        "average": "mean", "mean": "mean", "avg": "mean",
        "count": "count", "how many": "count", "number of": "count",
        "minimum": "min", "min": "min", "lowest": "min", "smallest": "min",
        "maximum": "max", "max": "max", "highest": "max", "largest": "max",
        "median": "median",
    }

    found_agg = None
    for kw, fn in agg_kws.items():
        if kw in q:
            found_agg = fn
            break

    # ── TOP N ─────────────────────────────────────────────────────────────────
    if any(kw in q for kw in ["top", "bottom", "best", "worst", "highest", "lowest", "largest", "smallest", "rank"]):
        n = _extract_number(q)
        ascending = any(kw in q for kw in ["bottom", "worst", "lowest", "smallest"])
        num_found = [c for c in found_cols if c in num_cols]
        cat_found = [c for c in found_cols if c in cat_cols]
        sort_col = num_found[0] if num_found else (num_cols[0] if num_cols else None)
        label_col = cat_found[0] if cat_found else (cols[0] if cols else None)

        if sort_col:
            if label_col and label_col != sort_col:
                grp = df.groupby(label_col)[sort_col].sum().reset_index()
                grp_sorted = grp.sort_values(sort_col, ascending=ascending).head(n)
                results.append({
                    "type": "bar",
                    "x": label_col, "y": sort_col,
                    "data": grp_sorted,
                    "title": f"{'Bottom' if ascending else 'Top'} {n} {label_col} by {sort_col}",
                })
            else:
                sorted_df = df[[sort_col]].dropna().sort_values(sort_col, ascending=ascending).head(n)
                results.append({
                    "type": "bar",
                    "x": sorted_df.index.astype(str), "y": sort_col,
                    "data": sorted_df.reset_index(),
                    "title": f"{'Bottom' if ascending else 'Top'} {n} values of {sort_col}",
                })
            return results

    # ── AGGREGATE + GROUP BY ───────────────────────────────────────────────────
    if found_agg:
        num_found = [c for c in found_cols if c in num_cols]
        cat_found = [c for c in found_cols if c in cat_cols]

        if not num_found and found_agg in ("sum", "mean", "min", "max", "median"):
            num_found = num_cols[:1]

        # scalar aggregate (no groupby)
        if num_found and not cat_found:
            val_col = num_found[0]
            agg_val = getattr(df[val_col].dropna(), found_agg)()
            results.append({
                "type": "metric",
                "label": f"{found_agg.upper()} of {val_col}",
                "value": agg_val,
            })
            # Add full stats alongside
            if found_agg in ("min", "max", "minimum", "maximum") and len(num_found) >= 1:
                results.append({
                    "type": "stats_table",
                    "cols": num_found,
                })
            return results

        # grouped aggregate
        if num_found and cat_found:
            val_col = num_found[0]
            grp_col = cat_found[0]
            if found_agg == "count":
                grp = df.groupby(grp_col).size().reset_index(name="count")
                y_col = "count"
            else:
                grp = df.groupby(grp_col)[val_col].agg(found_agg).reset_index()
                y_col = val_col
            grp = grp.sort_values(y_col, ascending=False)
            results.append({
                "type": "bar",
                "x": grp_col, "y": y_col,
                "data": grp,
                "title": f"{found_agg.capitalize()} of {y_col} by {grp_col}",
            })
            return results

        # count-only
        if found_agg == "count" and cat_found:
            grp_col = cat_found[0]
            grp = df[grp_col].value_counts().reset_index()
            grp.columns = [grp_col, "count"]
            results.append({
                "type": "bar",
                "x": grp_col, "y": "count",
                "data": grp,
                "title": f"Count by {grp_col}",
            })
            return results

    # ── SHOW DATA (fallback table) ─────────────────────────────────────────────
    if any(kw in q for kw in ["show", "display", "list", "table", "preview", "sample"]):
        target_cols = found_cols if found_cols else cols
        n = _extract_number(q, default=50)
        results.append({
            "type": "table",
            "data": df[target_cols].head(n),
            "title": f"Showing {min(n, len(df))} rows",
        })
        return results

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    if any(kw in q for kw in ["summary", "describe", "overview", "stats", "statistics"]):
        results.append({"type": "summary"})
        return results

    # ── GENERIC FALLBACK: try to build something useful ───────────────────────
    if found_cols:
        num_found = [c for c in found_cols if c in num_cols]
        cat_found = [c for c in found_cols if c in cat_cols]

        if len(num_found) >= 2:
            results.append({
                "type": "scatter",
                "x": num_found[0], "y": num_found[1], "color": cat_found[0] if cat_found else None,
                "title": f"Scatter: {num_found[0]} vs {num_found[1]}",
            })
        elif len(num_found) == 1 and cat_found:
            grp = df.groupby(cat_found[0])[num_found[0]].mean().reset_index().sort_values(num_found[0], ascending=False)
            results.append({
                "type": "bar",
                "x": cat_found[0], "y": num_found[0],
                "data": grp,
                "title": f"Average {num_found[0]} by {cat_found[0]}",
            })
        elif len(num_found) == 1:
            results.append({"type": "histogram", "col": num_found[0], "title": f"Distribution of {num_found[0]}"})
        elif cat_found:
            grp = df[cat_found[0]].value_counts().reset_index()
            grp.columns = [cat_found[0], "count"]
            results.append({
                "type": "bar", "x": cat_found[0], "y": "count",
                "data": grp, "title": f"Count by {cat_found[0]}",
            })
    else:
        results.append({"type": "no_match"})

    return results


def _render_result(r: dict, df: pd.DataFrame):
    rtype = r.get("type")

    if rtype == "bar":
        data = r.get("data", df)
        fig = px.bar(data, x=r["x"], y=r["y"], title=r.get("title", ""),
                     color=r["x"] if isinstance(r["x"], str) else None,
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("View data"):
            st.dataframe(data, use_container_width=True, hide_index=True)

    elif rtype == "scatter":
        color_col = r.get("color")
        fig = px.scatter(df, x=r["x"], y=r["y"], color=color_col,
                         title=r.get("title", ""), opacity=0.75, trendline="ols" if not color_col else None)
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)
        corr = df[[r["x"], r["y"]]].dropna().corr().iloc[0, 1]
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
                    border-radius:8px;padding:.6rem 1rem;font-size:.82rem;color:#7c7f96;">
          Pearson correlation between <b style="color:#f1f2f6;">{r['x']}</b> and
          <b style="color:#f1f2f6;">{r['y']}</b>: <b style="color:#818cf8;">{corr:.4f}</b>
        </div>
        """, unsafe_allow_html=True)

    elif rtype == "corr_heatmap":
        sel = r.get("cols", df.select_dtypes("number").columns.tolist())
        corr = df[sel].corr()
        fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                        color_continuous_scale="RdBu_r",
                        title=r.get("title", "Correlation Heatmap"))
        fig.update_layout(**PLOTLY_THEME, height=500)
        st.plotly_chart(fig, use_container_width=True)

    elif rtype == "histogram":
        col = r["col"]
        fig = px.histogram(df, x=col, nbins=50, title=r.get("title", f"Distribution of {col}"),
                           color_discrete_sequence=["#818cf8"], marginal="box")
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)
        s = df[col].dropna()
        ca, cb, cc, cd = st.columns(4)
        ca.metric("Mean", f"{s.mean():.4g}")
        cb.metric("Median", f"{s.median():.4g}")
        cc.metric("Std Dev", f"{s.std():.4g}")
        cd.metric("Skewness", f"{s.skew():.3f}")

    elif rtype == "line":
        fig = px.line(df, x=r["x"], y=r["y"], title=r.get("title", ""), markers=False,
                      color_discrete_sequence=["#818cf8"])
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)

    elif rtype == "multi_line":
        melt = df[[r["x"]] + r["y_cols"]].melt(id_vars=r["x"], var_name="Metric", value_name="Value")
        fig = px.line(melt, x=r["x"], y="Value", color="Metric",
                      title=r.get("title", ""), markers=False)
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)

    elif rtype == "pie":
        cat_col = r["cat"]
        val_col = r.get("val")
        if val_col:
            pie_df = df.groupby(cat_col)[val_col].sum().reset_index()
            fig = px.pie(pie_df, names=cat_col, values=val_col,
                         title=f"Breakdown of {val_col} by {cat_col}")
        else:
            pie_df = df[cat_col].value_counts().reset_index()
            pie_df.columns = [cat_col, "count"]
            fig = px.pie(pie_df, names=cat_col, values="count",
                         title=f"Percentage breakdown of {cat_col}")
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)

    elif rtype == "metric":
        label = r.get("label", "Result")
        value = r.get("value")
        fmt = f"{value:,.4g}" if isinstance(value, (int, float)) else str(value)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(129,140,248,.08),rgba(168,85,247,.05));
                    border:1px solid rgba(129,140,248,.2);border-radius:16px;
                    padding:2rem;text-align:center;margin:.5rem 0;">
          <div style="font-size:3rem;font-weight:900;color:#818cf8;">{fmt}</div>
          <div style="font-size:.85rem;color:#7c7f96;margin-top:.4rem;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    elif rtype == "stats_table":
        sel_cols = r.get("cols") or df.select_dtypes("number").columns.tolist()
        st.dataframe(df[sel_cols].describe().T.round(4), use_container_width=True)

    elif rtype == "table":
        data = r.get("data", df.head(50))
        title = r.get("title", "Data")
        st.markdown(f'<div style="font-weight:600;color:#f1f2f6;margin-bottom:.5rem;">{title}</div>', unsafe_allow_html=True)
        st.dataframe(data, use_container_width=True, hide_index=True)

    elif rtype == "filter":
        data = r.get("data", pd.DataFrame())
        title = r.get("title", "Filtered Data")
        n = len(data)
        st.markdown(f"""
        <div style="background:rgba(74,222,128,.06);border:1px solid rgba(74,222,128,.2);
                    border-radius:8px;padding:.6rem 1rem;margin-bottom:.75rem;font-size:.83rem;color:#7c7f96;">
          Found <b style="color:#4ade80;">{n:,} row{'s' if n != 1 else ''}</b> matching: {title}
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(data, use_container_width=True, hide_index=True)
        if not data.empty:
            st.download_button("⬇️ Download filtered rows",
                               data.to_csv(index=False).encode(),
                               file_name="filtered.csv", mime="text/csv")

    elif rtype == "outliers":
        col = r["col"]
        s = df[col].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        mask = (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
        plot_df = pd.DataFrame({"value": s, "type": ["Outlier" if m else "Normal" for m in mask]})
        n_out = mask.sum()
        st.markdown(f"""
        <div style="background:rgba(248,113,113,.06);border:1px solid rgba(248,113,113,.2);
                    border-radius:8px;padding:.6rem 1rem;margin-bottom:.75rem;font-size:.83rem;color:#7c7f96;">
          <b style="color:#f87171;">{n_out:,} outliers</b> detected in '{col}'
          ({round(n_out/len(s)*100,1)}% of values) using IQR method
        </div>
        """, unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            fig = px.strip(plot_df, x="type", y="value", color="type",
                           color_discrete_map={"Normal": "#818cf8", "Outlier": "#f87171"},
                           title=f"Outlier Strip — {col}")
            fig.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)
        with cb:
            fig2 = px.box(df, y=col, color_discrete_sequence=["#818cf8"],
                          title=f"Box Plot — {col}")
            fig2.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig2, use_container_width=True)

    elif rtype == "summary":
        num_df = df.select_dtypes("number")
        if not num_df.empty:
            st.dataframe(num_df.describe().T.round(4), use_container_width=True)
        cat_df = df.select_dtypes(include=["object", "category"])
        if not cat_df.empty:
            st.markdown('<div style="font-weight:600;color:#f1f2f6;margin:.75rem 0 .4rem;">Categorical Columns</div>', unsafe_allow_html=True)
            st.dataframe(cat_df.describe().T, use_container_width=True)

    elif rtype == "error":
        st.error(r.get("msg", "Something went wrong parsing the query."))

    elif rtype == "no_match":
        st.markdown("""
        <div style="background:rgba(251,191,36,.06);border:1px solid rgba(251,191,36,.2);
                    border-radius:10px;padding:1rem 1.25rem;font-size:.86rem;color:#7c7f96;line-height:1.8;">
          <b style="color:#fbbf24;">Couldn't interpret that query.</b><br>
          Try being more specific. Examples:<br>
          • <i>top 10 customers by revenue</i><br>
          • <i>average salary by department</i><br>
          • <i>distribution of age</i><br>
          • <i>correlation between price and quantity</i>
        </div>
        """, unsafe_allow_html=True)


def nlq_page():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header(
        "💬", "Natural Language Query",
        "Ask questions about your data in plain English — get instant charts and answers"
    ), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data loaded. Please upload a file first.")
        return

    df = st.session_state["clean_data"]
    fname = st.session_state.get("filename", "dataset")

    # Column reference panel
    with st.expander("📋 Available columns in your dataset", expanded=False):
        col_pills = ""
        num_cols = df.select_dtypes("number").columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
        for col in df.columns:
            if col in num_cols:
                color, label = "#38bdf8", "num"
            elif col in date_cols:
                color, label = "#4ade80", "date"
            else:
                color, label = "#f472b6", "cat"
            col_pills += f'<span style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);color:{color};padding:.2rem .65rem;border-radius:999px;font-size:.73rem;margin:.2rem;display:inline-block;"><b>{col}</b> <span style="opacity:.5;font-size:.65rem;">{label}</span></span>'
        st.markdown(f'<div style="line-height:2.2;">{col_pills}</div>', unsafe_allow_html=True)

    # Query input
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(129,140,248,.07),rgba(168,85,247,.05));
                border:1px solid rgba(129,140,248,.18);border-radius:14px;padding:1.25rem 1.5rem;
                margin-bottom:.75rem;position:relative;overflow:hidden;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;
                  background:linear-gradient(90deg,#6366f1,#a855f7,#38bdf8);"></div>
      <div style="font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
                  color:#818cf8;margin-bottom:.5rem;">Ask a question</div>
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input(
        "Type your question",
        placeholder="e.g.  top 10 products by revenue   ·   average salary by department   ·   distribution of age",
        label_visibility="collapsed",
        key="nlq_input"
    )

    col_run, col_clear = st.columns([3, 1])
    with col_run:
        run = st.button("🔍 Run Query", use_container_width=True, key="nlq_run")
    with col_clear:
        if st.button("Clear History", use_container_width=True, key="nlq_clear"):
            st.session_state["nlq_history"] = []
            st.rerun()

    # Example queries
    st.markdown('<div style="font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:#3d3f52;margin:.75rem 0 .4rem;">Try an example</div>', unsafe_allow_html=True)
    ex_cols = st.columns(5)
    examples_to_show = EXAMPLE_QUERIES[:10]
    for i, ex in enumerate(examples_to_show):
        with ex_cols[i % 5]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state["nlq_pending"] = ex
                st.rerun()

    # Handle example button clicks
    if "nlq_pending" in st.session_state:
        query = st.session_state.pop("nlq_pending")
        run = True

    st.markdown("---")

    # Run query
    if run and query.strip():
        if "nlq_history" not in st.session_state:
            st.session_state["nlq_history"] = []

        with st.spinner("Analyzing your question…"):
            try:
                results = _parse_and_execute(query, df)
            except Exception as e:
                results = [{"type": "error", "msg": f"Query error: {e}"}]

        entry = {"query": query, "results": results}
        st.session_state["nlq_history"].insert(0, entry)

    # Render history
    if "nlq_history" in st.session_state and st.session_state["nlq_history"]:
        for idx, entry in enumerate(st.session_state["nlq_history"]):
            q = entry["query"]
            res = entry["results"]

            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:.75rem;margin-bottom:.5rem;">
              <div style="background:linear-gradient(135deg,#6366f1,#a855f7);
                          width:28px;height:28px;border-radius:50%;flex-shrink:0;
                          display:flex;align-items:center;justify-content:center;
                          font-size:.8rem;font-weight:700;color:#fff;margin-top:2px;">Q</div>
              <div style="background:rgba(129,140,248,.06);border:1px solid rgba(129,140,248,.15);
                          border-radius:12px;border-top-left-radius:4px;padding:.65rem 1rem;
                          font-size:.9rem;color:#f1f2f6;font-weight:500;flex:1;">
                {q}
              </div>
            </div>
            """, unsafe_allow_html=True)

            with st.container():
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:.75rem;margin-bottom:1.5rem;">
                  <div style="background:rgba(74,222,128,.15);
                              width:28px;height:28px;border-radius:50%;flex-shrink:0;
                              display:flex;align-items:center;justify-content:center;
                              font-size:.8rem;font-weight:700;color:#4ade80;margin-top:2px;">A</div>
                  <div style="flex:1;min-width:0;">
                """, unsafe_allow_html=True)

                for r in res:
                    _render_result(r, df)

                st.markdown("</div></div>", unsafe_allow_html=True)

    elif not (run and query.strip()):
        st.markdown(f"""
        <div style="text-align:center;padding:3rem 1rem;color:#475569;">
          <div style="font-size:2.5rem;margin-bottom:.75rem;">💬</div>
          <div style="font-size:1rem;font-weight:600;color:#94A3B8;margin-bottom:.4rem;">
            Ask anything about <b style="color:#f1f2f6;">{fname}</b>
          </div>
          <div style="font-size:.83rem;color:#3d3f52;max-width:420px;margin:0 auto;line-height:1.8;">
            Type a question above or click one of the example queries to get started.
            Results include auto-generated charts, stats, and downloadable data.
          </div>
        </div>
        """, unsafe_allow_html=True)
