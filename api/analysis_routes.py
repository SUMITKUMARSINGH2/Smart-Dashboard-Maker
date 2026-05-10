from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
import json, traceback
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from api.store import get_store, set_store

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api")
PALETTE = ["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444","#8B5CF6","#06B6D4"]

def fig_json(fig):
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))

def _df(): return get_store().get("df")

# ── EDA ────────────────────────────────────────────────────────────────────────
@analysis_bp.route("/eda/correlation")
def api_corr():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    try:
        num = df.select_dtypes(include="number")
        if num.shape[1] < 2: return jsonify(error="Need 2+ numeric cols"), 400
        method = request.args.get("method","pearson")
        corr = num.corr(method=method)
        fig = go.Figure(go.Heatmap(
            z=corr.values, x=list(corr.columns), y=list(corr.columns),
            colorscale="RdBu_r", zmid=0,
            text=np.round(corr.values,2),
            texttemplate="%{text}", hovertemplate="%{x} × %{y}: %{z:.3f}<extra></extra>",
        ))
        fig.update_layout(**_layout(f"{method.title()} Correlation Matrix"))
        return jsonify(fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e)), 500

@analysis_bp.route("/eda/distribution")
def api_dist():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    col = request.args.get("col")
    bins = int(request.args.get("bins", 30))
    if not col or col not in df.columns: return jsonify(error="Bad column"), 400
    try:
        if pd.api.types.is_numeric_dtype(df[col]):
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df[col].dropna(), nbinsx=bins, name=col,
                                       marker_color=PALETTE[0], opacity=0.85))
            from scipy.stats import gaussian_kde
            s = df[col].dropna()
            if len(s) > 1:
                kde = gaussian_kde(s, bw_method="scott")
                xs = np.linspace(s.min(), s.max(), 200)
                ys = kde(xs) * len(s) * (s.max()-s.min()) / bins
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="KDE",
                                         line=dict(color=PALETTE[1], width=2)))
            fig.update_layout(**_layout(f"Distribution of {col}"))
        else:
            vc = df[col].value_counts().head(30)
            fig = go.Figure(go.Bar(x=vc.index.astype(str), y=vc.values,
                                   marker_color=PALETTE[0]))
            fig.update_layout(**_layout(f"Value Counts: {col}"))
        return jsonify(fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e)), 500

@analysis_bp.route("/eda/boxplot")
def api_box():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    cols = request.args.getlist("cols[]") or request.args.getlist("cols")
    if not cols:
        cols = df.select_dtypes(include="number").columns.tolist()[:10]
    try:
        fig = go.Figure()
        for i, c in enumerate(cols):
            fig.add_trace(go.Box(y=df[c].dropna(), name=c,
                                 marker_color=PALETTE[i % len(PALETTE)]))
        fig.update_layout(**_layout("Box Plots"))
        return jsonify(fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e)), 500

@analysis_bp.route("/eda/scatter")
def api_scatter():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    x = request.args.get("x"); y = request.args.get("y")
    color = request.args.get("color")
    if not x or not y: return jsonify(error="Provide x and y"), 400
    try:
        kwargs = dict(color=color) if color and color in df.columns else {}
        fig = px.scatter(df, x=x, y=y, **kwargs,
                         color_discrete_sequence=PALETTE,
                         trendline="ols")
        fig.update_layout(**_layout(f"{x} vs {y}"))
        return jsonify(fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e)), 500

