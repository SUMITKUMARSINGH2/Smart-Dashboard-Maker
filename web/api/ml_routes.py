from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
import json, traceback
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from api.store import get_store

ml_bp = Blueprint("ml", __name__, url_prefix="/api/ml")
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

def _df():
    return get_store().get("df")

def _num_df(df, cols=None):
    num = df.select_dtypes(include="number")
    if cols:
        num = num[[c for c in cols if c in num.columns]]
    return num.dropna()

# ── KMeans Clustering ──────────────────────────────────────────────────────────
@ml_bp.route("/kmeans", methods=["POST"])
def api_kmeans():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    k = int(body.get("k", 3))
    cols = body.get("cols") or None
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        num = _num_df(df, cols)
        if num.shape[1] < 2: return jsonify(error="Need 2+ numeric columns"), 400
        scaler = StandardScaler()
        X = scaler.fit_transform(num)
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        # Elbow data
        inertias = []
        for ki in range(1, min(11, len(num)+1)):
            inertias.append(float(KMeans(n_clusters=ki, random_state=42, n_init=5).fit(X).inertia_))

        # 2D PCA for scatter
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        reduced = pca.fit_transform(X)
        cluster_data = []
        for i in range(k):
            mask = labels == i
            cluster_data.append({
                "cluster": i, "size": int(mask.sum()),
                "x": reduced[mask, 0].tolist(),
                "y": reduced[mask, 1].tolist(),
            })

        fig = go.Figure()
        for cd in cluster_data:
            fig.add_trace(go.Scatter(
                x=cd["x"], y=cd["y"], mode="markers",
                name=f"Cluster {cd['cluster']} ({cd['size']})",
                marker=dict(color=PALETTE[cd["cluster"] % len(PALETTE)], size=6, opacity=0.75)
            ))
        fig.update_layout(**_layout(f"K-Means Clustering (k={k}) — PCA 2D"),
                          xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
                          yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"))

        # Elbow chart
        fig_elbow = go.Figure(go.Scatter(x=list(range(1,len(inertias)+1)), y=inertias,
                                          mode="lines+markers", line=dict(color=PALETTE[0])))
        fig_elbow.update_layout(**_layout("Elbow Curve"))

        cluster_col = [f"Cluster {l}" for l in labels.tolist()]
        sizes = {f"Cluster {i}": int((np.array(labels)==i).sum()) for i in range(k)}
        return jsonify(ok=True, k=k, sizes=sizes, fig=fig_json(fig),
                       fig_elbow=fig_json(fig_elbow), inertias=inertias,
                       explained_var=[round(float(v),4) for v in pca.explained_variance_ratio_])
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ── Anomaly Detection ──────────────────────────────────────────────────────────
@ml_bp.route("/anomaly", methods=["POST"])
def api_anomaly():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    contamination = float(body.get("contamination", 0.05))
    cols = body.get("cols") or None
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
        num = _num_df(df, cols)
        if num.shape[1] < 1: return jsonify(error="Need numeric columns"), 400
        X = StandardScaler().fit_transform(num)
        iso = IsolationForest(contamination=contamination, random_state=42)
        preds = iso.fit_predict(X)
        scores = iso.score_samples(X)
        n_anomalies = int((preds == -1).sum())
        # PCA for vis
        from sklearn.decomposition import PCA
        reduced = PCA(n_components=2).fit_transform(X)
        normal_mask = preds == 1
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=reduced[normal_mask,0], y=reduced[normal_mask,1],
                                 mode="markers", name="Normal",
                                 marker=dict(color=PALETTE[0], size=5, opacity=0.6)))
        fig.add_trace(go.Scatter(x=reduced[~normal_mask,0], y=reduced[~normal_mask,1],
                                 mode="markers", name="Anomaly",
                                 marker=dict(color=PALETTE[2], size=9, opacity=0.9,
                                             symbol="x", line=dict(width=1, color="white"))))
        fig.update_layout(**_layout(f"Anomaly Detection — {n_anomalies} anomalies ({contamination*100:.0f}% contamination)"),
                          xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
                          yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"))
        # score distribution
        fig_score = go.Figure(go.Histogram(x=scores, marker_color=PALETTE[1], nbinsx=40))
        fig_score.update_layout(**_layout("Anomaly Scores Distribution"))
        # anomalous rows
        anom_rows = num[preds==-1].head(50).where(pd.notnull(num[preds==-1].head(50)), None).to_dict(orient="records")
        return jsonify(ok=True, n_anomalies=n_anomalies, total=len(num),
                       pct=round(n_anomalies/len(num)*100,2),
                       fig=fig_json(fig), fig_score=fig_json(fig_score),
                       anomaly_rows=anom_rows, cols=list(num.columns))
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ── Feature Importance ─────────────────────────────────────────────────────────
@ml_bp.route("/feature-importance", methods=["POST"])
def api_feat_imp():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    target = body.get("target")
    if not target or target not in df.columns:
        return jsonify(error="Specify a valid target column"), 400
    model_type = body.get("model","rf")
    try:
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
        from sklearn.preprocessing import LabelEncoder
        num = df.select_dtypes(include="number")
        feats = [c for c in num.columns if c != target]
        if not feats: return jsonify(error="No numeric feature columns"), 400
        X = df[feats].fillna(df[feats].median())
        y_raw = df[target]
        is_cat = not pd.api.types.is_numeric_dtype(y_raw)
        if is_cat:
            le = LabelEncoder()
            y = le.fit_transform(y_raw.astype(str))
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            y = y_raw.fillna(y_raw.median())
            if model_type == "gbm":
                model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        importances = model.feature_importances_
        pairs = sorted(zip(feats, importances), key=lambda x: x[1], reverse=True)
        fig = go.Figure(go.Bar(
            x=[p[1] for p in pairs], y=[p[0] for p in pairs],
            orientation="h", marker_color=PALETTE[0],
            text=[f"{p[1]:.4f}" for p in pairs], textposition="outside"
        ))
        fig.update_layout(**_layout(f"Feature Importance → {target}"),
                          xaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"),
                          yaxis=dict(gridcolor="#1E293B", zerolinecolor="#1E293B"))
        return jsonify(ok=True, features=[{"feat":p[0],"importance":round(float(p[1]),6)} for p in pairs],
                       fig=fig_json(fig), model=model_type, target=target)
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ── PCA ────────────────────────────────────────────────────────────────────────
@ml_bp.route("/pca", methods=["POST"])
def api_pca():
    df = _df()
    if df is None: return jsonify(error="No dataset"), 400
    body = request.json or {}
    n_components = int(body.get("n_components", 3))
    try:
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        num = df.select_dtypes(include="number").dropna()
        if num.shape[1] < 2: return jsonify(error="Need 2+ numeric cols"), 400
        X = StandardScaler().fit_transform(num)
        n_components = min(n_components, num.shape[1], num.shape[0])
        pca = PCA(n_components=n_components, random_state=42)
        reduced = pca.fit_transform(X)
        # Scree plot
        fig_scree = go.Figure()
        fig_scree.add_trace(go.Bar(x=[f"PC{i+1}" for i in range(n_components)],
                                    y=pca.explained_variance_ratio_*100,
                                    marker_color=PALETTE[0], name="Explained Var %"))
        fig_scree.add_trace(go.Scatter(x=[f"PC{i+1}" for i in range(n_components)],
                                        y=np.cumsum(pca.explained_variance_ratio_)*100,
                                        mode="lines+markers", name="Cumulative", line=dict(color=PALETTE[1])))
        fig_scree.update_layout(**_layout("PCA — Explained Variance"))
        # Biplot (PC1 vs PC2)
        fig_bi = go.Figure()
        fig_bi.add_trace(go.Scatter(x=reduced[:,0], y=reduced[:,1], mode="markers",
                                     marker=dict(color=PALETTE[0], size=5, opacity=0.6), name="Samples"))
        # Loadings
        loadings = pca.components_.T
        scale = max(np.abs(reduced[:,0]).max(), np.abs(reduced[:,1]).max()) / max(np.abs(loadings).max(), 1e-9)
        for i, feat in enumerate(num.columns):
            fig_bi.add_annotation(ax=0, ay=0, x=loadings[i,0]*scale*0.7, y=loadings[i,1]*scale*0.7,
                                   xref="x", yref="y", axref="x", ayref="y",
                                   arrowhead=2, arrowcolor=PALETTE[2], arrowsize=1.5,
                                   font=dict(color=PALETTE[2], size=11), text=feat)
        fig_bi.update_layout(**_layout("PCA Biplot (PC1 vs PC2)"))
        components = []
        for i in range(n_components):
            components.append({
                "pc": f"PC{i+1}",
                "explained_var_pct": round(float(pca.explained_variance_ratio_[i])*100, 3),
                "loadings": {feat: round(float(loadings[j,i]),4) for j,feat in enumerate(num.columns)},
            })
        return jsonify(ok=True, n_components=n_components,
                       total_var_pct=round(float(pca.explained_variance_ratio_.sum())*100,2),
                       components=components, fig_scree=fig_json(fig_scree), fig_bi=fig_json(fig_bi))
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500
