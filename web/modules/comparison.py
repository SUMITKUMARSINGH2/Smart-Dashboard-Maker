import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO

_PLOTLY_DARK = dict(
    paper_bgcolor="#0A0F1E",
    plot_bgcolor="#0D1526",
    font=dict(color="#94A3B8", family="Space Grotesk"),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    title_font=dict(size=13, color="#E2E8F0"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.05)"),
)
NEON = ["#00D4FF", "#FF006E", "#10B981", "#F59E0B", "#A855F7", "#0EA5E9"]
CLR_A = "#00D4FF"
CLR_B = "#FF006E"
CLR_MATCH  = "#10B981"
CLR_ONLY_A = "#F59E0B"
CLR_ONLY_B = "#A855F7"


def _load_file(uploaded) -> pd.DataFrame | None:
    name = uploaded.name.lower()
    try:
        if name.endswith(".csv"):
            return pd.read_csv(uploaded)
        elif name.endswith((".xls", ".xlsx")):
            return pd.read_excel(uploaded)
        elif name.endswith(".json"):
            return pd.read_json(uploaded)
        elif name.endswith(".parquet"):
            return pd.read_parquet(uploaded)
    except Exception as e:
        st.error(f"Could not load file: {e}")
    return None


def _dtype_label(dtype) -> str:
    s = str(dtype)
    if "int" in s:   return "integer"
    if "float" in s: return "float"
    if "bool" in s:  return "boolean"
    if "datetime" in s or "date" in s: return "datetime"
    return "text"


def _schema_compare(df_a: pd.DataFrame, df_b: pd.DataFrame) -> pd.DataFrame:
    cols_a = {c: _dtype_label(df_a[c].dtype) for c in df_a.columns}
    cols_b = {c: _dtype_label(df_b[c].dtype) for c in df_b.columns}
    all_cols = sorted(set(cols_a) | set(cols_b))
    rows = []
    for c in all_cols:
        in_a = c in cols_a
        in_b = c in cols_b
        rows.append({
            "Column":   c,
            "Dataset A": cols_a.get(c, "—"),
            "Dataset B": cols_b.get(c, "—"),
            "Status":  ("Both"    if in_a and in_b else
                        "A only"  if in_a else "B only"),
            "Type match": ("✓" if in_a and in_b and cols_a[c] == cols_b[c] else
                           "✗" if in_a and in_b else "—"),
        })
    return pd.DataFrame(rows)


def _stat_compare(df_a: pd.DataFrame, df_b: pd.DataFrame, col: str) -> dict:
    sa, sb = df_a[col].dropna(), df_b[col].dropna()
    out = {}
    for label, s in [("A", sa), ("B", sb)]:
        out[label] = {
            "count":  len(s),
            "mean":   s.mean()  if pd.api.types.is_numeric_dtype(s) else None,
            "median": s.median() if pd.api.types.is_numeric_dtype(s) else None,
            "std":    s.std()   if pd.api.types.is_numeric_dtype(s) else None,
            "min":    s.min()   if pd.api.types.is_numeric_dtype(s) else None,
            "max":    s.max()   if pd.api.types.is_numeric_dtype(s) else None,
            "nulls":  df_a[col].isna().sum() if label=="A" else df_b[col].isna().sum(),
            "unique": s.nunique(),
        }
    return out


