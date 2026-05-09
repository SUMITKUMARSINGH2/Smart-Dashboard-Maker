import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

_PLOTLY_DARK = dict(
    paper_bgcolor="#0A0F1E",
    plot_bgcolor="#0D1526",
    font=dict(color="#94A3B8", family="Space Grotesk"),
    xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
    title_font=dict(size=13, color="#E2E8F0"),
)

PRESET_TAGS = ["Important", "Anomaly", "Check", "Error", "Verified", "Exclude", "Follow-up"]

TAG_COLORS = {
    "Important":  ("#F59E0B", "rgba(245,158,11,0.12)"),
    "Anomaly":    ("#FF006E", "rgba(255,0,110,0.12)"),
    "Check":      ("#00D4FF", "rgba(0,212,255,0.12)"),
    "Error":      ("#EF4444", "rgba(239,68,68,0.12)"),
    "Verified":   ("#10B981", "rgba(16,185,129,0.12)"),
    "Exclude":    ("#64748B", "rgba(100,116,139,0.12)"),
    "Follow-up":  ("#A855F7", "rgba(168,85,247,0.12)"),
    "Custom":     ("#E2E8F0", "rgba(226,232,240,0.08)"),
}

_SK = "_ann_"


def _init():
    if f"{_SK}store" not in st.session_state:
        st.session_state[f"{_SK}store"] = {}
    if f"{_SK}filter_tag" not in st.session_state:
        st.session_state[f"{_SK}filter_tag"] = "All"


def _tag_chip(tag: str) -> str:
    color, bg = TAG_COLORS.get(tag, TAG_COLORS["Custom"])
    return (f"<span style='display:inline-flex;align-items:center;gap:4px;"
            f"background:{bg};border:1px solid {color}40;border-radius:20px;"
            f"padding:.18rem .65rem;font-size:.7rem;font-weight:600;color:{color};"
            f"font-family:\"JetBrains Mono\",monospace;white-space:nowrap;'>"
            f"<span style='width:5px;height:5px;border-radius:50%;"
            f"background:{color};display:inline-block;flex-shrink:0;'></span>"
            f"{tag}</span>")


