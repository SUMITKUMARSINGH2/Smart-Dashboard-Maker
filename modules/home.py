import streamlit as st


def home_page():
    # ── Animated Hero ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.6; }
        50%       { opacity: 1; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50%       { transform: translateY(-6px); }
    }
    @keyframes shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    .hero-wrap {
        position: relative;
        background: linear-gradient(135deg, rgba(0,212,255,0.05) 0%, rgba(124,58,237,0.08) 50%, rgba(255,0,110,0.04) 100%);
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-bottom: 1.8rem;
        overflow: hidden;
    }
    .hero-wrap::before {
        content: '';
        position: absolute;
        top: -50%; right: -20%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(0,212,255,0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-wrap::after {
        content: '';
        position: absolute;
        bottom: -30%; left: 10%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-eyebrow {
        font-size: .62rem; font-weight: 600; letter-spacing: .2em;
        text-transform: uppercase; color: #00D4FF; margin-bottom: .7rem;
        font-family: 'JetBrains Mono', monospace;
        animation: pulse-glow 3s ease-in-out infinite;
    }
    .hero-title {
        font-size: 2.6rem; font-weight: 700; color: #F0F6FF;
        line-height: 1.1; margin: 0 0 1rem;
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -.02em;
    }
    .hero-gradient {
        background: linear-gradient(135deg, #00D4FF, #7C3AED, #FF006E);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
    }
    .hero-desc {
        color: #64748B; font-size: .9rem; line-height: 1.7;
        max-width: 580px; margin: 0 0 1.5rem;
    }
    .hero-badge {
        display: inline-flex; align-items: center; gap: 5px;
        border-radius: 20px; padding: .25rem .8rem;
        font-size: .72rem; font-weight: 600;
        border: 1px solid; margin: 3px;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: .02em;
    }
    .stat-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px; padding: 1.2rem 1rem;
        text-align: center;
        transition: all .2s ease;
    }
    .stat-card:hover {
        border-color: rgba(0,212,255,0.25);
        background: rgba(0,212,255,0.04);
        transform: translateY(-2px);
    }
    .stat-val {
        font-size: 2rem; font-weight: 700; line-height: 1;
        font-family: 'Space Grotesk', sans-serif;
    }
    .stat-lbl {
        font-size: .7rem; font-weight: 600; margin-top: 4px;
        text-transform: uppercase; letter-spacing: .08em;
        font-family: 'JetBrains Mono', monospace;
    }
    .feat-card {
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px; padding: 1.2rem 1.3rem;
        margin-bottom: 1rem;
        transition: all .2s ease;
        position: relative;
        overflow: hidden;
    }
    .feat-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
    }
    .feat-card:hover {
        border-color: rgba(255,255,255,0.12);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .feat-title {
        font-weight: 700; color: #E2E8F0; font-size: .88rem;
        margin-bottom: .35rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    .feat-desc { color: #64748B; font-size: .79rem; line-height: 1.55; }
    .feat-icon {
        width: 32px; height: 32px; border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: .9rem; margin-bottom: .7rem;
    }
    .section-label {
        font-size: .62rem; font-weight: 600; letter-spacing: .15em;
        text-transform: uppercase; color: #00D4FF; margin-bottom: .4rem;
        font-family: 'JetBrains Mono', monospace;
    }
    .section-title {
        font-size: 1.35rem; font-weight: 700; color: #F0F6FF;
        margin: .2rem 0 .5rem;
        font-family: 'Space Grotesk', sans-serif; letter-spacing: -.01em;
    }
    .section-bar {
        width: 32px; height: 2px; margin-bottom: 1.2rem;
        background: linear-gradient(90deg, #00D4FF, #7C3AED);
        border-radius: 2px;
    }
    .cta-btn {
        display: inline-block;
        background: linear-gradient(135deg, #0EA5E9, #7C3AED);
        color: white; font-weight: 700; font-size: .84rem;
        padding: .65rem 1.6rem; border-radius: 9px;
        cursor: pointer; text-decoration: none;
        box-shadow: 0 0 20px rgba(0,212,255,0.2);
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: .02em;
        transition: all .2s;
    }
    .cta-btn:hover {
        box-shadow: 0 0 35px rgba(0,212,255,0.35);
        transform: translateY(-1px);
    }
    </style>

    <div class="hero-wrap">
        <div class="hero-eyebrow">// Professional Data Analytics Platform</div>
        <h1 class="hero-title">
            Turn Raw Data Into<br>
            <span class="hero-gradient">Actionable Intelligence</span>
        </h1>
        <p class="hero-desc">
            Upload CSV, Excel, JSON or Parquet · Auto-profile & clean your data ·
            Build 19+ interactive charts · Run ML clustering, anomaly detection & PCA ·
            Export to Excel, Power BI, or standalone HTML reports.
        </p>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:1.5rem;">
            <span class="hero-badge" style="color:#00D4FF;border-color:rgba(0,212,255,0.3);background:rgba(0,212,255,0.07);">◎ 4+ File Formats</span>
            <span class="hero-badge" style="color:#A855F7;border-color:rgba(168,85,247,0.3);background:rgba(168,85,247,0.07);">▦ 19+ Chart Types</span>
            <span class="hero-badge" style="color:#10B981;border-color:rgba(16,185,129,0.3);background:rgba(16,185,129,0.07);">⬡ Power BI Export</span>
            <span class="hero-badge" style="color:#F59E0B;border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.07);">◈ ML Insights</span>
            <span class="hero-badge" style="color:#FF006E;border-color:rgba(255,0,110,0.3);background:rgba(255,0,110,0.07);">◐ Ask Your Data</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row ──────────────────────────────────────────────────────────────
    stats = [
        ("#00D4FF", "19+", "Chart Types"),
        ("#A855F7", "8+",  "Clean Tools"),
        ("#10B981", "4",   "Export Formats"),
        ("#FF006E", "ML",  "AI Insights"),
    ]
    cols = st.columns(4)
    for col, (color, val, lbl) in zip(cols, stats):
        col.markdown(f"""
        <div class="stat-card">
            <div class="stat-val" style="color:{color};">{val}</div>
            <div class="stat-lbl" style="color:{color};opacity:.7;">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)

    # ── Feature grid ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">What's inside</div>
    <div class="section-title">Ten powerful modules</div>
    <div class="section-bar"></div>
    """, unsafe_allow_html=True)

    features = [
        ("#00D4FF", "rgba(0,212,255,0.12)", "⬡", "Upload Data",
         "CSV, Excel, JSON, Parquet. Auto type detection, inline preview, quick summary stats."),
        ("#A855F7", "rgba(168,85,247,0.12)", "◎", "Data Profiling",
         "Full per-column profile: missing %, skewness, kurtosis, unique counts, memory usage."),
        ("#10B981", "rgba(16,185,129,0.12)", "✦", "Data Cleaning",
         "Remove duplicates, fill nulls (mean/median/mode/interpolate), outlier IQR & Z-Score removal."),
        ("#F59E0B", "rgba(245,158,11,0.12)", "∿", "EDA & Statistics",
         "Correlation heatmaps, distributions, pair plots, t-test, ANOVA, chi-square hypothesis tests."),
        ("#0EA5E9", "rgba(14,165,233,0.12)", "▦", "Chart Builder",
         "19 Plotly chart types. Full parameter control. One-click HTML export + copy Python code."),
        ("#8B5CF6", "rgba(139,92,246,0.12)", "⚡", "Auto Dashboard",
         "Auto-generates KPI cards, correlation matrix, bar charts, box plots and pivot heatmaps."),
        ("#FF006E", "rgba(255,0,110,0.12)", "⏱", "Time Series",
         "Auto-detect dates. Trend lines, rolling averages, seasonality, growth rate analysis."),
        ("#14B8A6", "rgba(20,184,166,0.12)", "◈", "ML Insights",
         "K-Means clustering, Isolation Forest anomaly detection, feature importance, PCA viz."),
        ("#F97316", "rgba(249,115,22,0.12)", "↓", "Export & Reports",
         "CSV, Excel, JSON, Parquet. Chart HTML export. Power BI Excel + M Query + DAX bundle."),
    ]

    c1, c2, c3 = st.columns(3)
    cols_list = [c1, c2, c3]
    for i, (color, bg, icon, title, desc) in enumerate(features):
        cols_list[i % 3].markdown(f"""
        <div class="feat-card" style="border-top:2px solid {color}20;">
            <div class="feat-icon" style="background:{bg};color:{color};">{icon}</div>
            <div class="feat-title">{title}</div>
            <div class="feat-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

    # ── CTA ────────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(0,212,255,0.05),rgba(124,58,237,0.07));
                border:1px solid rgba(0,212,255,0.12);border-radius:16px;
                padding:1.8rem 2rem;text-align:center;margin-top:.5rem;'>
        <div style='font-size:.65rem;font-weight:600;letter-spacing:.15em;color:#00D4FF;
                    text-transform:uppercase;margin-bottom:.6rem;font-family:"JetBrains Mono",monospace;'>
            Get Started
        </div>
        <div style='font-size:1.1rem;font-weight:700;color:#F0F6FF;margin-bottom:.4rem;
                    font-family:"Space Grotesk",sans-serif;'>
            Ready to explore your data?
        </div>
        <div style='color:#64748B;font-size:.85rem;'>
            Click <b style="color:#00D4FF;">Upload Data</b> in the sidebar to load your first dataset.
            Your data stays in your session — never saved or shared.
        </div>
    </div>
    """, unsafe_allow_html=True)