@analysis_bp.route("/eda/hypothesis")
def api_hyp():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    col1 = request.args.get("col1"); col2 = request.args.get("col2")
    test = request.args.get("test","ttest")
    if not col1 or not col2: return jsonify(error="Provide col1 and col2"), 400
    try:
        from scipy import stats as sp
        a = df[col1].dropna(); b = df[col2].dropna()
        if test == "ttest":
            stat, pval = sp.ttest_ind(a, b)
            name = "Independent T-Test"
        elif test == "mannwhitney":
            stat, pval = sp.mannwhitneyu(a, b, alternative="two-sided")
            name = "Mann-Whitney U"
        elif test == "ks":
            stat, pval = sp.ks_2samp(a, b)
            name = "KS Test"
        elif test == "levene":
            stat, pval = sp.levene(a, b)
            name = "Levene's Test"
        else:
            stat, pval = sp.ttest_ind(a, b); name="T-Test"
        return jsonify(
            test=name, stat=float(stat), pval=float(pval),
            significant=bool(pval < 0.05),
            interpretation=(
                f"p={pval:.4f} — {'Statistically significant difference' if pval<0.05 else 'No significant difference'} at α=0.05"
            )
        )
    except Exception as e:
        return jsonify(error=str(e)), 500

# ── Time Series ────────────────────────────────────────────────────────────────
@analysis_bp.route("/timeseries/trend")
def api_ts_trend():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    date_col = request.args.get("date_col")
    val_col  = request.args.get("val_col")
    window   = int(request.args.get("window", 7))
    if not date_col or not val_col: return jsonify(error="Provide date_col and val_col"), 400
    try:
        d = df[[date_col, val_col]].copy()
        d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
        d = d.dropna().sort_values(date_col)
        d["rolling"] = d[val_col].rolling(window).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d[date_col], y=d[val_col], mode="lines",
                                 name=val_col, line=dict(color=PALETTE[0], width=1.5), opacity=0.7))
        fig.add_trace(go.Scatter(x=d[date_col], y=d["rolling"], mode="lines",
                                 name=f"{window}-period MA", line=dict(color=PALETTE[1], width=2.5)))
        fig.update_layout(**_layout(f"{val_col} Trend"))
        return jsonify(fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e)), 500

@analysis_bp.route("/timeseries/growth")
def api_ts_growth():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    date_col = request.args.get("date_col"); val_col = request.args.get("val_col")
    if not date_col or not val_col: return jsonify(error="Provide columns"), 400
    try:
        d = df[[date_col, val_col]].copy()
        d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
        d = d.dropna().sort_values(date_col)
        d["growth"] = d[val_col].pct_change() * 100
        fig = go.Figure()
        fig.add_trace(go.Bar(x=d[date_col], y=d["growth"], name="Growth %",
                             marker_color=[PALETTE[2] if v < 0 else PALETTE[0] for v in d["growth"]]))
        fig.update_layout(**_layout(f"{val_col} Period-over-Period Growth %"))
        return jsonify(fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e)), 500

@analysis_bp.route("/timeseries/decompose")
def api_ts_decompose():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    date_col = request.args.get("date_col"); val_col = request.args.get("val_col")
    period   = int(request.args.get("period", 12))
    if not date_col or not val_col: return jsonify(error="Provide columns"), 400
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
        d = df[[date_col, val_col]].copy()
        d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
        d = d.dropna().sort_values(date_col).set_index(date_col)
        result = seasonal_decompose(d[val_col], model="additive", period=period, extrapolate_trend="freq")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d.index, y=result.trend,    mode="lines", name="Trend",    line=dict(color=PALETTE[0])))
        fig.add_trace(go.Scatter(x=d.index, y=result.seasonal, mode="lines", name="Seasonal", line=dict(color=PALETTE[1])))
        fig.add_trace(go.Scatter(x=d.index, y=result.resid,    mode="lines", name="Residual", line=dict(color=PALETTE[2])))
        fig.update_layout(**_layout(f"Seasonal Decomposition of {val_col}"))
        return jsonify(fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e)), 500

