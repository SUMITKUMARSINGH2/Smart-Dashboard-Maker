import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from styles import DARK_CSS, section_header, kpi_row_html

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,21,40,1)",
    font=dict(family="Space Grotesk", color="#E2E8F0"),
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444"],
)

def ml_insights():
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    st.markdown(section_header("◈", "ML Insights", "Clustering, feature importance, anomaly detection & PCA"), unsafe_allow_html=True)

    if "clean_data" not in st.session_state or st.session_state["clean_data"] is None:
        st.warning("⚠️ No data uploaded yet. Please upload a file first.")
        return

    df = st.session_state["clean_data"]
    num_cols = df.select_dtypes(include=["int64","float64","int32","float32"]).columns.tolist()

    if len(num_cols) < 2:
        st.warning("At least 2 numeric columns are required for ML analysis.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["🔵 Clustering (K-Means)", "📉 PCA", "⚠️ Anomaly Detection", "⭐ Feature Importance"])

    # ── K-Means ────────────────────────────────────────────────────────────────
    with tab1:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        feat_cols = st.multiselect("Feature columns", num_cols, default=num_cols[:min(4, len(num_cols))], key="km_cols")
        n_clusters = st.slider("Number of clusters (K)", 2, 10, 3, key="km_k")

        if st.button("Run K-Means Clustering") and len(feat_cols) >= 2:
            with st.spinner("Clustering..."):
                X = df[feat_cols].dropna()
                scaler = StandardScaler()
                Xs = scaler.fit_transform(X)
                km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = km.fit_predict(Xs)
                X = X.copy()
                X["Cluster"] = [f"Cluster {c}" for c in labels]

                c1, c2 = st.columns(2)
                with c1:
                    fig = px.scatter(X, x=feat_cols[0], y=feat_cols[1],
                                     color="Cluster",
                                     color_discrete_sequence=["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444","#8B5CF6","#F97316","#06B6D4","#84CC16"],
                                     title=f"K-Means Clusters (K={n_clusters})")
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    cluster_counts = X["Cluster"].value_counts().reset_index()
                    cluster_counts.columns = ["Cluster", "Count"]
                    fig2 = px.pie(cluster_counts, names="Cluster", values="Count",
                                  color_discrete_sequence=["#00D4FF","#7C3AED","#FF006E","#10B981","#F59E0B","#EF4444"],
                                  title="Cluster Distribution")
                    fig2.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig2, use_container_width=True)

                # Cluster means
                st.markdown('<div style="font-weight:600;color:#E2E8F0;margin:.75rem 0 .5rem;">Cluster Centroids</div>', unsafe_allow_html=True)
                centroids = pd.DataFrame(scaler.inverse_transform(km.cluster_centers_),
                                          columns=feat_cols)
                centroids.index = [f"Cluster {i}" for i in range(n_clusters)]
                st.dataframe(centroids.round(3), use_container_width=True)

                # Inertia elbow
                inertias = []
                K_range = range(2, min(11, len(X)))
                for k in K_range:
                    km_test = KMeans(n_clusters=k, random_state=42, n_init=10)
                    km_test.fit(Xs)
                    inertias.append(km_test.inertia_)
                fig3 = px.line(x=list(K_range), y=inertias, markers=True,
                               labels={"x": "K", "y": "Inertia"},
                               title="Elbow Curve",
                               color_discrete_sequence=["#00D4FF"])
                fig3.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig3, use_container_width=True)

    # ── PCA ────────────────────────────────────────────────────────────────────
    with tab2:
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler

        pca_cols = st.multiselect("Feature columns", num_cols, default=num_cols, key="pca_cols")
        n_components = st.slider("Components", 2, min(10, len(pca_cols)) if len(pca_cols) > 2 else 2, 2, key="pca_comp")

        if st.button("Run PCA") and len(pca_cols) >= 2:
            with st.spinner("Computing PCA..."):
                X = df[pca_cols].dropna()
                scaler = StandardScaler()
                Xs = scaler.fit_transform(X)
                pca = PCA(n_components=min(n_components, len(pca_cols)))
                comps = pca.fit_transform(Xs)
                var_ratio = pca.explained_variance_ratio_

                # Scree plot
                c1, c2 = st.columns(2)
                with c1:
                    fig = px.bar(x=[f"PC{i+1}" for i in range(len(var_ratio))],
                                 y=var_ratio * 100,
                                 labels={"x": "Component", "y": "Variance Explained (%)"},
                                 color_discrete_sequence=["#7C3AED"],
                                 title="Explained Variance (Scree Plot)")
                    fig.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig, use_container_width=True)

                with c2:
                    pca_df = pd.DataFrame(comps, columns=[f"PC{i+1}" for i in range(comps.shape[1])])
                    fig2 = px.scatter(pca_df, x="PC1", y="PC2",
                                      color_discrete_sequence=["#00D4FF"],
                                      title="PCA — PC1 vs PC2", opacity=.7)
                    fig2.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig2, use_container_width=True)

                # Loadings
                loadings = pd.DataFrame(pca.components_.T,
                                         columns=[f"PC{i+1}" for i in range(comps.shape[1])],
                                         index=pca_cols)
                st.markdown('<div style="font-weight:600;color:#E2E8F0;margin:.75rem 0 .5rem;">Component Loadings</div>', unsafe_allow_html=True)
                st.dataframe(loadings.round(4), use_container_width=True)

    # ── Anomaly Detection ──────────────────────────────────────────────────────
    with tab3:
        from sklearn.ensemble import IsolationForest

        anom_cols = st.multiselect("Feature columns", num_cols, default=num_cols[:min(4, len(num_cols))], key="anom_cols")
        contamination = st.slider("Expected anomaly fraction", 0.01, 0.20, 0.05, 0.01)

        if st.button("Detect Anomalies") and len(anom_cols) >= 1:
            with st.spinner("Running Isolation Forest..."):
                X = df[anom_cols].dropna()
                iso = IsolationForest(contamination=contamination, random_state=42)
                preds = iso.fit_predict(X)
                X = X.copy()
                X["Anomaly"] = ["Anomaly" if p == -1 else "Normal" for p in preds]
                n_anom = (preds == -1).sum()

                st.markdown(f"""
                <div style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);
                            border-radius:8px;padding:.75rem 1rem;margin-bottom:1rem;">
                  <b style="color:#EF4444;">⚠️ {n_anom:,} anomalies detected</b>
                  <span style="color:#94A3B8;"> ({round(n_anom/len(X)*100,1)}% of data)</span>
                </div>
                """, unsafe_allow_html=True)

                fig = px.scatter(X, x=anom_cols[0], y=anom_cols[1] if len(anom_cols) > 1 else anom_cols[0],
                                 color="Anomaly",
                                 color_discrete_map={"Normal": "#00D4FF", "Anomaly": "#EF4444"},
                                 title=f"Anomaly Detection — Isolation Forest (contamination={contamination})")
                fig.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown('<div style="font-weight:600;color:#E2E8F0;margin:.75rem 0 .5rem;">Anomalous Rows (sample)</div>', unsafe_allow_html=True)
                anom_rows = df.loc[X[X["Anomaly"] == "Anomaly"].index].head(50)
                st.dataframe(anom_rows, use_container_width=True, hide_index=True)

    # ── Feature Importance ─────────────────────────────────────────────────────
    with tab4:
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder

        cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
        all_cols = num_cols + cat_cols
        target = st.selectbox("Target column", all_cols, key="fi_target")
        feat_options = [c for c in num_cols if c != target]

        if st.button("Compute Feature Importance") and feat_options:
            with st.spinner("Training model..."):
                X_df = df[feat_options].dropna()
                y = df[target].loc[X_df.index]
                valid = y.notna()
                X_df = X_df[valid]
                y = y[valid]

                is_class = not pd.api.types.is_numeric_dtype(y)
                if is_class:
                    le = LabelEncoder()
                    y = le.fit_transform(y.astype(str))
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    model = RandomForestRegressor(n_estimators=100, random_state=42)

                model.fit(X_df, y)
                importances = pd.DataFrame({
                    "Feature": feat_options,
                    "Importance": model.feature_importances_
                }).sort_values("Importance", ascending=True)

                fig = px.bar(importances, x="Importance", y="Feature", orientation="h",
                             color="Importance", color_continuous_scale="Plasma",
                             title=f"Feature Importance → predicting '{target}'")
                fig.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig, use_container_width=True)