def comparison_page():
    st.markdown("""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// dataset comparison</div>
        <h2>Data Comparison</h2>
        <div class='page-header-bar'></div>
        <p>Upload a second dataset and compare schemas, statistics, and distributions side-by-side</p>
    </div>""", unsafe_allow_html=True)

    # ── Dataset A ─────────────────────────────────────────────────────────────
    df_a = st.session_state.get("df")
    name_a = st.session_state.get("filename", "Dataset A") or "Dataset A"

    # ── Dataset B upload ──────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:rgba(255,0,110,0.04);border:1px solid rgba(255,0,110,0.18);
                border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:1.2rem;'>
        <div style='font-size:.62rem;font-weight:600;letter-spacing:.14em;color:#FF006E;
                    text-transform:uppercase;font-family:"JetBrains Mono",monospace;
                    margin-bottom:.7rem;'>Dataset B — Upload to compare</div>
    """, unsafe_allow_html=True)
    up_b = st.file_uploader(
        "Upload Dataset B (CSV, Excel, JSON, Parquet)",
        type=["csv","xlsx","xls","json","parquet"],
        key="cmp_upload_b",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if df_a is None:
        st.warning("Please upload Dataset A via the Upload Data page first.")
        return

    df_b = None
    if up_b is not None:
        df_b = _load_file(up_b)
        name_b = up_b.name
    elif st.session_state.get("_cmp_df_b") is not None:
        df_b   = st.session_state["_cmp_df_b"]
        name_b = st.session_state.get("_cmp_name_b", "Dataset B")
    else:
        name_b = "Dataset B"

    if up_b is not None and df_b is not None:
        st.session_state["_cmp_df_b"]   = df_b
        st.session_state["_cmp_name_b"] = up_b.name

    if df_b is None:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;
                    border:1px dashed rgba(255,0,110,0.12);border-radius:18px;
                    background:rgba(255,0,110,0.02);margin-top:1rem;'>
            <div style='font-size:3rem;opacity:.15;margin-bottom:1rem;'>⟺</div>
            <div style='color:#4A5568;font-size:.95rem;'>
                Upload a second dataset above to start comparing
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Header cards ─────────────────────────────────────────────────────────
    h1, hdiv, h2 = st.columns([5,1,5])
    for col_ui, df_x, nm, clr in [(h1,df_a,name_a,CLR_A),(h2,df_b,name_b,CLR_B)]:
        col_ui.markdown(f"""
        <div style='background:rgba(255,255,255,0.025);border:1px solid {clr}30;
                    border-radius:14px;padding:1.2rem 1.4rem;'>
            <div style='font-size:.62rem;font-weight:600;letter-spacing:.14em;
                        color:{clr};text-transform:uppercase;
                        font-family:"JetBrains Mono",monospace;margin-bottom:.5rem;'>
                {'Dataset A' if clr==CLR_A else 'Dataset B'}
            </div>
            <div style='font-size:.85rem;color:#E2E8F0;font-weight:600;
                        margin-bottom:.8rem;overflow:hidden;text-overflow:ellipsis;
                        white-space:nowrap;' title='{nm}'>{nm}</div>
            <div style='display:flex;gap:1.2rem;flex-wrap:wrap;'>
                <div><div style='font-size:1.3rem;font-weight:800;color:{clr};'>{len(df_x):,}</div>
                     <div style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                                 text-transform:uppercase;letter-spacing:.08em;'>rows</div></div>
                <div><div style='font-size:1.3rem;font-weight:800;color:{clr};'>{len(df_x.columns):,}</div>
                     <div style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                                 text-transform:uppercase;letter-spacing:.08em;'>columns</div></div>
                <div><div style='font-size:1.3rem;font-weight:800;color:{clr};'>
                         {df_x.memory_usage(deep=True).sum()/1024:.0f}KB</div>
                     <div style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                                 text-transform:uppercase;letter-spacing:.08em;'>memory</div></div>
            </div>
        </div>""", unsafe_allow_html=True)
    hdiv.markdown("""
    <div style='display:flex;align-items:center;justify-content:center;height:100%;
                font-size:1.8rem;color:#1E293B;'>⟺</div>""", unsafe_allow_html=True)

    # ── Summary badges ────────────────────────────────────────────────────────
    cols_a_set = set(df_a.columns)
    cols_b_set = set(df_b.columns)
    shared = cols_a_set & cols_b_set
    only_a = cols_a_set - cols_b_set
    only_b = cols_b_set - cols_a_set

    row_diff = len(df_b) - len(df_a)
    row_diff_sign = "+" if row_diff > 0 else ""

    st.markdown(f"""
    <div style='display:flex;gap:.8rem;flex-wrap:wrap;margin:1.2rem 0;'>
        <div style='background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                    border-radius:10px;padding:.6rem 1.1rem;'>
            <span style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                         text-transform:uppercase;letter-spacing:.1em;'>Shared columns</span>
            <span style='color:{CLR_MATCH};font-weight:700;font-size:1rem;margin-left:.5rem;'>{len(shared)}</span>
        </div>
        <div style='background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);
                    border-radius:10px;padding:.6rem 1.1rem;'>
            <span style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                         text-transform:uppercase;letter-spacing:.1em;'>A only</span>
            <span style='color:{CLR_ONLY_A};font-weight:700;font-size:1rem;margin-left:.5rem;'>{len(only_a)}</span>
        </div>
        <div style='background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.25);
                    border-radius:10px;padding:.6rem 1.1rem;'>
            <span style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                         text-transform:uppercase;letter-spacing:.1em;'>B only</span>
            <span style='color:{CLR_ONLY_B};font-weight:700;font-size:1rem;margin-left:.5rem;'>{len(only_b)}</span>
        </div>
        <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);
                    border-radius:10px;padding:.6rem 1.1rem;'>
            <span style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                         text-transform:uppercase;letter-spacing:.1em;'>Row delta</span>
            <span style='color:{"#10B981" if row_diff>=0 else "#FF006E"};font-weight:700;
                         font-size:1rem;margin-left:.5rem;'>{row_diff_sign}{row_diff:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Main tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Schema",
        "Statistics",
        "Distributions",
        "Value Overlap",
        "Export Report",
    ])

    schema_df = _schema_compare(df_a, df_b)

    # ── Tab 1: Schema ─────────────────────────────────────────────────────────
    with tab1:
        sc1, sc2 = st.columns(2)

        # Venn-style bar
        venn_df = pd.DataFrame([
            {"Group":"Shared",   "Count":len(shared),  "color":CLR_MATCH},
            {"Group":"A only",   "Count":len(only_a),  "color":CLR_ONLY_A},
            {"Group":"B only",   "Count":len(only_b),  "color":CLR_ONLY_B},
        ])
        fig_venn = px.bar(venn_df, x="Group", y="Count", text_auto=True,
                          color="Group",
                          color_discrete_map={
                              "Shared":CLR_MATCH, "A only":CLR_ONLY_A, "B only":CLR_ONLY_B
                          },
                          template="plotly_dark", title="Column presence")
        fig_venn.update_layout(showlegend=False, height=280, **_PLOTLY_DARK)
        sc1.plotly_chart(fig_venn, use_container_width=True)

        # Type match donut
        type_match_count = int((schema_df["Type match"]=="✓").sum())
        type_mismatch    = int((schema_df["Type match"]=="✗").sum())
        fig_tm = px.pie(
            values=[type_match_count, type_mismatch, len(only_a)+len(only_b)],
            names=["Type match","Type mismatch","Not in both"],
            color_discrete_sequence=[CLR_MATCH,"#FF006E","#1E293B"],
            hole=0.52, template="plotly_dark", title="Type compatibility"
        )
        fig_tm.update_layout(height=280, **_PLOTLY_DARK)
        sc2.plotly_chart(fig_tm, use_container_width=True)

        # Schema table with color coding
        def style_status(val):
            if val == "Both":    return f"color:{CLR_MATCH};font-weight:600;"
            if val == "A only":  return f"color:{CLR_ONLY_A};font-weight:600;"
            if val == "B only":  return f"color:{CLR_ONLY_B};font-weight:600;"
            return ""
        def style_typematch(val):
            if val == "✓": return f"color:{CLR_MATCH};font-weight:700;"
            if val == "✗": return f"color:#FF006E;font-weight:700;"
            return "color:#2D3748;"

        styled = schema_df.style \
            .applymap(style_status,     subset=["Status"]) \
            .applymap(style_typematch,  subset=["Type match"])
        st.dataframe(styled, use_container_width=True, height=420)

        if only_a:
            st.markdown(f"<span style='color:{CLR_ONLY_A};font-size:.8rem;font-weight:600;'>Columns only in A:</span> "
                        + ", ".join(f"`{c}`" for c in sorted(only_a)), unsafe_allow_html=True)
        if only_b:
            st.markdown(f"<span style='color:{CLR_ONLY_B};font-size:.8rem;font-weight:600;'>Columns only in B:</span> "
                        + ", ".join(f"`{c}`" for c in sorted(only_b)), unsafe_allow_html=True)

    # ── Tab 2: Statistics ──────────────────────────────────────────────────────
    with tab2:
        shared_num = [c for c in shared
                      if pd.api.types.is_numeric_dtype(df_a[c])
                      and pd.api.types.is_numeric_dtype(df_b[c])]

        if not shared_num:
            st.info("No shared numeric columns found for statistical comparison.")
        else:
            # Stat comparison table
            stat_rows = []
            for c in shared_num:
                sa, sb = df_a[c].dropna(), df_b[c].dropna()
                mean_delta = (sb.mean() - sa.mean()) / (abs(sa.mean()) + 1e-9) * 100
                std_delta  = (sb.std()  - sa.std())  / (abs(sa.std())  + 1e-9) * 100
                stat_rows.append({
                    "Column":       c,
                    "Mean A":       round(sa.mean(), 4),
                    "Mean B":       round(sb.mean(), 4),
                    "Mean Δ%":      round(mean_delta, 1),
                    "Std A":        round(sa.std(),  4),
                    "Std B":        round(sb.std(),  4),
                    "Std Δ%":       round(std_delta, 1),
                    "Nulls A":      int(df_a[c].isna().sum()),
                    "Nulls B":      int(df_b[c].isna().sum()),
                    "Unique A":     int(sa.nunique()),
                    "Unique B":     int(sb.nunique()),
                })

            stat_df = pd.DataFrame(stat_rows)

            def color_delta(val):
                if isinstance(val, (int,float)):
                    if abs(val) > 20: return f"color:#FF006E;font-weight:700;"
                    if abs(val) > 5:  return f"color:#F59E0B;font-weight:600;"
                    return f"color:{CLR_MATCH};"
                return ""

            styled_s = stat_df.style.applymap(color_delta, subset=["Mean Δ%","Std Δ%"])
            st.dataframe(styled_s, use_container_width=True, height=420)

            # Mean shift bar chart
            st.markdown("<br>", unsafe_allow_html=True)
            fig_ms = go.Figure()
            fig_ms.add_trace(go.Bar(name=f"A — {name_a[:20]}",
                                     x=stat_df["Column"], y=stat_df["Mean A"],
                                     marker_color=CLR_A, opacity=0.85))
            fig_ms.add_trace(go.Bar(name=f"B — {name_b[:20]}",
                                     x=stat_df["Column"], y=stat_df["Mean B"],
                                     marker_color=CLR_B, opacity=0.85))
            fig_ms.update_layout(barmode="group", title="Mean values — A vs B",
                                  height=350, **_PLOTLY_DARK)
            st.plotly_chart(fig_ms, use_container_width=True)

            # Δ% heatmap
            delta_data = stat_df[["Column","Mean Δ%","Std Δ%"]].set_index("Column")
            fig_hm = px.imshow(
                delta_data.T, text_auto=True, aspect="auto",
                color_continuous_scale=["#10B981","#0D1526","#FF006E"],
                color_continuous_midpoint=0,
                template="plotly_dark",
                title="% change from A → B (red = large shift)"
            )
            fig_hm.update_layout(height=200, **_PLOTLY_DARK)
            st.plotly_chart(fig_hm, use_container_width=True)

    # ── Tab 3: Distributions ──────────────────────────────────────────────────
    with tab3:
        shared_cols = sorted(shared)
        if not shared_cols:
            st.info("No shared columns found.")
        else:
            d_col = st.selectbox("Column to compare", shared_cols, key="cmp_dcol")

            is_num_a = pd.api.types.is_numeric_dtype(df_a[d_col])
            is_num_b = pd.api.types.is_numeric_dtype(df_b[d_col])

            if is_num_a and is_num_b:
                # Overlapping histograms
                fig_d = go.Figure()
                fig_d.add_trace(go.Histogram(
                    x=df_a[d_col].dropna(), name=f"A — {name_a[:15]}",
                    nbinsx=40, marker_color=CLR_A, opacity=0.65,
                ))
                fig_d.add_trace(go.Histogram(
                    x=df_b[d_col].dropna(), name=f"B — {name_b[:15]}",
                    nbinsx=40, marker_color=CLR_B, opacity=0.65,
                ))
                fig_d.update_layout(barmode="overlay", height=380,
                                     title=f"{d_col} — distribution overlay",
                                     **_PLOTLY_DARK,
                                     xaxis_title=d_col, yaxis_title="Count")
                st.plotly_chart(fig_d, use_container_width=True)

                # KDE-style violin
                import plotly.figure_factory as ff
                try:
                    va = df_a[d_col].dropna().tolist()
                    vb = df_b[d_col].dropna().tolist()
                    if len(va) > 1 and len(vb) > 1:
                        fig_kde = ff.create_distplot(
                            [va, vb],
                            group_labels=[f"A — {name_a[:12]}", f"B — {name_b[:12]}"],
                            colors=[CLR_A, CLR_B],
                            show_rug=False,
                        )
                        fig_kde.update_layout(height=320,
                                               title=f"{d_col} — density comparison",
                                               **_PLOTLY_DARK)
                        st.plotly_chart(fig_kde, use_container_width=True)
                except Exception:
                    pass

                # Box side-by-side
                box_df = pd.concat([
                    df_a[[d_col]].assign(Dataset=f"A — {name_a[:15]}"),
                    df_b[[d_col]].assign(Dataset=f"B — {name_b[:15]}"),
                ])
                fig_box = px.box(box_df, x="Dataset", y=d_col, color="Dataset",
                                  color_discrete_sequence=[CLR_A, CLR_B],
                                  template="plotly_dark",
                                  title=f"{d_col} — box comparison",
                                  points="outliers")
                fig_box.update_layout(height=340, showlegend=False, **_PLOTLY_DARK)
                st.plotly_chart(fig_box, use_container_width=True)

            else:
                # Categorical: side-by-side bar
                va = df_a[d_col].value_counts().head(20).reset_index()
                vb = df_b[d_col].value_counts().head(20).reset_index()
                va.columns = ["Value","Count"]
                vb.columns = ["Value","Count"]
                va["Dataset"] = f"A — {name_a[:15]}"
                vb["Dataset"] = f"B — {name_b[:15]}"
                cat_df = pd.concat([va, vb])
                fig_cat = px.bar(cat_df, x="Value", y="Count", color="Dataset",
                                  barmode="group",
                                  color_discrete_sequence=[CLR_A, CLR_B],
                                  template="plotly_dark",
                                  title=f"{d_col} — top value counts")
                fig_cat.update_layout(height=380, **_PLOTLY_DARK)
                st.plotly_chart(fig_cat, use_container_width=True)

    # ── Tab 4: Value Overlap ──────────────────────────────────────────────────
    with tab4:
        shared_cat = [c for c in shared
                      if not pd.api.types.is_numeric_dtype(df_a[c])
                      or df_a[c].nunique() < 50]
        shared_cat = sorted(shared_cat) or sorted(shared)

        if not shared_cat:
            st.info("No suitable columns for value overlap analysis.")
        else:
            ov_col = st.selectbox("Column", shared_cat, key="cmp_ovcol")
            vals_a = set(df_a[ov_col].dropna().astype(str).unique())
            vals_b = set(df_b[ov_col].dropna().astype(str).unique())

            only_in_a = vals_a - vals_b
            only_in_b = vals_b - vals_a
            in_both   = vals_a & vals_b

            ov1, ov2, ov3 = st.columns(3)
            for kpi, val, lbl, clr in [
                (ov1, len(in_both),   "shared values",    CLR_MATCH),
                (ov2, len(only_in_a), "only in A",        CLR_ONLY_A),
                (ov3, len(only_in_b), "only in B",        CLR_ONLY_B),
            ]:
                kpi.markdown(f"""
                <div style='background:rgba(255,255,255,0.025);border:1px solid {clr}30;
                            border-radius:12px;padding:1rem 1.2rem;text-align:center;'>
                    <div style='font-size:1.6rem;font-weight:800;color:{clr};'>{val:,}</div>
                    <div style='font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;
                                color:#4A5568;font-family:"JetBrains Mono",monospace;
                                margin-top:.2rem;'>{lbl}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Venn donut
            fig_ov = px.pie(
                values=[len(in_both), len(only_in_a), len(only_in_b)],
                names=["Shared","A only","B only"],
                color_discrete_sequence=[CLR_MATCH, CLR_ONLY_A, CLR_ONLY_B],
                hole=0.52, template="plotly_dark",
                title=f"'{ov_col}' value overlap"
            )
            fig_ov.update_layout(height=300, **_PLOTLY_DARK)
            st.plotly_chart(fig_ov, use_container_width=True)

            o1, o2, o3 = st.columns(3)
            with o1:
                st.markdown(f"<span style='color:{CLR_MATCH};font-size:.78rem;font-weight:600;'>In both</span>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(sorted(in_both), columns=["Value"]),
                             use_container_width=True, height=220)
            with o2:
                st.markdown(f"<span style='color:{CLR_ONLY_A};font-size:.78rem;font-weight:600;'>Only in A</span>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(sorted(only_in_a), columns=["Value"]),
                             use_container_width=True, height=220)
            with o3:
                st.markdown(f"<span style='color:{CLR_ONLY_B};font-size:.78rem;font-weight:600;'>Only in B</span>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(sorted(only_in_b), columns=["Value"]),
                             use_container_width=True, height=220)

    # ── Tab 5: Export Report ──────────────────────────────────────────────────
    with tab5:
        st.markdown("""
        <div style='background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.15);
                    border-radius:12px;padding:1rem 1.3rem;margin-bottom:1rem;
                    font-size:.83rem;color:#64748B;'>
            The comparison report includes the schema diff, statistical summary,
            and null / unique counts for all shared columns.
        </div>""", unsafe_allow_html=True)

        # Build summary report dict
        report_sections = {}

        # Schema
        report_sections["schema"] = schema_df

        # Stats for shared numeric
        shared_num_e = [c for c in shared
                        if pd.api.types.is_numeric_dtype(df_a[c])
                        and pd.api.types.is_numeric_dtype(df_b[c])]
        stat_rows_e = []
        for c in shared_num_e:
            sa, sb = df_a[c].dropna(), df_b[c].dropna()
            stat_rows_e.append({
                "Column": c,
                "Mean A": round(sa.mean(),4), "Mean B": round(sb.mean(),4),
                "Std A":  round(sa.std(),4),  "Std B":  round(sb.std(),4),
                "Min A":  round(sa.min(),4),   "Min B":  round(sb.min(),4),
                "Max A":  round(sa.max(),4),   "Max B":  round(sb.max(),4),
                "Nulls A": int(df_a[c].isna().sum()), "Nulls B": int(df_b[c].isna().sum()),
                "Unique A": int(sa.nunique()),          "Unique B": int(sb.nunique()),
            })
        if stat_rows_e:
            report_sections["statistics"] = pd.DataFrame(stat_rows_e)

        # Shape summary
        shape_df = pd.DataFrame([
            {"Metric":"Rows",    "Dataset A": len(df_a), "Dataset B": len(df_b),
             "Delta": len(df_b)-len(df_a)},
            {"Metric":"Columns", "Dataset A": len(df_a.columns), "Dataset B": len(df_b.columns),
             "Delta": len(df_b.columns)-len(df_a.columns)},
            {"Metric":"Shared columns","Dataset A":len(shared),"Dataset B":len(shared),
             "Delta":0},
            {"Metric":"A-only cols","Dataset A":len(only_a),"Dataset B":0,"Delta":-len(only_a)},
            {"Metric":"B-only cols","Dataset A":0,"Dataset B":len(only_b),"Delta":len(only_b)},
        ])
        report_sections["shape"] = shape_df

        # Export as Excel with sheets
        buf = BytesIO()
        try:
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                for sheet, data in report_sections.items():
                    data.to_excel(writer, sheet_name=sheet[:31], index=False)
            buf.seek(0)
            st.download_button(
                "Download Comparison Report (Excel)",
                data=buf,
                file_name="comparison_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception:
            pass

        # CSV fallback
        csv_report = pd.concat(list(report_sections.values()), axis=0, ignore_index=True)
        st.download_button(
            "Download as CSV",
            data=schema_df.to_csv(index=False).encode(),
            file_name="comparison_schema.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("<br><span style='color:#A0AEC0;font-weight:600;font-size:.83rem;'>Shape summary</span>", unsafe_allow_html=True)
        st.dataframe(shape_df, use_container_width=True)

        st.markdown("<br><span style='color:#A0AEC0;font-weight:600;font-size:.83rem;'>Schema diff preview</span>", unsafe_allow_html=True)
        st.dataframe(schema_df, use_container_width=True)