# ── Outliers ───────────────────────────────────────────────────────────────────
@analysis_bp.route("/outliers/detect")
def api_outliers():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    method = request.args.get("method","iqr")
    col    = request.args.get("col")
    try:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if col and col in num_cols:
            num_cols = [col]
        results = []
        for c in num_cols:
            s = df[c].dropna()
            if method == "iqr":
                q1,q3 = s.quantile(0.25), s.quantile(0.75)
                iqr = q3-q1
                mask = (s < q1-1.5*iqr) | (s > q3+1.5*iqr)
            elif method == "zscore":
                from scipy.stats import zscore
                mask = pd.Series(np.abs(zscore(s)) > 3, index=s.index)
            elif method == "modified_z":
                med = s.median()
                mad = np.median(np.abs(s - med))
                mask = pd.Series(np.abs(0.6745*(s-med)/(mad+1e-9)) > 3.5, index=s.index)
            else:
                mask = pd.Series(False, index=s.index)
            out_idx = s[mask].index.tolist()[:100]
            results.append({
                "col": c,
                "n_outliers": int(mask.sum()),
                "pct": round(mask.mean()*100, 2),
                "lower": float(s.min()), "upper": float(s.max()),
                "sample": [float(s[i]) for i in out_idx[:20]],
            })
        # box plot
        fig = go.Figure()
        for i,c in enumerate(df.select_dtypes(include="number").columns[:10]):
            fig.add_trace(go.Box(y=df[c].dropna(), name=c, marker_color=PALETTE[i%len(PALETTE)],
                                 boxpoints="outliers"))
        fig.update_layout(**_layout(f"Outlier Detection — {method.upper()}"))
        return jsonify(results=results, fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ── Comparison ─────────────────────────────────────────────────────────────────
@analysis_bp.route("/comparison/upload", methods=["POST"])
def api_cmp_upload():
    import io
    f = request.files.get("file")
    if not f: return jsonify(error="No file"), 400
    try:
        raw = f.read(); ext = f.filename.rsplit(".",1)[-1].lower()
        if ext == "csv": df2 = pd.read_csv(io.BytesIO(raw))
        elif ext in ("xls","xlsx"): df2 = pd.read_excel(io.BytesIO(raw))
        elif ext == "json": df2 = pd.read_json(io.BytesIO(raw))
        else: return jsonify(error="Unsupported format"), 400
        set_store(cmp_df_b=df2, cmp_name_b=f.filename)
        return jsonify(ok=True, filename=f.filename, rows=df2.shape[0], cols=df2.shape[1], columns=list(df2.columns))
    except Exception as e:
        return jsonify(error=str(e)), 500

@analysis_bp.route("/comparison/stats")
def api_cmp_stats():
    store = get_store()
    df_a = store.get("df"); df_b = store.get("cmp_df_b")
    if df_a is None or df_b is None: return jsonify(error="Load both datasets"), 400
    try:
        common = list(set(df_a.select_dtypes(include="number").columns) &
                      set(df_b.select_dtypes(include="number").columns))
        stats = []
        for c in common:
            stats.append({
                "col": c,
                "mean_a": float(df_a[c].mean()), "mean_b": float(df_b[c].mean()),
                "std_a": float(df_a[c].std()),  "std_b": float(df_b[c].std()),
                "min_a": float(df_a[c].min()),  "min_b": float(df_b[c].min()),
                "max_a": float(df_a[c].max()),  "max_b": float(df_b[c].max()),
            })
        # overlap chart
        fig = go.Figure()
        for i, c in enumerate(common[:5]):
            fig.add_trace(go.Violin(y=df_a[c].dropna(), name=f"{c} (A)",
                                    side="negative", line_color=PALETTE[0]))
            fig.add_trace(go.Violin(y=df_b[c].dropna(), name=f"{c} (B)",
                                    side="positive", line_color=PALETTE[1]))
        fig.update_layout(**_layout("Distribution Comparison A vs B"))
        return jsonify(stats=stats, common_cols=common, fig=fig_json(fig),
                       shape_a=list(df_a.shape), shape_b=list(df_b.shape))
    except Exception as e:
        return jsonify(error=str(e)), 500

# ── layout helper ──────────────────────────────────────────────────────────────
def _layout(title=""):
    return dict(
        title=dict(text=title, font=dict(color="#E2E8F0", size=16)),
        paper_bgcolor="#0D1528", plot_bgcolor="#0D1528",
        font=dict(color="#94A3B8", family="Space Grotesk, sans-serif"),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
        yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")),
    )
