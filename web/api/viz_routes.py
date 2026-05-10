from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
import json, traceback, re
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from api.store import get_store, set_store

viz_bp = Blueprint("viz", __name__, url_prefix="/api")
PALETTE = ["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444","#8B5CF6","#06B6D4"]

def fig_json(fig):
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))

def _df(): return get_store().get("df")

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

# ── Auto Dashboard ─────────────────────────────────────────────────────────────
@viz_bp.route("/dashboard/kpis")
def api_kpis():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    try:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        kpis = []
        for c in num_cols[:8]:
            s = df[c].dropna()
            kpis.append({
                "col": c,
                "mean": round(float(s.mean()),4) if len(s) else 0,
                "min": round(float(s.min()),4) if len(s) else 0,
                "max": round(float(s.max()),4) if len(s) else 0,
                "std": round(float(s.std()),4) if len(s) else 0,
                "missing": int(df[c].isna().sum()),
                "missing_pct": round(df[c].isna().mean()*100,1),
            })
        return jsonify(kpis=kpis, rows=len(df), cols=len(df.columns))
    except Exception as e:
        return jsonify(error=str(e)), 500

@viz_bp.route("/dashboard/charts")
def api_dash_charts():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    try:
        charts = []
        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(include="object").columns.tolist()

        # Correlation heatmap
        if len(num_cols) >= 2:
            corr = df[num_cols[:10]].corr()
            fig = go.Figure(go.Heatmap(z=corr.values, x=list(corr.columns),
                                       y=list(corr.columns), colorscale="RdBu_r", zmid=0))
            fig.update_layout(**_layout("Correlation Heatmap"))
            charts.append({"title": "Correlation Heatmap", "fig": fig_json(fig)})

        # Distribution of first numeric col
        if num_cols:
            c = num_cols[0]
            fig = go.Figure(go.Histogram(x=df[c].dropna(), marker_color=PALETTE[0], nbinsx=30))
            fig.update_layout(**_layout(f"Distribution: {c}"))
            charts.append({"title": f"Distribution: {c}", "fig": fig_json(fig)})

        # Top categorical
        if cat_cols:
            c = cat_cols[0]
            vc = df[c].value_counts().head(15)
            fig = go.Figure(go.Bar(x=vc.index.astype(str), y=vc.values, marker_color=PALETTE[1]))
            fig.update_layout(**_layout(f"Top Categories: {c}"))
            charts.append({"title": f"Top: {c}", "fig": fig_json(fig)})

        # Scatter first 2 numeric
        if len(num_cols) >= 2:
            fig = go.Figure(go.Scatter(x=df[num_cols[0]], y=df[num_cols[1]],
                                       mode="markers", marker=dict(color=PALETTE[2], opacity=0.6, size=5)))
            fig.update_layout(**_layout(f"{num_cols[0]} vs {num_cols[1]}"))
            charts.append({"title": f"{num_cols[0]} vs {num_cols[1]}", "fig": fig_json(fig)})

        # Box plots
        if num_cols:
            fig = go.Figure()
            for i, c in enumerate(num_cols[:6]):
                fig.add_trace(go.Box(y=df[c].dropna(), name=c, marker_color=PALETTE[i%len(PALETTE)]))
            fig.update_layout(**_layout("Box Plots — Numeric Columns"))
            charts.append({"title": "Box Plots", "fig": fig_json(fig)})

        # Missing values bar
        miss = df.isna().sum()
        miss = miss[miss > 0].sort_values(ascending=False)
        if len(miss):
            fig = go.Figure(go.Bar(x=miss.index.tolist(), y=miss.values.tolist(),
                                   marker_color=PALETTE[2]))
            fig.update_layout(**_layout("Missing Values by Column"))
            charts.append({"title": "Missing Values", "fig": fig_json(fig)})

        return jsonify(charts=charts)
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ── Chart Builder ──────────────────────────────────────────────────────────────
@viz_bp.route("/chart/build", methods=["POST"])
def api_chart_build():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    chart_type = body.get("type","scatter")
    x = body.get("x"); y = body.get("y"); color = body.get("color")
    size = body.get("size"); text_col = body.get("text_col")
    agg = body.get("agg","sum"); bins = int(body.get("bins",20))
    title = body.get("title", f"{chart_type.title()} Chart")
    try:
        clr_kw = dict(color=color) if color and color in df.columns else {}
        fig = None
        if chart_type == "scatter":
            fig = px.scatter(df, x=x, y=y, **clr_kw, color_discrete_sequence=PALETTE)
        elif chart_type == "line":
            fig = px.line(df, x=x, y=y, **clr_kw, color_discrete_sequence=PALETTE)
        elif chart_type == "bar":
            if agg != "none" and x and y:
                grp = df.groupby(x)[y].agg(agg).reset_index()
                fig = px.bar(grp, x=x, y=y, **clr_kw, color_discrete_sequence=PALETTE)
            else:
                fig = px.bar(df, x=x, y=y, **clr_kw, color_discrete_sequence=PALETTE)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x, nbins=bins, color_discrete_sequence=PALETTE, **clr_kw)
        elif chart_type == "box":
            fig = px.box(df, x=x, y=y, **clr_kw, color_discrete_sequence=PALETTE)
        elif chart_type == "violin":
            fig = px.violin(df, x=x, y=y, **clr_kw, color_discrete_sequence=PALETTE, box=True)
        elif chart_type == "pie":
            vc = df[x].value_counts().head(15) if x else pd.Series()
            fig = go.Figure(go.Pie(labels=vc.index.astype(str), values=vc.values,
                                   marker=dict(colors=PALETTE)))
        elif chart_type == "donut":
            vc = df[x].value_counts().head(15) if x else pd.Series()
            fig = go.Figure(go.Pie(labels=vc.index.astype(str), values=vc.values, hole=0.4,
                                   marker=dict(colors=PALETTE)))
        elif chart_type == "heatmap":
            num = df.select_dtypes(include="number")
            corr = num.corr()
            fig = go.Figure(go.Heatmap(z=corr.values, x=list(corr.columns),
                                       y=list(corr.columns), colorscale="RdBu_r", zmid=0))
        elif chart_type == "bubble":
            sz = df[size] if size and size in df.columns else None
            fig = px.scatter(df, x=x, y=y, size=sz, **clr_kw, color_discrete_sequence=PALETTE)
        elif chart_type == "area":
            fig = px.area(df, x=x, y=y, **clr_kw, color_discrete_sequence=PALETTE)
        elif chart_type == "funnel":
            if x and y:
                fig = go.Figure(go.Funnel(y=df[x].astype(str), x=df[y],
                                          marker=dict(color=PALETTE)))
        elif chart_type == "treemap":
            if x and y:
                grp = df.groupby(x)[y].sum().reset_index()
                fig = px.treemap(grp, path=[x], values=y, color_discrete_sequence=PALETTE)
        elif chart_type == "sunburst":
            if x and y:
                grp = df.groupby(x)[y].sum().reset_index()
                fig = px.sunburst(grp, path=[x], values=y, color_discrete_sequence=PALETTE)
        elif chart_type == "strip":
            fig = px.strip(df, x=x, y=y, **clr_kw, color_discrete_sequence=PALETTE)
        elif chart_type == "ecdf":
            fig = px.ecdf(df, x=x, color_discrete_sequence=PALETTE)
        elif chart_type == "hexbin":
            if x and y:
                fig = go.Figure(go.Histogram2dContour(x=df[x], y=df[y],
                                                       colorscale="Blues"))
        elif chart_type == "density":
            if x and y:
                fig = px.density_heatmap(df, x=x, y=y, color_continuous_scale="Blues")
        elif chart_type == "waterfall":
            if x and y:
                fig = go.Figure(go.Waterfall(x=df[x].astype(str).tolist(), y=df[y].tolist(),
                                             connector={"line":{"color":PALETTE[0]}}))
        elif chart_type == "gauge":
            if y and y in df.columns:
                val = float(df[y].mean())
                fig = go.Figure(go.Indicator(mode="gauge+number", value=val,
                    gauge=dict(axis=dict(range=[float(df[y].min()), float(df[y].max())]),
                               bar=dict(color=PALETTE[0]))))
        if fig is None:
            return jsonify(error="Unsupported chart type or missing columns"), 400
        fig.update_layout(**_layout(title))
        return jsonify(fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ── NLQ ────────────────────────────────────────────────────────────────────────
@viz_bp.route("/nlq/query", methods=["POST"])
def api_nlq():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    q = body.get("query","").lower().strip()
    if not q: return jsonify(error="Empty query"), 400
    try:
        result = _nlq_engine(df, q)
        return jsonify(result)
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

def _nlq_engine(df, q):
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    all_cols = list(df.columns)

    def find_col(text):
        for c in all_cols:
            if c.lower() in text:
                return c
        return None

    def find_num_col(text):
        for c in num_cols:
            if c.lower() in text:
                return c
        return num_cols[0] if num_cols else None

    # show top N
    m = re.search(r"show\s+(top|first|last)\s*(\d+)", q)
    if m:
        n = int(m.group(2))
        if "last" in q:
            sub = df.tail(n)
        else:
            col = find_num_col(q)
            if col and ("top" in q or "highest" in q or "most" in q):
                sub = df.nlargest(n, col)
            else:
                sub = df.head(n)
        return {"type":"table","answer":f"Showing {n} rows","data":sub.where(pd.notnull(sub),None).head(n).to_dict(orient="records"),"cols":list(sub.columns)}

    # count
    if re.search(r"\bhow many\b|\bcount\b|\bnumber of\b", q):
        col = find_col(q)
        val_m = re.search(r"(?:where|with|that (?:are|is|have)|is|are)\s+(.+?)(?:\?|$)", q)
        if col and val_m:
            val = val_m.group(1).strip().strip("'\"")
            cnt = int((df[col].astype(str).str.lower() == val.lower()).sum())
            return {"type":"scalar","answer":f"Count where {col}={val}: {cnt:,}","value":cnt}
        return {"type":"scalar","answer":f"Total rows: {len(df):,}","value":len(df)}

    # average / mean
    m = re.search(r"\b(average|avg|mean)\b", q)
    if m:
        col = find_num_col(q)
        if col:
            val = float(df[col].mean())
            return {"type":"scalar","answer":f"Average {col}: {val:,.4f}","value":val}

    # max / highest
    if re.search(r"\b(max|maximum|highest|largest|biggest)\b", q):
        col = find_num_col(q)
        if col:
            val = float(df[col].max())
            return {"type":"scalar","answer":f"Max {col}: {val:,.4f}","value":val}

    # min / lowest
    if re.search(r"\b(min|minimum|lowest|smallest)\b", q):
        col = find_num_col(q)
        if col:
            val = float(df[col].min())
            return {"type":"scalar","answer":f"Min {col}: {val:,.4f}","value":val}

    # sum / total
    if re.search(r"\b(sum|total|summ?ation)\b", q):
        col = find_num_col(q)
        if col:
            val = float(df[col].sum())
            return {"type":"scalar","answer":f"Sum of {col}: {val:,.4f}","value":val}

    # correlation
    if re.search(r"\bcorrelat\b", q):
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            pairs = []
            for i in range(len(num_cols)):
                for j in range(i+1, len(num_cols)):
                    pairs.append({"col1":num_cols[i],"col2":num_cols[j],"r":round(float(corr.iloc[i,j]),4)})
            pairs.sort(key=lambda x:abs(x["r"]), reverse=True)
            return {"type":"correlation","answer":f"Top correlations","pairs":pairs[:10]}

    # distribution / histogram
    if re.search(r"\bdistribution\b|\bhistogram\b", q):
        col = find_num_col(q)
        if col:
            fig = go.Figure(go.Histogram(x=df[col].dropna(), marker_color=PALETTE[0]))
            fig.update_layout(**_layout(f"Distribution of {col}"))
            return {"type":"chart","answer":f"Distribution of {col}","fig":fig_json(fig)}

    # group by
    m = re.search(r"group\s+by\s+(\w+)", q)
    if m:
        grp_col = None
        for c in all_cols:
            if c.lower() == m.group(1).lower():
                grp_col = c
                break
        if grp_col and num_cols:
            num_col = find_num_col(q) or num_cols[0]
            result = df.groupby(grp_col)[num_col].mean().reset_index().round(4)
            return {"type":"table","answer":f"Group by {grp_col}","data":result.to_dict(orient="records"),"cols":list(result.columns)}

    # unique / distinct
    if re.search(r"\bunique\b|\bdistinct\b", q):
        col = find_col(q)
        if col:
            vals = df[col].dropna().unique().tolist()[:50]
            return {"type":"list","answer":f"Unique values in {col} ({len(vals)} shown)","values":[str(v) for v in vals]}

    # missing
    if re.search(r"\bmissing\b|\bnull\b|\bnan\b|\bna\b", q):
        miss = df.isna().sum()
        miss = miss[miss>0].sort_values(ascending=False)
        data = [{"col":c,"missing":int(v),"pct":round(v/len(df)*100,2)} for c,v in miss.items()]
        return {"type":"table","answer":f"{miss.sum()} missing values found","data":data,"cols":["col","missing","pct"]}

    # outliers
    if re.search(r"\boutlier\b", q):
        col = find_num_col(q)
        if col:
            s = df[col].dropna()
            q1,q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3-q1
            mask = (s < q1-1.5*iqr) | (s > q3+1.5*iqr)
            cnt = int(mask.sum())
            return {"type":"scalar","answer":f"{cnt} outliers in {col} (IQR method)","value":cnt}

    # fallback: summary stats
    if num_cols:
        desc = df[num_cols[:5]].describe().round(4)
        return {"type":"table","answer":"Summary statistics","data":desc.reset_index().to_dict(orient="records"),"cols":["index"]+num_cols[:5]}

    return {"type":"text","answer":"I couldn't interpret that query. Try: 'show top 10', 'average of <col>', 'count rows where <col> is <val>', 'correlation', 'distribution of <col>'"}

def fig_json(fig):
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))

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

