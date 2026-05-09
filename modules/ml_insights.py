import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io

# lazy imports to avoid slow startup
def _sklearn():
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest, RandomForestRegressor, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.metrics import silhouette_score
    return KMeans, IsolationForest, RandomForestRegressor, RandomForestClassifier, StandardScaler, PCA, silhouette_score


def _ph(title, sub):
    st.markdown(f"""
    <div class='ph-wrap'>
        <div class='ph-eyebrow'>Machine Learning</div>
        <h2 class='ph-title'>{title}</h2>
        <div class='ph-bar'></div>
        <p class='ph-sub'>{sub}</p>
    </div>""", unsafe_allow_html=True)


def ml_insights_page():
    _ph("ML Insights",
        "Clustering · Anomaly Detection · Feature Importance · PCA — all without writing code")

    if st.session_state.df is None:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state.df
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if len(num_cols) < 2:
        st.info("Need at least 2 numeric columns for ML analysis.")
        return

    KMeans, IsolationForest, RFR, RFC, StandardScaler, PCA, silhouette_score = _sklearn()

    LAYOUT = dict(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFAF9",
        font=dict(family="Plus Jakarta Sans", color="#374151"),
        title_font=dict(size=14, color="#1C1917", family="Plus Jakarta Sans"),
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "K-Means Clustering", "Anomaly Detection", "Feature Importance", "PCA Explorer"
    ])

    # ── TAB 1 : K-Means Clustering ────────────────────────────────────────
    with tab1:
        st.markdown("""
        <div style='background:#F5F3FF;border-radius:12px;padding:1rem 1.3rem;
                    margin-bottom:1rem;border-left:4px solid #7C3AED;'>
            <b style='color:#5B21B6;'>K-Means Clustering</b>
            <span style='color:#6B7280;font-size:.85rem;'> — Groups similar rows into clusters based on numeric features</span>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        feat_cols = c1.multiselect("Feature columns", num_cols,
                                    default=num_cols[:min(4, len(num_cols))],
                                    key="km_feat")
        k = c2.slider("Number of clusters (K)", 2, 10, 3)
        scale = c3.checkbox("Standardize features", True, key="km_scale")

        if feat_cols and len(feat_cols) >= 2:
            data = df[feat_cols].dropna()

            if st.button("Run Clustering", key="km_run"):
                with st.spinner("Running K-Means…"):
                    X = data.values
                    if scale:
                        sc = StandardScaler()
                        X = sc.fit_transform(X)

                    km = KMeans(n_clusters=k, random_state=42, n_init=10)
                    labels = km.fit_predict(X)
                    data = data.copy()
                    data["Cluster"] = labels.astype(str)

                    sil = silhouette_score(X, labels)

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Clusters", k)
                    m2.metric("Silhouette Score", f"{sil:.4f}")
                    m3.metric("Rows clustered", f"{len(data):,}")

                    # Scatter (first 2 features)
                    fig = px.scatter(
                        data, x=feat_cols[0], y=feat_cols[1],
                        color="Cluster",
                        title=f"K-Means Clusters (k={k}) — {feat_cols[0]} vs {feat_cols[1]}",
                        template="plotly_white",
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        opacity=0.75,
                    )
                    fig.update_layout(height=460, **LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

                    # Cluster sizes
                    vc = data["Cluster"].value_counts().reset_index()
                    vc.columns = ["Cluster", "Count"]
                    fig2 = px.bar(vc, x="Cluster", y="Count",
                                  color="Cluster", template="plotly_white",
                                  title="Cluster Sizes",
                                  color_discrete_sequence=px.colors.qualitative.Bold,
                                  text_auto=True)
                    fig2.update_layout(height=320, showlegend=False, **LAYOUT)
                    st.plotly_chart(fig2, use_container_width=True)

                    # Cluster stats
                    st.markdown("**Cluster Means**")
                    st.dataframe(data.groupby("Cluster")[feat_cols].mean().round(3),
                                 use_container_width=True)

                    # Elbow chart
                    st.markdown("**Elbow Curve (optimal K finder)**")
                    inertias = []
                    ks = range(2, min(11, len(data)))
                    for ki in ks:
                        inertias.append(KMeans(n_clusters=ki, random_state=42, n_init=10).fit(X).inertia_)
                    fig3 = px.line(x=list(ks), y=inertias, markers=True,
                                   labels={"x": "K", "y": "Inertia"},
                                   title="Elbow Curve — choose K at the 'elbow'",
                                   template="plotly_white",
                                   color_discrete_sequence=["#7C3AED"])
                    fig3.add_vline(x=k, line_dash="dash", line_color="#F43F5E",
                                   annotation_text=f"Selected K={k}")
                    fig3.update_layout(height=320, **LAYOUT)
                    st.plotly_chart(fig3, use_container_width=True)

                    # Download labelled data
                    out = df.copy()
                    out.loc[data.index, "Cluster"] = labels
                    csv = out.to_csv(index=False)
                    st.download_button("Download Clustered Data (CSV)", csv.encode(),
                                       file_name="clustered_data.csv", mime="text/csv")

    # ── TAB 2 : Anomaly Detection ─────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style='background:#FFF1F2;border-radius:12px;padding:1rem 1.3rem;
                    margin-bottom:1rem;border-left:4px solid #F43F5E;'>
            <b style='color:#9F1239;'>Isolation Forest</b>
            <span style='color:#6B7280;font-size:.85rem;'> — Detects unusual rows that don't fit the normal data pattern</span>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        feat_cols_a = c1.multiselect("Feature columns", num_cols,
                                      default=num_cols[:min(4, len(num_cols))],
                                      key="iso_feat")
        contamination = c2.slider("Expected anomaly % (contamination)", 1, 20, 5)

        if feat_cols_a:
            if st.button("Detect Anomalies", key="iso_run"):
                with st.spinner("Running Isolation Forest…"):
                    data_a = df[feat_cols_a].dropna()
                    sc = StandardScaler()
                    X_a = sc.fit_transform(data_a)

                    iso = IsolationForest(contamination=contamination/100,
                                         random_state=42, n_jobs=-1)
                    preds = iso.fit_predict(X_a)
                    scores = iso.score_samples(X_a)

                    data_a = data_a.copy()
                    data_a["Anomaly"] = np.where(preds == -1, "Anomaly", "Normal")
                    data_a["Anomaly Score"] = scores

                    n_anomalies = (preds == -1).sum()
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Anomalies found", f"{n_anomalies:,}")
                    m2.metric("Normal rows", f"{len(data_a) - n_anomalies:,}")
                    m3.metric("Anomaly rate", f"{n_anomalies/len(data_a)*100:.1f}%")

                    # Scatter of first 2 features
                    fig = px.scatter(
                        data_a, x=feat_cols_a[0],
                        y=feat_cols_a[1] if len(feat_cols_a) > 1 else feat_cols_a[0],
                        color="Anomaly",
                        color_discrete_map={"Normal": "#7C3AED", "Anomaly": "#F43F5E"},
                        title="Anomaly Detection Results",
                        template="plotly_white", opacity=0.75,
                        hover_data=["Anomaly Score"],
                    )
                    fig.update_layout(height=460, **LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

                    # Score distribution
                    fig2 = px.histogram(data_a, x="Anomaly Score", color="Anomaly",
                                        nbins=50, barmode="overlay", opacity=0.75,
                                        template="plotly_white",
                                        color_discrete_map={"Normal":"#7C3AED","Anomaly":"#F43F5E"},
                                        title="Anomaly Score Distribution")
                    fig2.update_layout(height=320, **LAYOUT)
                    st.plotly_chart(fig2, use_container_width=True)

                    st.markdown("**Anomalous Rows (sample)**")
                    anomaly_rows = df.loc[data_a[data_a["Anomaly"] == "Anomaly"].index].head(20)
                    st.dataframe(anomaly_rows, use_container_width=True)

                    csv = df.copy()
                    csv.loc[data_a.index, "Anomaly"] = data_a["Anomaly"].values
                    csv.loc[data_a.index, "Anomaly Score"] = data_a["Anomaly Score"].values
                    st.download_button("Download with Anomaly Labels (CSV)",
                                       csv.to_csv(index=False).encode(),
                                       file_name="anomaly_labels.csv", mime="text/csv")

    # ── TAB 3 : Feature Importance ───────────────────────────────────────
    with tab3:
        st.markdown("""
        <div style='background:#ECFDF5;border-radius:12px;padding:1rem 1.3rem;
                    margin-bottom:1rem;border-left:4px solid #059669;'>
            <b style='color:#065F46;'>Random Forest Feature Importance</b>
            <span style='color:#6B7280;font-size:.85rem;'> — Which features best predict your target variable?</span>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        target = c1.selectbox("Target (what to predict)", num_cols + cat_cols, key="fi_target")
        feat_pool = [c for c in num_cols if c != target]
        features_fi = c2.multiselect("Predictor features", feat_pool,
                                      default=feat_pool[:min(8, len(feat_pool))],
                                      key="fi_feat")
        n_trees = c3.slider("Number of trees", 50, 500, 100, 50)

        if features_fi and target:
            if st.button("Compute Feature Importance", key="fi_run"):
                with st.spinner("Training Random Forest…"):
                    sub = df[features_fi + [target]].dropna()
                    X_fi = sub[features_fi].values
                    y_fi = sub[target]

                    is_cat = target in cat_cols or y_fi.nunique() <= 10
                    if is_cat:
                        model = RFC(n_estimators=n_trees, random_state=42, n_jobs=-1)
                        task = "Classification"
                    else:
                        model = RFR(n_estimators=n_trees, random_state=42, n_jobs=-1)
                        task = "Regression"

                    model.fit(X_fi, y_fi)
                    imp = pd.DataFrame({
                        "Feature": features_fi,
                        "Importance": model.feature_importances_,
                    }).sort_values("Importance", ascending=True)

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Task type", task)
                    m2.metric("Features used", len(features_fi))
                    m3.metric("Trees", n_trees)

                    fig = px.bar(imp, x="Importance", y="Feature", orientation="h",
                                 title=f"Feature Importance for '{target}'",
                                 template="plotly_white",
                                 color="Importance",
                                 color_continuous_scale=["#EDE9FE","#7C3AED"],
                                 text_auto=".3f")
                    fig.update_layout(height=max(350, len(features_fi) * 40),
                                      yaxis={"categoryorder": "total ascending"},
                                      **LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("**Importance Table**")
                    st.dataframe(imp.sort_values("Importance", ascending=False).round(5),
                                 use_container_width=True)

                    # Code to reproduce
                    feat_str = str(features_fi)
                    with st.expander("View / Copy Python Code"):
                        st.code(f"""
import pandas as pd
from sklearn.ensemble import {'RandomForestClassifier' if is_cat else 'RandomForestRegressor'}

df = pd.read_csv("your_file.csv")
features = {feat_str}
X = df[features].dropna()
y = df.loc[X.index, "{target}"]

model = {'RandomForestClassifier' if is_cat else 'RandomForestRegressor'}(n_estimators={n_trees}, random_state=42)
model.fit(X, y)

importance = pd.DataFrame({{"Feature": features, "Importance": model.feature_importances_}})
print(importance.sort_values("Importance", ascending=False))
""", language="python")

    # ── TAB 4 : PCA ──────────────────────────────────────────────────────
    with tab4:
        st.markdown("""
        <div style='background:#FFF7ED;border-radius:12px;padding:1rem 1.3rem;
                    margin-bottom:1rem;border-left:4px solid #F97316;'>
            <b style='color:#9A3412;'>Principal Component Analysis (PCA)</b>
            <span style='color:#6B7280;font-size:.85rem;'> — Reduce high-dimensional data to 2D or 3D for visualization</span>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        pca_feats = c1.multiselect("Features for PCA", num_cols,
                                    default=num_cols[:min(6, len(num_cols))],
                                    key="pca_feat")
        n_comp = c2.radio("Components", [2, 3], horizontal=True, key="pca_comp")
        color_by = c3.selectbox("Color by", ["None"] + cat_cols + num_cols, key="pca_color")

        if pca_feats and len(pca_feats) >= 2:
            if st.button("Run PCA", key="pca_run"):
                with st.spinner("Computing PCA…"):
                    sub = df[pca_feats].dropna()
                    sc = StandardScaler()
                    X_pca = sc.fit_transform(sub)
                    n_c = min(n_comp, len(pca_feats))
                    pca = PCA(n_components=n_c, random_state=42)
                    comps = pca.fit_transform(X_pca)

                    pca_df = pd.DataFrame(
                        comps,
                        columns=[f"PC{i+1}" for i in range(n_c)],
                        index=sub.index,
                    )
                    if color_by != "None":
                        pca_df[color_by] = df.loc[sub.index, color_by].values

                    var = pca.explained_variance_ratio_ * 100
                    m1, m2, m3 = st.columns(3)
                    m1.metric("PC1 variance", f"{var[0]:.1f}%")
                    m2.metric("PC2 variance", f"{var[1]:.1f}%")
                    m3.metric("Total explained", f"{var[:n_c].sum():.1f}%")

                    color_col = color_by if color_by != "None" else None

                    if n_c == 2:
                        fig = px.scatter(pca_df, x="PC1", y="PC2", color=color_col,
                                         title="PCA — 2D Projection",
                                         template="plotly_white", opacity=0.75,
                                         color_discrete_sequence=px.colors.qualitative.Bold,
                                         color_continuous_scale="Viridis",
                                         labels={"PC1": f"PC1 ({var[0]:.1f}%)",
                                                 "PC2": f"PC2 ({var[1]:.1f}%)"})
                    else:
                        fig = px.scatter_3d(pca_df, x="PC1", y="PC2", z="PC3",
                                            color=color_col,
                                            title="PCA — 3D Projection",
                                            template="plotly_white", opacity=0.75,
                                            color_discrete_sequence=px.colors.qualitative.Bold,
                                            color_continuous_scale="Viridis",
                                            labels={"PC1": f"PC1 ({var[0]:.1f}%)",
                                                    "PC2": f"PC2 ({var[1]:.1f}%)",
                                                    "PC3": f"PC3 ({var[2]:.1f}%)"})

                    fig.update_layout(height=500, **LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

                    # Scree plot
                    all_pca = PCA(random_state=42).fit(X_pca)
                    ev_ratio = all_pca.explained_variance_ratio_ * 100
                    cum_ev = np.cumsum(ev_ratio)
                    fig2 = go.Figure()
                    fig2.add_bar(x=[f"PC{i+1}" for i in range(len(ev_ratio))],
                                 y=ev_ratio, name="Individual",
                                 marker_color="#7C3AED", opacity=0.8)
                    fig2.add_trace(go.Scatter(
                        x=[f"PC{i+1}" for i in range(len(cum_ev))],
                        y=cum_ev, name="Cumulative",
                        mode="lines+markers",
                        line=dict(color="#F43F5E", width=2),
                    ))
                    fig2.add_hline(y=80, line_dash="dot", line_color="#059669",
                                   annotation_text="80% variance")
                    fig2.update_layout(title="Scree Plot — Explained Variance per Component",
                                       height=360, template="plotly_white",
                                       yaxis_title="Variance %", xaxis_title="Component",
                                       **LAYOUT)
                    st.plotly_chart(fig2, use_container_width=True)

                    # Loadings
                    loadings = pd.DataFrame(
                        pca.components_.T,
                        index=pca_feats,
                        columns=[f"PC{i+1}" for i in range(n_c)]
                    ).round(4)
                    st.markdown("**PCA Loadings** (contribution of each feature to each component)")
                    st.dataframe(loadings, use_container_width=True)

                    with st.expander("View / Copy Python Code"):
                        st.code(f"""
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.express as px

df = pd.read_csv("your_file.csv")
features = {str(pca_feats)}

X = StandardScaler().fit_transform(df[features].dropna())
pca = PCA(n_components={n_c}, random_state=42)
comps = pca.fit_transform(X)

pca_df = pd.DataFrame(comps, columns={str([f"PC{i+1}" for i in range(n_c)])})
print("Explained variance:", pca.explained_variance_ratio_)

fig = px.scatter(pca_df, x="PC1", y="PC2")
fig.show()
""", language="python")
