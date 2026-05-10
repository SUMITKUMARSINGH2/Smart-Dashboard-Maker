from flask import Blueprint, request, jsonify, make_response
import pandas as pd
import numpy as np
import json, traceback, re, io, base64
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from api.store import get_store, set_store

features_bp = Blueprint("features", __name__, url_prefix="/api")
PALETTE = ["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444","#8B5CF6","#06B6D4"]

def fig_json(fig):
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))

def _layout(title=""):
    return dict(
        title=dict(text=title, font=dict(color="#E2E8F0", size=16)),
        paper_bgcolor="#0D1528", plot_bgcolor="#0D1528",
        font=dict(color="#94A3B8", family="Space Grotesk, sans-serif"),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8")),
    )

def _df(): return get_store().get("df")

# ══════════════════════════════════════════════════════════════════════════════
# 1. DATA FORECASTING
# ══════════════════════════════════════════════════════════════════════════════
@features_bp.route("/forecast", methods=["POST"])
def api_forecast():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    date_col  = body.get("date_col")
    val_col   = body.get("val_col")
    periods   = int(body.get("periods", 30))
    p = int(body.get("p", 1))
    d = int(body.get("d", 1))
    q = int(body.get("q", 1))
    freq      = body.get("freq", "D")
    if not date_col or not val_col:
        return jsonify(error="Provide date_col and val_col"), 400
    try:
        series_df = df[[date_col, val_col]].copy()
        series_df[date_col] = pd.to_datetime(series_df[date_col], errors="coerce")
        series_df = series_df.dropna().sort_values(date_col)
        series_df = series_df.set_index(date_col)[val_col].resample(freq).mean().interpolate()
        if len(series_df) < 10:
            return jsonify(error="Need at least 10 data points for forecasting"), 400
        from statsmodels.tsa.arima.model import ARIMA
        model = ARIMA(series_df, order=(p, d, q))
        result = model.fit()
        forecast = result.get_forecast(steps=periods)
        forecast_mean = forecast.predicted_mean
        conf_int = forecast.conf_int(alpha=0.05)
        fig = go.Figure()
        # Historical
        fig.add_trace(go.Scatter(
            x=series_df.index, y=series_df.values,
            mode="lines", name="Historical",
            line=dict(color=PALETTE[0], width=2)
        ))
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_mean.index, y=forecast_mean.values,
            mode="lines", name="Forecast",
            line=dict(color=PALETTE[2], width=2.5, dash="dash")
        ))
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=list(conf_int.index) + list(conf_int.index[::-1]),
            y=list(conf_int.iloc[:, 1]) + list(conf_int.iloc[:, 0][::-1]),
            fill="toself", fillcolor="rgba(255,0,110,0.1)",
            line=dict(color="rgba(255,0,110,0)"),
            name="95% Confidence Interval"
        ))
        fig.add_vline(x=str(series_df.index[-1]), line_dash="dot",
                      line_color=PALETTE[3], opacity=0.6)
        fig.update_layout(
            **_layout(f"ARIMA({p},{d},{q}) Forecast — {val_col}"),
            xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B",
                       rangeslider=dict(visible=True, bgcolor="#060B1A")),
            yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
        )
        # Summary stats
        summary = {
            "aic": round(float(result.aic), 2),
            "bic": round(float(result.bic), 2),
            "forecast_mean": round(float(forecast_mean.mean()), 4),
            "forecast_min": round(float(forecast_mean.min()), 4),
            "forecast_max": round(float(forecast_mean.max()), 4),
            "n_obs": len(series_df),
            "periods": periods,
        }
        return jsonify(fig=fig_json(fig), summary=summary)
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ══════════════════════════════════════════════════════════════════════════════
# 2. WHAT-IF SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
@features_bp.route("/whatif/info")
def api_whatif_info():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cols_info = []
    for c in num_cols:
        s = df[c].dropna()
        cols_info.append({
            "col": c,
            "mean": float(s.mean()),
            "std": float(s.std()),
            "min": float(s.min()),
            "max": float(s.max()),
            "q25": float(s.quantile(0.25)),
            "q75": float(s.quantile(0.75)),
        })
    return jsonify(cols=cols_info)