# ── Live Feed ──────────────────────────────────────────────────────────────────
@viz_bp.route("/live/connect", methods=["POST"])
def api_live_connect():
    body = request.json or {}
    url = body.get("url","")
    interval = int(body.get("interval", 30))
    set_store(live_url=url, live_interval=interval, live_connected=True,
              live_history=[], live_paused=False, live_fetch_count=0)
    return jsonify(ok=True)

@viz_bp.route("/live/fetch")
def api_live_fetch():
    import requests as req, time, io
    store = get_store()
    if not store.get("live_connected"): return jsonify(error="Not connected"), 400
    if store.get("live_paused"): return jsonify(paused=True)
    url = store.get("live_url","")
    try:
        resp = req.get(url, timeout=10)
        ct = resp.headers.get("content-type","")
        if "json" in ct:
            data = resp.json()
            if isinstance(data, list): df = pd.DataFrame(data)
            elif isinstance(data, dict): df = pd.DataFrame([data])
            else: df = pd.DataFrame()
        elif "csv" in ct or url.endswith(".csv"):
            df = pd.read_csv(io.StringIO(resp.text))
        else:
            df = pd.DataFrame()
        store["live_fetch_count"] = store.get("live_fetch_count",0)+1
        store["live_last_fetch"] = time.time()
        store["live_df"] = df
        hist = store.get("live_history",[])
        if len(df) and "timestamp" not in df.columns:
            df.insert(0,"_fetch_ts", pd.Timestamp.now().isoformat())
        hist.append(df)
        store["live_history"] = hist[-100:]
        rows = df.where(pd.notnull(df),None).head(50).to_dict(orient="records") if len(df) else []
        return jsonify(ok=True, rows=rows, cols=list(df.columns), fetch_count=store["live_fetch_count"], ts=store["live_last_fetch"])
    except Exception as e:
        return jsonify(error=str(e)), 500

@viz_bp.route("/live/pause", methods=["POST"])
def api_live_pause():
    store = get_store()
    store["live_paused"] = not store.get("live_paused", False)
    return jsonify(paused=store["live_paused"])

@viz_bp.route("/live/disconnect", methods=["POST"])
def api_live_disconnect():
    set_store(live_connected=False, live_url="", live_history=[], live_df=None, live_fetch_count=0)
    return jsonify(ok=True)
