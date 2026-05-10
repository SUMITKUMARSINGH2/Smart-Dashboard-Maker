import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

_PLOTLY_DARK = dict(
    paper_bgcolor="#0A0F1E",
    plot_bgcolor="#0D1526",
    font=dict(color="#94A3B8", family="Space Grotesk"),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    title_font=dict(size=13, color="#E2E8F0"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.05)"),
)
NEON = ["#FF006E","#F59E0B","#00D4FF","#10B981","#A855F7","#EF4444","#0EA5E9","#14B8A6"]


def _zscore_outliers(series: pd.Series, thresh: float = 3.0):
    mu, sd = series.mean(), series.std()
    if sd == 0:
        return pd.Series(False, index=series.index)
    return (np.abs(series - mu) / sd) > thresh


def _iqr_outliers(series: pd.Series, mult: float = 1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return (series < q1 - mult * iqr) | (series > q3 + mult * iqr)


def _isolation_forest(df_num: pd.DataFrame, contamination: float = 0.05):
    try:
        from sklearn.ensemble import IsolationForest
        clf = IsolationForest(contamination=contamination, random_state=42, n_jobs=-1)
        preds = clf.fit_predict(df_num.fillna(df_num.median()))
        scores = clf.score_samples(df_num.fillna(df_num.median()))
        return preds == -1, scores
    except ImportError:
        return pd.Series(False, index=df_num.index), np.zeros(len(df_num))


def _lof(df_num: pd.DataFrame, n_neighbors: int = 20):
    try:
        from sklearn.neighbors import LocalOutlierFactor
        clf = LocalOutlierFactor(n_neighbors=min(n_neighbors, len(df_num)-1))
        preds = clf.fit_predict(df_num.fillna(df_num.median()))
        return preds == -1
    except (ImportError, ValueError):
        return pd.Series(False, index=df_num.index)


def outliers_page():
    st.markdown("""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// anomaly detection</div>
        <h2>Outlier Detection</h2>
        <div class='page-header-bar'></div>
        <p>Automatically scan for anomalies using statistical and ML methods — then bulk-annotate them</p>
    </div>""", unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    if not num_cols:
        st.warning("No numeric columns found in the dataset.")
        return

    df_num = df[num_cols].copy()

    # ── Settings panel ─────────────────────────────────────────────────────────
    with st.expander("⚙  Detection Settings", expanded=True):
        col_m, col_z, col_iq, col_c = st.columns(4)
        method = col_m.selectbox(
            "Method",
            ["Z-Score", "IQR (Tukey)", "Isolation Forest", "Local Outlier Factor", "All Methods"],
            key="od_method"
        )
        z_thresh  = col_z.slider("Z-Score threshold", 1.5, 5.0, 3.0, 0.1, key="od_zt",
                                  help="Flag rows where |z| > threshold")
        iqr_mult  = col_iq.slider("IQR multiplier",   1.0, 3.0, 1.5, 0.1, key="od_iqm",
                                   help="Flag rows below Q1 - k·IQR or above Q3 + k·IQR")
        contam    = col_c.slider("IF contamination",  0.01, 0.3, 0.05, 0.01, key="od_cont",
                                  help="Expected fraction of outliers (Isolation Forest)")

        col_cols, col_run = st.columns([3,1])
        chosen_cols = col_cols.multiselect(
            "Columns to scan (leave blank = all numeric)",
            num_cols, key="od_cols"
        )
        if not chosen_cols:
            chosen_cols = num_cols
        run_btn = col_run.button("Run Detection", type="primary", use_container_width=True, key="od_run")

    df_scan = df_num[chosen_cols].copy()

    # ── Run detection ──────────────────────────────────────────────────────────
    if run_btn or st.session_state.get("_od_results") is not None:

        if run_btn:
            with st.spinner("Scanning for outliers…"):
                results = {}

                if method in ("Z-Score", "All Methods"):
                    mask = pd.DataFrame({c: _zscore_outliers(df_scan[c], z_thresh) for c in chosen_cols})
                    results["Z-Score"] = mask.any(axis=1)

                if method in ("IQR (Tukey)", "All Methods"):
                    mask = pd.DataFrame({c: _iqr_outliers(df_scan[c], iqr_mult) for c in chosen_cols})
                    results["IQR"] = mask.any(axis=1)

                if method in ("Isolation Forest", "All Methods"):
                    is_out, scores = _isolation_forest(df_scan, contam)
                    results["IsoForest"] = pd.Series(is_out, index=df_scan.index)
                    results["_if_scores"] = scores

                if method in ("Local Outlier Factor", "All Methods"):
                    results["LOF"] = pd.Series(_lof(df_scan), index=df_scan.index)

                st.session_state["_od_results"] = results
                st.session_state["_od_cols"]    = chosen_cols

        results    = st.session_state.get("_od_results", {})
        used_cols  = st.session_state.get("_od_cols", chosen_cols)
        bool_keys  = [k for k in results if not k.startswith("_")]

        # Consensus mask (flagged by ≥1 method)
        if bool_keys:
            consensus = pd.concat([results[k] for k in bool_keys], axis=1).any(axis=1)
        else:
            consensus = pd.Series(False, index=df.index)

        outlier_idx  = df.index[consensus].tolist()
        n_out        = len(outlier_idx)
        n_total      = len(df)
        pct          = n_out / max(n_total, 1) * 100

        # ── KPI row ────────────────────────────────────────────────────────────
        k1, k2, k3, k4 = st.columns(4)
        for kpi, val, sub, clr in [
            (k1, f"{n_out:,}",         "outliers found",    "#FF006E"),
            (k2, f"{pct:.1f}%",        "of dataset",        "#F59E0B"),
            (k3, f"{n_total-n_out:,}", "clean rows",        "#10B981"),
            (k4, f"{len(used_cols)}",  "columns scanned",   "#00D4FF"),
        ]:
            kpi.markdown(f"""
            <div style='background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                        border-radius:12px;padding:1rem 1.2rem;text-align:center;'>
                <div style='font-size:1.7rem;font-weight:800;color:{clr};
                            font-family:"Space Grotesk",sans-serif;'>{val}</div>
                <div style='font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;
                            color:#4A5568;font-family:"JetBrains Mono",monospace;margin-top:.2rem;'>{sub}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Overview", "Column Drill-Down", "Scatter Explorer", "Export & Annotate"]
        )

        # ── Tab 1: Overview ───────────────────────────────────────────────────
        with tab1:
            # Method comparison bar
            if len(bool_keys) > 1:
                method_counts = {k: int(results[k].sum()) for k in bool_keys}
                mc_df = pd.DataFrame(list(method_counts.items()), columns=["Method","Count"])
                fig_m = px.bar(mc_df, x="Method", y="Count", text_auto=True,
                               color="Method", color_discrete_sequence=NEON,
                               template="plotly_dark", title="Outliers detected per method")
                fig_m.update_layout(showlegend=False, height=300, **_PLOTLY_DARK)
                st.plotly_chart(fig_m, use_container_width=True)

            # Per-column outlier count heatmap
            col_out_z   = {c: int(_zscore_outliers(df_scan[c], z_thresh).sum()) for c in used_cols}
            col_out_iqr = {c: int(_iqr_outliers(df_scan[c], iqr_mult).sum())   for c in used_cols}

            hm_df = pd.DataFrame({"Z-Score": col_out_z, "IQR": col_out_iqr}).T
            if not hm_df.empty:
                fig_hm = px.imshow(
                    hm_df,
                    text_auto=True, aspect="auto",
                    color_continuous_scale=["#0D1526","#7C3AED","#FF006E"],
                    template="plotly_dark",
                    title="Outliers per column (Z-Score vs IQR)",
                )
                fig_hm.update_layout(height=220, **_PLOTLY_DARK)
                st.plotly_chart(fig_hm, use_container_width=True)

            # Isolation Forest score distribution
            if "_if_scores" in results:
                scores = results["_if_scores"]
                fig_sc = go.Figure()
                fig_sc.add_trace(go.Histogram(
                    x=scores, nbinsx=60,
                    marker_color="#7C3AED", opacity=0.8, name="Anomaly score"
                ))
                # threshold line
                thresh_line = np.percentile(scores, contam * 100)
                fig_sc.add_vline(x=thresh_line, line_dash="dash",
                                 line_color="#FF006E",
                                 annotation_text=f"threshold ({contam*100:.0f}%)",
                                 annotation_font_color="#FF006E")
                fig_sc.update_layout(title="Isolation Forest — anomaly score distribution",
                                     height=280, **_PLOTLY_DARK,
                                     xaxis_title="Score (lower = more anomalous)",
                                     yaxis_title="Count")
                st.plotly_chart(fig_sc, use_container_width=True)

        # ── Tab 2: Column drill-down ──────────────────────────────────────────
        with tab2:
            sel_col = st.selectbox("Select column", used_cols, key="od_drill")
            c_series = df_scan[sel_col].dropna()
            z_mask   = _zscore_outliers(df[sel_col].dropna(), z_thresh)
            i_mask   = _iqr_outliers(df[sel_col].dropna(), iqr_mult)
            any_flag = z_mask | i_mask

            d1, d2, d3 = st.columns(3)
            d1.metric("Z-Score outliers", int(z_mask.sum()), f"{z_mask.mean()*100:.1f}%")
            d2.metric("IQR outliers",     int(i_mask.sum()), f"{i_mask.mean()*100:.1f}%")
            d3.metric("Either method",    int(any_flag.sum()), f"{any_flag.mean()*100:.1f}%")

            # Box plot
            flag_series = pd.Series("Normal", index=df.index)
            flag_series[z_mask & ~i_mask] = "Z-Score only"
            flag_series[~z_mask & i_mask] = "IQR only"
            flag_series[z_mask & i_mask]  = "Both methods"

            box_df = pd.DataFrame({sel_col: df[sel_col], "Status": flag_series}).dropna()
            fig_box = px.box(
                box_df, x="Status", y=sel_col,
                color="Status",
                color_discrete_map={
                    "Normal":      "#10B981",
                    "Z-Score only":"#F59E0B",
                    "IQR only":    "#00D4FF",
                    "Both methods":"#FF006E",
                },
                template="plotly_dark",
                title=f"{sel_col} — box plot by outlier status",
                points="outliers",
            )
            fig_box.update_layout(height=380, showlegend=True, **_PLOTLY_DARK)
            st.plotly_chart(fig_box, use_container_width=True)

            # Distribution
            fig_hist = go.Figure()
            normal_vals = df.loc[~any_flag, sel_col].dropna()
            out_vals    = df.loc[any_flag,  sel_col].dropna()
            fig_hist.add_trace(go.Histogram(x=normal_vals, nbinsx=50,
                                            name="Normal", marker_color="#10B981", opacity=0.7))
            fig_hist.add_trace(go.Histogram(x=out_vals, nbinsx=30,
                                            name="Outlier", marker_color="#FF006E", opacity=0.9))

            # IQR fences as vlines
            q1, q3 = df[sel_col].quantile(0.25), df[sel_col].quantile(0.75)
            iqr = q3 - q1
            for bound, label, color in [
                (q1 - iqr_mult*iqr, f"Q1−{iqr_mult}·IQR", "#F59E0B"),
                (q3 + iqr_mult*iqr, f"Q3+{iqr_mult}·IQR", "#F59E0B"),
            ]:
                fig_hist.add_vline(x=bound, line_dash="dash", line_color=color,
                                   annotation_text=label, annotation_font_color=color)

            fig_hist.update_layout(barmode="overlay", height=320,
                                   title=f"{sel_col} — distribution overlay",
                                   **_PLOTLY_DARK,
                                   xaxis_title=sel_col, yaxis_title="Count")
            st.plotly_chart(fig_hist, use_container_width=True)

            # Outlier table for this column
            with st.expander(f"Rows flagged in '{sel_col}'"):
                flag_df = df[any_flag][[sel_col]].copy()
                flag_df["Z-Score"]  = ((df[sel_col] - df[sel_col].mean()) / df[sel_col].std()).abs().round(3)
                flag_df["IQR flag"] = i_mask[any_flag].map({True:"Yes", False:""})
                flag_df = flag_df.sort_values(sel_col, ascending=False)
                st.dataframe(flag_df, use_container_width=True, height=300)

        # ── Tab 3: Scatter Explorer ───────────────────────────────────────────
        with tab3:
            if len(used_cols) < 2:
                st.info("Need at least 2 numeric columns for scatter view.")
            else:
                sc1, sc2, sc3 = st.columns(3)
                x_col  = sc1.selectbox("X axis",     used_cols, key="od_sx")
                y_col  = sc2.selectbox("Y axis",     [c for c in used_cols if c != x_col] or used_cols, key="od_sy")
                sz_col = sc3.selectbox("Size (opt)", ["—"] + used_cols, key="od_ssz")

                scatter_df = df[[x_col, y_col]].copy()
                scatter_df["Outlier"] = consensus.map({True:"Outlier", False:"Normal"})
                if sz_col != "—" and sz_col in df.columns:
                    scatter_df["_sz"] = (df[sz_col] - df[sz_col].min()) / (df[sz_col].max() - df[sz_col].min() + 1e-9) * 20 + 4
                else:
                    scatter_df["_sz"] = 6

                normal_sc  = scatter_df[scatter_df["Outlier"]=="Normal"]
                outlier_sc = scatter_df[scatter_df["Outlier"]=="Outlier"]

                fig_sc2 = go.Figure()
                fig_sc2.add_trace(go.Scatter(
                    x=normal_sc[x_col], y=normal_sc[y_col],
                    mode="markers", name="Normal",
                    marker=dict(color="#10B981", size=normal_sc["_sz"].clip(4,20),
                                opacity=0.45, line=dict(width=0))
                ))
                fig_sc2.add_trace(go.Scatter(
                    x=outlier_sc[x_col], y=outlier_sc[y_col],
                    mode="markers", name="Outlier",
                    marker=dict(color="#FF006E", size=outlier_sc["_sz"].clip(7,22),
                                symbol="diamond", opacity=0.9,
                                line=dict(color="white", width=1))
                ))
                fig_sc2.update_layout(
                    title=f"Outlier scatter — {y_col} vs {x_col}",
                    height=500, xaxis_title=x_col, yaxis_title=y_col,
                    **_PLOTLY_DARK
                )
                st.plotly_chart(fig_sc2, use_container_width=True)

                # Parallel coordinates
                if len(used_cols) >= 3:
                    pc_df = df_scan[used_cols[:6]].copy()
                    pc_df["_flag"] = consensus.astype(int)
                    dims = [dict(label=c, values=pc_df[c]) for c in used_cols[:6]]
                    dims.append(dict(label="Outlier", values=pc_df["_flag"],
                                     tickvals=[0,1], ticktext=["Normal","Outlier"]))
                    fig_pc = go.Figure(go.Parcoords(
                        line=dict(color=pc_df["_flag"],
                                  colorscale=[[0,"#10B981"],[1,"#FF006E"]],
                                  showscale=True),
                        dimensions=dims
                    ))
                    fig_pc.update_layout(title="Parallel coordinates — normal vs outlier",
                                         height=380, **_PLOTLY_DARK)
                    st.plotly_chart(fig_pc, use_container_width=True)

        # ── Tab 4: Export & Annotate ──────────────────────────────────────────
        with tab4:
            st.markdown("""
            <div style='background:rgba(255,0,110,0.05);border:1px solid rgba(255,0,110,0.2);
                        border-radius:12px;padding:1rem 1.3rem;margin-bottom:1.2rem;'>
                <div style='font-size:.62rem;font-weight:700;letter-spacing:.14em;color:#FF006E;
                            text-transform:uppercase;font-family:"JetBrains Mono",monospace;
                            margin-bottom:.4rem;'>Bulk Annotation</div>
                <div style='font-size:.83rem;color:#94A3B8;'>
                    Automatically push all detected outlier rows into the 
                    <b style='color:#E2E8F0;'>Annotations</b> module with a single click.
                    Existing manual annotations are preserved.
                </div>
            </div>""", unsafe_allow_html=True)

            ann_col1, ann_col2 = st.columns(2)
            bulk_tag   = ann_col1.selectbox(
                "Bulk tag to apply",
                ["Anomaly","Check","Important","Follow-up","Exclude"],
                key="od_btag"
            )
            bulk_prio  = ann_col2.selectbox(
                "Bulk priority",
                ["High","Critical","Medium","Low"],
                key="od_bprio"
            )
            bulk_note  = st.text_input(
                "Auto-note prefix",
                value="Auto-detected outlier",
                key="od_bnote"
            )

            st.markdown(f"""
            <div style='font-size:.78rem;color:#4A5568;margin:.5rem 0 1rem;
                        font-family:"JetBrains Mono",monospace;'>
                {n_out:,} rows will be annotated as
                <span style='color:#FF006E;font-weight:700;'>{bulk_tag}</span> /
                <span style='color:#F59E0B;font-weight:700;'>{bulk_prio}</span>
            </div>""", unsafe_allow_html=True)

            if st.button(f"Bulk Annotate {n_out:,} Outlier Rows →", type="primary",
                         key="od_bulk_ann", use_container_width=True):
                if "_ann_store" not in st.session_state:
                    st.session_state["_ann_store"] = {}
                ann = st.session_state["_ann_store"]
                ts  = datetime.now().strftime("%Y-%m-%d %H:%M")
                for idx in outlier_idx:
                    if idx not in ann:
                        ann[idx] = {
                            "tag":      bulk_tag,
                            "note":     bulk_note,
                            "priority": bulk_prio,
                            "ts":       ts,
                        }
                st.session_state["_ann_store"] = ann
                st.success(f"Annotated {n_out:,} rows as **{bulk_tag}** in the Annotations module.")

            st.markdown("---")

            # CSV export
            export_df = df.copy()
            export_df["_Outlier_Flag"]    = consensus.map({True:"Yes", False:""})
            export_df["_Outlier_Methods"] = ""
            for k in bool_keys:
                flag_col = results[k].map({True: k, False: ""})
                export_df["_Outlier_Methods"] += flag_col.where(flag_col != "", "")
                export_df["_Outlier_Methods"] = export_df["_Outlier_Methods"].str.strip()

            st.download_button(
                "Download Flagged Dataset (CSV)",
                data=export_df.to_csv(index=False).encode(),
                file_name="outliers_flagged.csv",
                mime="text/csv",
                use_container_width=True,
            )

            out_only = export_df[export_df["_Outlier_Flag"]=="Yes"]
            if not out_only.empty:
                st.download_button(
                    "Download Outliers Only (CSV)",
                    data=out_only.to_csv(index=False).encode(),
                    file_name="outliers_only.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            # Preview
            st.markdown("<br><span style='color:#A0AEC0;font-weight:600;font-size:.83rem;'>Preview (first 20 outlier rows)</span>", unsafe_allow_html=True)
            if not out_only.empty:
                st.dataframe(out_only.head(20), use_container_width=True, height=300)
            else:
                st.info("No outliers detected with current settings.")

    else:
        # Empty state
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;
                    border:1px dashed rgba(255,0,110,0.15);border-radius:18px;
                    background:rgba(255,0,110,0.03);margin-top:1rem;'>
            <div style='font-size:3rem;opacity:.2;margin-bottom:1rem;'>◎</div>
            <div style='color:#4A5568;font-size:.95rem;'>
                Configure your settings above and click <b style='color:#E2E8F0;'>Run Detection</b>
            </div>
        </div>""", unsafe_allow_html=True)