@features_bp.route("/whatif/simulate", methods=["POST"])
def api_whatif_simulate():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    adjustments = body.get("adjustments", {})  # {col: multiplier}
    try:
        sim_df = df.copy()
        for col, mult in adjustments.items():
            if col in sim_df.columns and pd.api.types.is_numeric_dtype(sim_df[col]):
                sim_df[col] = sim_df[col] * float(mult)
        num = sim_df.select_dtypes(include="number")
        orig_num = df.select_dtypes(include="number")
        stats = []
        for c in num.columns:
            orig_s = orig_num[c].dropna()
            sim_s  = num[c].dropna()
            delta_mean = float(sim_s.mean() - orig_s.mean())
            stats.append({
                "col": c,
                "orig_mean": round(float(orig_s.mean()), 4),
                "sim_mean":  round(float(sim_s.mean()), 4),
                "delta_mean": round(delta_mean, 4),
                "delta_pct": round((delta_mean / (orig_s.mean() + 1e-10)) * 100, 2),
                "orig_sum": round(float(orig_s.sum()), 2),
                "sim_sum":  round(float(sim_s.sum()), 2),
            })
        # Comparison bar chart
        modified_cols = list(adjustments.keys())
        if modified_cols:
            fig = go.Figure()
            for c in modified_cols[:6]:
                if c not in num.columns: continue
                orig_mean = float(df[c].dropna().mean())
                sim_mean  = float(sim_df[c].dropna().mean())
                fig.add_trace(go.Bar(name=f"{c} (original)", x=[c], y=[orig_mean],
                                     marker_color=PALETTE[0]))
                fig.add_trace(go.Bar(name=f"{c} (simulated)", x=[c], y=[sim_mean],
                                     marker_color=PALETTE[2]))
            fig.update_layout(**_layout("What-If: Original vs Simulated Means"), barmode="group")
        else:
            fig = go.Figure()
            fig.update_layout(**_layout("Adjust sliders to simulate changes"))
        return jsonify(stats=stats, fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ══════════════════════════════════════════════════════════════════════════════
# 3. REGRESSION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
@features_bp.route("/regression", methods=["POST"])
def api_regression():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    x_cols  = body.get("x_cols", [])
    y_col   = body.get("y_col")
    degree  = int(body.get("degree", 1))
    model_t = body.get("model", "linear")
    if not x_cols or not y_col:
        return jsonify(error="Provide x_cols and y_col"), 400
    try:
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.preprocessing import PolynomialFeatures, StandardScaler
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        from sklearn.model_selection import cross_val_score
        sub = df[x_cols + [y_col]].dropna()
        X = sub[x_cols].values
        y = sub[y_col].values
        # Polynomial features
        if degree > 1:
            poly = PolynomialFeatures(degree=degree, include_bias=False)
            X_feat = poly.fit_transform(X)
            feat_names = poly.get_feature_names_out(x_cols)
        else:
            X_feat = X
            feat_names = x_cols
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_feat)
        if model_t == "ridge":
            reg = Ridge(alpha=1.0)
        elif model_t == "lasso":
            reg = Lasso(alpha=0.01, max_iter=10000)
        else:
            reg = LinearRegression()
        reg.fit(X_scaled, y)
        y_pred = reg.predict(X_scaled)
        r2   = float(r2_score(y, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
        mae  = float(mean_absolute_error(y, y_pred))
        # CV score
        cv_scores = cross_val_score(reg, X_scaled, y, cv=min(5, len(sub)//2), scoring="r2")
        cv_r2 = float(cv_scores.mean())
        # Scatter: actual vs predicted
        fig_fit = go.Figure()
        fig_fit.add_trace(go.Scatter(x=y, y=y_pred, mode="markers",
                                     marker=dict(color=PALETTE[0], size=5, opacity=0.6),
                                     name="Predicted vs Actual"))
        mn, mx = float(min(y.min(), y_pred.min())), float(max(y.max(), y_pred.max()))
        fig_fit.add_trace(go.Scatter(x=[mn,mx], y=[mn,mx], mode="lines",
                                     line=dict(color=PALETTE[2], dash="dash"), name="Perfect Fit"))
        fig_fit.update_layout(**_layout("Actual vs Predicted"))
        # Residuals
        residuals = y - y_pred
        fig_res = go.Figure()
        fig_res.add_trace(go.Scatter(x=y_pred, y=residuals, mode="markers",
                                     marker=dict(color=PALETTE[1], size=5, opacity=0.6),
                                     name="Residuals"))
        fig_res.add_hline(y=0, line_dash="dot", line_color=PALETTE[3], opacity=0.7)
        fig_res.update_layout(**_layout("Residual Plot"))
        # Residuals histogram
        fig_rhist = go.Figure(go.Histogram(x=residuals, marker_color=PALETTE[2], nbinsx=30))
        fig_rhist.update_layout(**_layout("Residuals Distribution"))
        # If single X: scatter with fit line
        fig_line = None
        if len(x_cols) == 1:
            x_range = np.linspace(X[:,0].min(), X[:,0].max(), 200).reshape(-1,1)
            if degree > 1:
                x_range_feat = poly.transform(x_range)
            else:
                x_range_feat = x_range
            x_range_scaled = scaler.transform(x_range_feat)
            y_range = reg.predict(x_range_scaled)
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=X[:,0], y=y, mode="markers",
                                          marker=dict(color=PALETTE[0], size=5, opacity=0.6), name="Data"))
            fig_line.add_trace(go.Scatter(x=x_range[:,0], y=y_range, mode="lines",
                                          line=dict(color=PALETTE[2], width=2.5),
                                          name=f"Degree {degree} Fit"))
            fig_line.update_layout(**_layout(f"{x_cols[0]} → {y_col}"))
        coeff_list = []
        for name, coef in zip(feat_names, reg.coef_):
            coeff_list.append({"feature": str(name), "coefficient": round(float(coef), 6)})
        coeff_list.sort(key=lambda x: abs(x["coefficient"]), reverse=True)
        return jsonify(
            r2=round(r2, 6), rmse=round(rmse, 6), mae=round(mae, 6),
            cv_r2=round(cv_r2, 4), intercept=round(float(reg.intercept_), 6),
            n_samples=len(sub), degree=degree, model=model_t,
            coefficients=coeff_list,
            fig_fit=fig_json(fig_fit), fig_res=fig_json(fig_res),
            fig_rhist=fig_json(fig_rhist),
            fig_line=fig_json(fig_line) if fig_line else None,
        )
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ══════════════════════════════════════════════════════════════════════════════
# 4. TEXT ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
@features_bp.route("/text/analyze")
def api_text_analyze():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    col = request.args.get("col")
    if not col or col not in df.columns:
        return jsonify(error="Invalid column"), 400
    try:
        import collections
        texts = df[col].dropna().astype(str)
        # Word frequency
        all_words = []
        for t in texts:
            words = re.findall(r"\b[a-zA-Z]{3,}\b", t.lower())
            all_words.extend(words)
        STOPWORDS = {"the","and","for","are","but","not","you","all","can","had","her","was",
                     "one","our","out","day","get","has","him","his","how","its","may",
                     "new","now","old","see","two","who","boy","did","man","men","let",
                     "put","say","she","too","use","this","that","with","have","from",
                     "they","been","will","some","what","when","them","then","than",
                     "there","their","would","could","should","other","about","into",
                     "more","also","just","like","very","even","most","such","each",
                     "your","which","these","after","where","before","these","here"}
        filtered = [w for w in all_words if w not in STOPWORDS]
        counter = collections.Counter(filtered)
        top_words = [{"word": w, "count": c} for w, c in counter.most_common(30)]
        # Bar chart
        if top_words:
            fig_freq = go.Figure(go.Bar(
                x=[t["count"] for t in top_words],
                y=[t["word"] for t in top_words],
                orientation="h",
                marker_color=PALETTE[0],
            ))
            fig_freq.update_layout(**_layout(f"Word Frequency — {col}"),
                                   xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
                                   yaxis=dict(autorange="reversed", gridcolor="#1E293B", zerolinecolor="#1E293B"))
        else:
            fig_freq = go.Figure()
            fig_freq.update_layout(**_layout("No words found"))
        # Sentiment (TextBlob)
        sentiment_results = []
        try:
            from textblob import TextBlob
            for t in texts[:500]:
                blob = TextBlob(str(t))
                sentiment_results.append({
                    "polarity": round(blob.sentiment.polarity, 4),
                    "subjectivity": round(blob.sentiment.subjectivity, 4),
                })
        except Exception:
            pass
        if sentiment_results:
            polarities = [s["polarity"] for s in sentiment_results]
            pos = sum(1 for p in polarities if p > 0.05)
            neg = sum(1 for p in polarities if p < -0.05)
            neu = len(polarities) - pos - neg
            avg_polarity = round(float(np.mean(polarities)), 4)
            avg_subjectivity = round(float(np.mean([s["subjectivity"] for s in sentiment_results])), 4)
            fig_sent = go.Figure()
            fig_sent.add_trace(go.Histogram(
                x=polarities, marker_color=PALETTE[1], nbinsx=30, name="Polarity"
            ))
            fig_sent.update_layout(**_layout("Sentiment Polarity Distribution"),
                                   xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B", title="Polarity (-1=negative, 1=positive)"),
                                   yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"))
            fig_pie = go.Figure(go.Pie(
                labels=["Positive","Negative","Neutral"],
                values=[pos, neg, neu],
                marker=dict(colors=[PALETTE[3], PALETTE[2], PALETTE[0]]),
                hole=0.4
            ))
            fig_pie.update_layout(**_layout("Sentiment Distribution"))
        else:
            avg_polarity = avg_subjectivity = 0
            pos = neg = neu = 0
            fig_sent = go.Figure()
            fig_sent.update_layout(**_layout("Sentiment (TextBlob unavailable)"))
            fig_pie = go.Figure()
        # Text stats
        lengths = texts.str.len()
        word_counts = texts.str.split().str.len()
        return jsonify(
            col=col, n_texts=len(texts),
            top_words=top_words,
            total_words=len(all_words), unique_words=len(set(filtered)),
            avg_length=round(float(lengths.mean()), 1),
            avg_words=round(float(word_counts.mean()), 1),
            sentiment={"avg_polarity": avg_polarity, "avg_subjectivity": avg_subjectivity,
                       "positive": pos, "negative": neg, "neutral": neu},
            fig_freq=fig_json(fig_freq),
            fig_sent=fig_json(fig_sent),
            fig_pie=fig_json(fig_pie),
        )
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

@features_bp.route("/text/wordcloud")
def api_wordcloud():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    col = request.args.get("col")
    if not col or col not in df.columns:
        return jsonify(error="Invalid column"), 400
    try:
        from wordcloud import WordCloud
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        texts = " ".join(df[col].dropna().astype(str).tolist())
        wc = WordCloud(
            width=900, height=450, background_color="#0D1528",
            colormap="cool", max_words=150,
            collocations=False
        ).generate(texts)
        buf = io.BytesIO()
        plt.figure(figsize=(9, 4.5), facecolor="#0D1528")
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(buf, format="png", bbox_inches="tight", facecolor="#0D1528", dpi=120)
        plt.close()
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        return jsonify(image=f"data:image/png;base64,{img_b64}")
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ══════════════════════════════════════════════════════════════════════════════
# 5. DATA VALIDATION RULES
# ══════════════════════════════════════════════════════════════════════════════
@features_bp.route("/validation/rules", methods=["GET", "POST", "DELETE"])
def api_validation_rules():
    store = get_store()
    if "validation_rules" not in store:
        store["validation_rules"] = []
    rules = store["validation_rules"]
    if request.method == "GET":
        return jsonify(rules=rules)
    body = request.json or {}
    if request.method == "POST":
        rule = {
            "id": len(rules),
            "col": body.get("col", ""),
            "rule_type": body.get("rule_type", "range"),
            "min_val": body.get("min_val"),
            "max_val": body.get("max_val"),
            "pattern": body.get("pattern", ""),
            "allowed_values": body.get("allowed_values", []),
            "not_null": bool(body.get("not_null", False)),
            "label": body.get("label", ""),
        }
        rules.append(rule)
        store["validation_rules"] = rules
        return jsonify(ok=True, rule=rule)
    if request.method == "DELETE":
        rule_id = body.get("id")
        store["validation_rules"] = [r for r in rules if r["id"] != rule_id]
        return jsonify(ok=True)

@features_bp.route("/validation/check", methods=["POST"])
def api_validation_check():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    store = get_store()
    rules = store.get("validation_rules", [])
    if not rules: return jsonify(error="No rules defined"), 400
    try:
        violations = []
        summary = []
        for rule in rules:
            col = rule["col"]
            if col not in df.columns:
                summary.append({"rule": rule["label"] or col, "col": col, "violations": 0, "error": "Column not found"})
                continue
            mask = pd.Series(False, index=df.index)
            if rule["not_null"]:
                mask = mask | df[col].isna()
            if rule["rule_type"] == "range":
                if rule["min_val"] is not None:
                    try: mask = mask | (pd.to_numeric(df[col], errors="coerce") < float(rule["min_val"]))
                    except: pass
                if rule["max_val"] is not None:
                    try: mask = mask | (pd.to_numeric(df[col], errors="coerce") > float(rule["max_val"]))
                    except: pass
            elif rule["rule_type"] == "pattern":
                if rule["pattern"]:
                    mask = mask | (~df[col].astype(str).str.match(rule["pattern"], na=True))
            elif rule["rule_type"] == "allowed_values":
                if rule["allowed_values"]:
                    mask = mask | (~df[col].astype(str).isin([str(v) for v in rule["allowed_values"]]))
            n_violations = int(mask.sum())
            viol_rows = df[mask].head(10).where(pd.notnull(df[mask].head(10)), None).to_dict(orient="records")
            summary.append({
                "rule": rule.get("label") or f"{col} — {rule['rule_type']}",
                "col": col,
                "rule_type": rule["rule_type"],
                "violations": n_violations,
                "pct": round(n_violations / len(df) * 100, 2),
                "sample_rows": viol_rows,
            })
            for row in viol_rows:
                violations.append({"rule": rule.get("label") or col, "col": col, **row})
        total_violations = sum(s["violations"] for s in summary)
        # Chart
        fig = go.Figure(go.Bar(
            x=[s["rule"] for s in summary],
            y=[s["violations"] for s in summary],
            marker_color=[PALETTE[2] if s["violations"] > 0 else PALETTE[3] for s in summary],
            text=[f"{s['violations']} ({s['pct']}%)" for s in summary],
            textposition="outside"
        ))
        fig.update_layout(**_layout(f"Validation Results — {total_violations} total violations"))
        return jsonify(summary=summary, total_violations=total_violations,
                       rows_checked=len(df), fig=fig_json(fig))
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ══════════════════════════════════════════════════════════════════════════════
# 6. COLUMN CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
@features_bp.route("/calculator/evaluate", methods=["POST"])
def api_calc_evaluate():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    expr     = body.get("expr", "").strip()
    new_col  = body.get("new_col", "").strip()
    preview_only = body.get("preview_only", False)
    if not expr: return jsonify(error="Empty expression"), 400
    if not new_col: return jsonify(error="Provide a column name"), 400
    try:
        safe_locals = {c: df[c] for c in df.columns if re.match(r"^[a-zA-Z_]\w*$", c)}
        safe_locals.update({
            "log": np.log, "log10": np.log10, "log2": np.log2,
            "exp": np.exp, "sqrt": np.sqrt, "abs": np.abs,
            "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "round": np.round, "floor": np.floor, "ceil": np.ceil,
            "clip": np.clip, "power": np.power, "pi": np.pi, "e": np.e,
            "mean": np.mean, "std": np.std, "sum": np.sum,
            "min": np.minimum, "max": np.maximum,
            "where": np.where, "nan": np.nan, "inf": np.inf,
            "pd": pd, "np": np,
        })
        # Try pandas eval first (fast, safe)
        try:
            result_series = df.eval(expr)
        except Exception:
            result_series = eval(expr, {"__builtins__": {}}, safe_locals)
        if isinstance(result_series, pd.Series):
            result_series = result_series.reset_index(drop=True)
        else:
            result_series = pd.Series(result_series, index=df.index)
        preview_vals = result_series.dropna().head(20).tolist()
        preview_vals = [float(v) if isinstance(v, (np.floating, float)) else v for v in preview_vals]
        stats = {}
        if pd.api.types.is_numeric_dtype(result_series):
            s = result_series.dropna()
            stats = {
                "min": round(float(s.min()), 6) if len(s) else None,
                "max": round(float(s.max()), 6) if len(s) else None,
                "mean": round(float(s.mean()), 6) if len(s) else None,
                "std": round(float(s.std()), 6) if len(s) else None,
                "nulls": int(result_series.isna().sum()),
            }
        if not preview_only:
            df[new_col] = result_series
            set_store(df=df)
            toast_msg = f"Column '{new_col}' added successfully"
        else:
            toast_msg = "Preview computed"
        return jsonify(ok=True, msg=toast_msg, preview=preview_vals, stats=stats,
                       new_col=new_col, n_rows=len(df))
    except Exception as e:
        return jsonify(error=f"Expression error: {str(e)}"), 400

@features_bp.route("/calculator/columns")
def api_calc_cols():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    return jsonify(
        columns=list(df.columns),
        numeric_cols=df.select_dtypes(include="number").columns.tolist()
    )

# ══════════════════════════════════════════════════════════════════════════════
# 7. SQL QUERY (DuckDB)
# ══════════════════════════════════════════════════════════════════════════════
@features_bp.route("/sql/query", methods=["POST"])
def api_sql_query():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    sql = body.get("sql", "").strip()
    if not sql: return jsonify(error="Empty query"), 400
    # Block dangerous statements
    sql_upper = sql.upper()
    blocked = ["DROP ", "DELETE ", "INSERT ", "UPDATE ", "ALTER ", "CREATE ", "TRUNCATE ",
               "EXEC ", "EXECUTE ", "PRAGMA ", "ATTACH ", "DETACH "]
    for kw in blocked:
        if kw in sql_upper:
            return jsonify(error=f"Statement not allowed: {kw.strip()}. Only SELECT queries are permitted."), 400
    try:
        import duckdb
        # Register the dataframe as "data" table in an in-memory DuckDB connection
        con = duckdb.connect()
        con.register("data", df)
        result = con.execute(sql).fetchdf()
        con.close()
        columns = list(result.columns)
        # Safely convert to JSON-serialisable list of dicts
        rows = []
        for _, row in result.iterrows():
            record = {}
            for col in columns:
                val = row[col]
                if pd.isna(val) if not isinstance(val, (list, dict)) else False:
                    record[col] = None
                elif hasattr(val, "item"):  # numpy scalar
                    record[col] = val.item()
                else:
                    record[col] = val
            rows.append(record)
        numeric_cols = result.select_dtypes(include="number").columns.tolist()
        return jsonify(
            columns=columns,
            rows=rows,
            numeric_cols=numeric_cols,
            n_rows=len(rows),
            n_cols=len(columns),
        )
    except Exception as e:
        return jsonify(error=str(e)), 400