def annotations_page():
    _init()

    st.markdown("""
    <div class='page-header'>
        <div class='page-header-eyebrow'>// data annotation</div>
        <h2>Row Annotations</h2>
        <div class='page-header-bar'></div>
        <p>Tag, label, and add notes to individual rows — then export the annotated dataset</p>
    </div>""", unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df        = st.session_state.df
    ann_store = st.session_state[f"{_SK}store"]

    # ── Summary bar ────────────────────────────────────────────────────────
    total_ann  = len(ann_store)
    tag_counts = {}
    for v in ann_store.values():
        t = v.get("tag","")
        if t: tag_counts[t] = tag_counts.get(t,0)+1

    st.markdown(f"""
    <div style='display:flex;gap:.8rem;flex-wrap:wrap;margin-bottom:1.2rem;'>
        <div style='background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                    border-radius:10px;padding:.65rem 1.1rem;'>
            <span style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                         text-transform:uppercase;letter-spacing:.1em;'>Total rows</span>
            <span style='color:#F0F6FF;font-weight:700;font-size:1rem;margin-left:.5rem;'>{len(df):,}</span>
        </div>
        <div style='background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.2);
                    border-radius:10px;padding:.65rem 1.1rem;'>
            <span style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                         text-transform:uppercase;letter-spacing:.1em;'>Annotated</span>
            <span style='color:#00D4FF;font-weight:700;font-size:1rem;margin-left:.5rem;'>{total_ann:,}</span>
        </div>
        <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px;padding:.65rem 1.1rem;'>
            <span style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                         text-transform:uppercase;letter-spacing:.1em;'>Coverage</span>
            <span style='color:#A855F7;font-weight:700;font-size:1rem;margin-left:.5rem;'>
                {total_ann/max(len(df),1)*100:.1f}%
            </span>
        </div>
        {"".join(f'''<div style='background:{TAG_COLORS.get(t,TAG_COLORS["Custom"])[1]};
                    border:1px solid {TAG_COLORS.get(t,TAG_COLORS["Custom"])[0]}40;
                    border-radius:10px;padding:.65rem 1.1rem;'>
                    <span style='font-size:.62rem;color:#4A5568;font-family:"JetBrains Mono",monospace;
                                 text-transform:uppercase;letter-spacing:.1em;'>{t}</span>
                    <span style='color:{TAG_COLORS.get(t,TAG_COLORS["Custom"])[0]};font-weight:700;
                                 font-size:1rem;margin-left:.5rem;'>{c}</span>
                    </div>''' for t,c in tag_counts.items())}
    </div>
    """, unsafe_allow_html=True)

    # ── Layout: annotation panel left, table right ──────────────────────────
    left, right = st.columns([1, 2])

    with left:
        st.markdown("""
        <div style='background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.15);
                    border-radius:14px;padding:1.2rem 1.3rem;'>
            <div style='font-size:.62rem;font-weight:600;letter-spacing:.14em;color:#00D4FF;
                        text-transform:uppercase;font-family:"JetBrains Mono",monospace;
                        margin-bottom:.9rem;'>Add / Edit Annotation</div>
        """, unsafe_allow_html=True)

        row_idx = st.number_input(
            "Row number (0-indexed)",
            min_value=0, max_value=len(df)-1, value=0, step=1,
            key="ann_row_idx"
        )

        existing = ann_store.get(row_idx, {})

        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

        tag_choice = st.selectbox(
            "Tag",
            PRESET_TAGS + ["Custom"],
            index=PRESET_TAGS.index(existing["tag"]) if existing.get("tag") in PRESET_TAGS else len(PRESET_TAGS),
            key="ann_tag"
        )
        custom_tag = ""
        if tag_choice == "Custom":
            custom_tag = st.text_input("Custom tag name", value=existing.get("tag",""), key="ann_custom")

        note = st.text_area(
            "Note / comment",
            value=existing.get("note", ""),
            height=90, key="ann_note",
            placeholder="Describe why this row is flagged…"
        )

        priority = st.select_slider(
            "Priority",
            options=["Low", "Medium", "High", "Critical"],
            value=existing.get("priority", "Medium"),
            key="ann_priority"
        )

        PRIO_COLORS = {"Low":"#64748B","Medium":"#F59E0B","High":"#FF006E","Critical":"#EF4444"}
        prio_color = PRIO_COLORS.get(priority, "#64748B")

        col_save, col_del = st.columns(2)
        with col_save:
            if st.button("Save Annotation", key="ann_save", use_container_width=True, type="primary"):
                final_tag = custom_tag.strip() or tag_choice
                if final_tag and final_tag != "Custom":
                    ann_store[row_idx] = {
                        "tag":      final_tag,
                        "note":     note.strip(),
                        "priority": priority,
                        "ts":       datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    st.session_state[f"{_SK}store"] = ann_store
                    st.success(f"Row {row_idx} annotated as **{final_tag}**")
                    st.rerun()
                else:
                    st.warning("Please select or type a tag.")
        with col_del:
            if st.button("Clear Row", key="ann_del", use_container_width=True):
                if row_idx in ann_store:
                    del ann_store[row_idx]
                    st.session_state[f"{_SK}store"] = ann_store
                    st.success(f"Annotation cleared for row {row_idx}")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Row preview ──────────────────────────────────────────────────
        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
        row_data = df.iloc[row_idx]
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                    border-radius:12px;padding:1rem 1.2rem;'>
            <div style='font-size:.62rem;font-weight:600;letter-spacing:.14em;color:#64748B;
                        text-transform:uppercase;font-family:"JetBrains Mono",monospace;
                        margin-bottom:.6rem;'>Row {row_idx} preview</div>
            {"".join(
                f"<div style='display:flex;justify-content:space-between;align-items:baseline;"
                f"padding:.25rem 0;border-bottom:1px solid rgba(255,255,255,0.04);'>"
                f"<span style='font-size:.73rem;color:#64748B;font-family:\"JetBrains Mono\",monospace;"
                f"max-width:48%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{str(c)}</span>"
                f"<span style='font-size:.73rem;color:#E2E8F0;max-width:48%;text-align:right;"
                f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{str(v)}</span>"
                f"</div>"
                for c,v in zip(row_data.index[:8], row_data.values[:8])
            )}
            {"<div style='font-size:.68rem;color:#2D3748;margin-top:.4rem;text-align:center;'>… and " + str(len(row_data)-8) + " more columns</div>" if len(row_data) > 8 else ""}
        </div>
        """, unsafe_allow_html=True)

        if existing:
            t = existing.get("tag","")
            col_ann, _ = TAG_COLORS.get(t, TAG_COLORS["Custom"])
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.02);border:1px solid {col_ann}30;
                        border-radius:10px;padding:.8rem 1rem;margin-top:.6rem;'>
                <div style='display:flex;align-items:center;justify-content:space-between;
                            margin-bottom:.4rem;'>
                    {_tag_chip(t)}
                    <span style='font-size:.65rem;color:#2D3748;font-family:"JetBrains Mono",monospace;'>{existing.get("ts","")}</span>
                </div>
                <div style='font-size:.73rem;color:#64748B;'>{existing.get("note","—") or "—"}</div>
                <div style='margin-top:.4rem;'>
                    <span style='font-size:.68rem;font-weight:700;color:{PRIO_COLORS.get(existing.get("priority","Medium"),"#F59E0B")};
                                 font-family:"JetBrains Mono",monospace;'>
                        ↑ {existing.get("priority","Medium")} priority
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        tab1, tab2, tab3 = st.tabs(["Annotated Table", "Analytics", "Export"])

        with tab1:
            # ── Filter ─────────────────────────────────────────────────
            all_tags = sorted(set(v.get("tag","") for v in ann_store.values() if v.get("tag")))
            filter_tag = st.selectbox(
                "Filter by tag",
                ["All"] + all_tags,
                key="ann_filter"
            )

            # Build display df
            disp_df = df.copy()
            disp_df.insert(0, "_tag", "")
            disp_df.insert(1, "_priority", "")
            disp_df.insert(2, "_note", "")
            for idx, meta in ann_store.items():
                if idx < len(disp_df):
                    disp_df.at[idx, "_tag"]      = meta.get("tag", "")
                    disp_df.at[idx, "_priority"]  = meta.get("priority", "")
                    disp_df.at[idx, "_note"]      = meta.get("note", "")

            disp_df.index.name = "Row #"

            if filter_tag != "All":
                disp_df = disp_df[disp_df["_tag"] == filter_tag]
            else:
                # Sort annotated rows to top
                disp_df = pd.concat([
                    disp_df[disp_df["_tag"] != ""],
                    disp_df[disp_df["_tag"] == ""],
                ])

            show_only_ann = st.checkbox("Show annotated rows only", value=False, key="ann_only")
            if show_only_ann:
                disp_df = disp_df[disp_df["_tag"] != ""]

            n_showing = len(disp_df)
            st.markdown(f"""<div style='font-size:.73rem;color:#4A5568;margin-bottom:.4rem;
                            font-family:"JetBrains Mono",monospace;'>
                            Showing <span style='color:#A0AEC0;'>{n_showing:,}</span> rows
                            {"· <span style='color:#00D4FF;'>" + str(filter_tag) + "</span>" if filter_tag != "All" else ""}
                            </div>""", unsafe_allow_html=True)

            st.dataframe(
                disp_df.rename(columns={"_tag":"Tag","_priority":"Priority","_note":"Note"}),
                use_container_width=True,
                height=500,
                column_config={
                    "Tag":      st.column_config.TextColumn("Tag", width="small"),
                    "Priority": st.column_config.TextColumn("Priority", width="small"),
                    "Note":     st.column_config.TextColumn("Note", width="medium"),
                },
            )

        with tab2:
            if not ann_store:
                st.markdown("""
                <div style='text-align:center;padding:3rem;
                            border:1px dashed rgba(0,212,255,0.12);border-radius:14px;
                            color:#4A5568;'>
                    <div style='font-size:2rem;opacity:.25;margin-bottom:.6rem;'>✦</div>
                    No annotations yet — start tagging rows on the left.
                </div>""", unsafe_allow_html=True)
            else:
                # Tag distribution
                tag_df = pd.DataFrame([
                    {"Tag": v["tag"], "Priority": v.get("priority","Medium")}
                    for v in ann_store.values() if v.get("tag")
                ])
                NEON = ["#00D4FF","#A855F7","#FF006E","#10B981","#F59E0B","#0EA5E9","#EF4444","#64748B"]

                c1a, c2a = st.columns(2)
                with c1a:
                    tc = tag_df["Tag"].value_counts().reset_index()
                    tc.columns = ["Tag","Count"]
                    fig1 = px.pie(tc, names="Tag", values="Count", hole=0.48,
                                  template="plotly_dark", title="Tag Distribution",
                                  color_discrete_sequence=NEON)
                    fig1.update_layout(height=300, **_PLOTLY_DARK)
                    st.plotly_chart(fig1, use_container_width=True)

                with c2a:
                    pc = tag_df["Priority"].value_counts().reset_index()
                    pc.columns = ["Priority","Count"]
                    PRIO_ORDER = ["Critical","High","Medium","Low"]
                    PRIO_CLR   = {"Critical":"#EF4444","High":"#FF006E","Medium":"#F59E0B","Low":"#64748B"}
                    pc["Priority"] = pd.Categorical(pc["Priority"], categories=PRIO_ORDER, ordered=True)
                    pc = pc.sort_values("Priority")
                    fig2 = px.bar(pc, x="Priority", y="Count",
                                  color="Priority",
                                  color_discrete_map=PRIO_CLR,
                                  template="plotly_dark", title="Priority Breakdown",
                                  text_auto=True)
                    fig2.update_layout(height=300, showlegend=False, **_PLOTLY_DARK)
                    st.plotly_chart(fig2, use_container_width=True)

                # Tag × Priority heatmap
                if tag_df["Tag"].nunique() > 1 and tag_df["Priority"].nunique() > 1:
                    pivot = tag_df.groupby(["Tag","Priority"]).size().unstack(fill_value=0)
                    fig3 = px.imshow(pivot, text_auto=True, aspect="auto",
                                     color_continuous_scale=["#0D1526","#7C3AED","#00D4FF"],
                                     template="plotly_dark",
                                     title="Tag × Priority Heatmap")
                    fig3.update_layout(height=280, **_PLOTLY_DARK)
                    st.plotly_chart(fig3, use_container_width=True)

                # Row index scatter
                num_cols = df.select_dtypes(include="number").columns.tolist()
                if len(num_cols) >= 2 and ann_store:
                    st.markdown("<div style='margin-top:.4rem;'></div>", unsafe_allow_html=True)
                    fa1, fa2 = st.columns(2)
                    xc = fa1.selectbox("X axis", num_cols, key="ann_ax")
                    yc = fa2.selectbox("Y axis", [c for c in num_cols if c != xc] or num_cols, key="ann_ay")

                    plot_df = df[[xc, yc]].copy()
                    plot_df["_ann"] = "Unannotated"
                    plot_df["_tag"] = ""
                    for idx, meta in ann_store.items():
                        if idx < len(plot_df):
                            plot_df.at[idx, "_ann"] = "Annotated"
                            plot_df.at[idx, "_tag"] = meta.get("tag","")

                    ann_part = plot_df[plot_df["_ann"]=="Annotated"]
                    unann    = plot_df[plot_df["_ann"]=="Unannotated"]

                    fig4 = go.Figure()
                    fig4.add_trace(go.Scatter(
                        x=unann[xc], y=unann[yc],
                        mode="markers", name="Unannotated",
                        marker=dict(color="#1E293B", size=5, opacity=0.5)
                    ))
                    for tag in ann_part["_tag"].unique():
                        subset = ann_part[ann_part["_tag"]==tag]
                        clr, _ = TAG_COLORS.get(tag, TAG_COLORS["Custom"])
                        fig4.add_trace(go.Scatter(
                            x=subset[xc], y=subset[yc],
                            mode="markers", name=tag,
                            marker=dict(color=clr, size=10, symbol="diamond",
                                        line=dict(color="white",width=1))
                        ))
                    fig4.update_layout(title=f"Annotated rows — {yc} vs {xc}",
                                       height=380, template="plotly_dark",
                                       xaxis_title=xc, yaxis_title=yc,
                                       **_PLOTLY_DARK)
                    st.plotly_chart(fig4, use_container_width=True)

        with tab3:
            st.markdown("""
            <div style='background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.15);
                        border-radius:12px;padding:1rem 1.3rem;margin-bottom:1rem;
                        font-size:.83rem;color:#64748B;'>
                The export adds <b style="color:#E2E8F0;">_Tag</b>,
                <b style="color:#E2E8F0;">_Priority</b>,
                <b style="color:#E2E8F0;">_Note</b>, and
                <b style="color:#E2E8F0;">_Annotated_At</b> columns to your dataset.
                Unannotated rows have empty values in those columns.
            </div>""", unsafe_allow_html=True)

            export_df = df.copy()
            export_df["_Tag"]           = ""
            export_df["_Priority"]      = ""
            export_df["_Note"]          = ""
            export_df["_Annotated_At"]  = ""
            for idx, meta in ann_store.items():
                if idx < len(export_df):
                    export_df.at[idx, "_Tag"]          = meta.get("tag","")
                    export_df.at[idx, "_Priority"]      = meta.get("priority","")
                    export_df.at[idx, "_Note"]          = meta.get("note","")
                    export_df.at[idx, "_Annotated_At"]  = meta.get("ts","")

            c1e, c2e = st.columns(2)
            c1e.metric("Total rows",     f"{len(export_df):,}")
            c2e.metric("Annotated rows", f"{total_ann:,}")

            st.markdown("<br>", unsafe_allow_html=True)

            # CSV
            csv_bytes = export_df.to_csv(index=False).encode()
            st.download_button(
                "Download Annotated CSV",
                data=csv_bytes,
                file_name=f"{(st.session_state.filename or 'data').rsplit('.',1)[0]}_annotated.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # Annotated rows only
            ann_only_df = export_df[export_df["_Tag"] != ""]
            if not ann_only_df.empty:
                st.download_button(
                    "Download Annotated Rows Only",
                    data=ann_only_df.to_csv(index=False).encode(),
                    file_name="annotated_rows_only.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            # Preview
            st.markdown("<br><span style='color:#A0AEC0;font-weight:600;font-size:.83rem;'>Export preview</span>", unsafe_allow_html=True)
            preview_cols = ["_Tag","_Priority","_Note","_Annotated_At"] + df.columns[:4].tolist()
            st.dataframe(export_df[preview_cols].head(20), use_container_width=True)

            # Clear all
            st.markdown("---")
            st.markdown("<span style='color:#FF006E;font-size:.8rem;font-weight:600;'>Danger Zone</span>", unsafe_allow_html=True)
            if st.button("Clear All Annotations", key="ann_clear_all"):
                st.session_state[f"{_SK}store"] = {}
                st.success("All annotations cleared.")
                st.rerun()
