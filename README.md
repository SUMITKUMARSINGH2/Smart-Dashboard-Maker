# DataViz Pro

DataViz Pro is a full-stack analytics platform built with Flask. Upload a dataset and explore it with interactive dashboards, EDA tools, forecasting, text analytics, and more — all through a modern dark-theme web UI.

---

## Key Features

- Upload CSV, Excel, JSON, Parquet, or TSV files
- Auto dashboard with KPIs and smart charts
- Chart Builder with 20+ chart types
- EDA & Statistics: correlation, distributions, box plots, scatter, hypothesis testing
- Time series analysis, seasonal decomposition, ARIMA forecasting
- Regression analysis (linear, ridge, lasso, polynomial)
- Text analytics: word frequency, sentiment analysis, word cloud
- Natural language queries (NLQ) over your data
- Outlier detection, data profiling, cleaning, and validation rules
- What-If simulator, dataset comparison, annotations
- Export to CSV, Excel, JSON

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask, Gunicorn |
| Visualization | Plotly 6.x |
| Data Science | Pandas, NumPy, scikit-learn, SciPy, Statsmodels |
| NLP | TextBlob, WordCloud |
| Frontend | Jinja2 templates, HTML/CSS, JavaScript |

---

## Project Layout

```
DataViz-Pro/
├── web/
│   ├── web_app.py            # Flask app entrypoint (main)
│   ├── api/
│   │   ├── data_routes.py    # Upload, preview, cleaning, profiling
│   │   ├── viz_routes.py     # Chart builder, dashboard, NLQ, live feed
│   │   ├── analysis_routes.py# EDA, time series, outliers, comparison
│   │   ├── features_routes.py# Forecasting, regression, text analytics, what-if
│   │   └── store.py          # Session-based data store
│   ├── templates/            # Jinja2 HTML templates
│   ├── static/
│   │   ├── css/style.css     # App styles
│   │   └── js/               # Page-specific JavaScript modules
│   ├── render.yaml           # Render deployment config
│   └── requirements.txt      # Python dependencies
├── streamlitdashb/           # Legacy Streamlit dashboard (not the main app)
├── sample_sales_data.csv     # Sample dataset for quick start
└── README.md
```

---

## Running Locally

```bash
# Install dependencies
pip install -r web/requirements.txt

# Start the Flask app
cd web && python web_app.py
```

Then open [http://localhost:5000](http://localhost:5000).

---

## Deployment (Render)

The `web/render.yaml` is pre-configured for [Render](https://render.com):

```yaml
services:
  - type: web
    name: datavizpro-flask
    runtime: python3
    rootDir: web
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 web_app:app
    plan: free
```

Push to GitHub, connect the repo in Render, and it will auto-deploy.

---

## Quick Start

1. Go to **Upload** and drop any CSV/Excel file, or load the built-in **sample sales dataset**
2. Explore the **Auto Dashboard** for instant KPIs and charts
3. Use **Chart Builder** to create custom visualizations
4. Run **EDA & Statistics** for correlations, distributions, and hypothesis tests
5. Try **Forecasting** for ARIMA time series predictions
6. Use **Text Analytics** for sentiment analysis and word frequency on text columns
