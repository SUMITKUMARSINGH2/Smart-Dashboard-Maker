# DataViz Pro

A full-featured data analytics web application built with **Flask**, **Jinja2 templates**, and **vanilla JavaScript**. Upload any dataset and instantly explore, clean, visualize, model, and export your data — no code required.

---

## Features

### Core Analysis
| Page | Description |
|---|---|
| **Upload Data** | CSV, Excel, JSON, Parquet, TSV. Auto-detects separators, encoding, and column types. Includes 4 built-in sample datasets. |
| **Data Profiling** | Per-column statistics: mean, median, std, quartiles, skewness, kurtosis, missing %, unique counts, histograms and value counts. |
| **Data Cleaning** | Remove duplicates, fill/drop missing values, cast types, rename/drop columns, filter rows, strip whitespace, remove outliers, reset to original. |
| **EDA & Statistics** | Correlation heatmap (Pearson/Spearman/Kendall), distributions with KDE, box plots, scatter with trendline, hypothesis tests (T-test, Mann-Whitney, KS, Levene). |
| **Chart Builder** | 19 chart types: Scatter, Line, Bar, Histogram, Area, Box, Violin, Strip, ECDF, Pie, Donut, Treemap, Sunburst, Funnel, Heatmap, Hex Density, Density Heatmap, Bubble, Waterfall, Gauge. |
| **Auto Dashboard** | Auto-generated KPI tiles and smart charts based on your dataset structure. |

### Advanced Analysis
| Page | Description |
|---|---|
| **Time Series** | Trend with rolling average, period-over-period growth %, seasonal decomposition (trend + seasonal + residual). |
| **ML Insights** | K-Means clustering (with elbow curve + PCA 2D), Isolation Forest anomaly detection, Random Forest / GBM feature importance, PCA biplot + scree plot. |
| **Data Forecasting** | ARIMA(p,d,q) time-series forecasting with 95% confidence intervals and a range slider. Configurable order, frequency, and forecast horizon. |
| **What-If Simulator** | Adjust column multipliers with real-time sliders and instantly compare original vs. simulated statistics and totals. |
| **Regression Analysis** | Linear, Ridge, Lasso regression; polynomial degrees 1–4; actual-vs-predicted chart, residual plot, residuals distribution, R², RMSE, MAE, cross-validated R². |
| **Text Analytics** | Word cloud, top-30 word frequency bar chart, TextBlob sentiment analysis (polarity/subjectivity), sentiment distribution pie chart and histogram. |
| **Outlier Detection** | IQR, Z-Score, Modified Z-Score methods across all numeric columns with interactive box plots. |
| **Data Comparison** | Upload a second dataset and compare statistics, distributions, and shapes side-by-side. |

### Data Management
| Page | Description |
|---|---|
| **Ask Your Data (NLQ)** | Natural language queries: "show top 10 by revenue", "average of age", "correlation", "distribution of price", "group by category", and more. |
| **Live Data Feed** | Connect to any JSON or CSV URL endpoint, auto-refresh at a configurable interval, pause/resume. |
| **Annotations** | Tag and annotate specific rows with notes, labels (note/flag/error/review/important), and custom colors. |
| **Data Validation** | Define rules (numeric range, regex pattern, allowed values, not-null) and run validation checks to flag violations. |
| **Column Calculator** | Create new columns using mathematical expressions: `log(price+1)`, `revenue * quantity`, `where(age > 18, 'adult', 'minor')`, and more. |
| **Export & Reports** | Download as CSV, Excel (.xlsx with stats sheet), JSON, Parquet, HTML report, ZIP bundle, or Power BI M-Query + DAX measures. |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · Flask · Pandas · NumPy |
| Statistics | SciPy · Statsmodels |
| Machine Learning | scikit-learn |
| Visualization | Plotly (server-side JSON, client-side rendering) |
| NLP | TextBlob · WordCloud |
| Templates | Jinja2 |
| Frontend | Vanilla JavaScript · Plotly.js |
| Styling | Custom CSS (Space Grotesk + JetBrains Mono fonts) |

---

## Project Structure

```
dataviz-pro/
├── web_app.py                  # Flask app, routing, context processors
├── api/
│   ├── store.py                # Server-side session data store
│   ├── data_routes.py          # Upload, profiling, cleaning, annotations, samples
│   ├── analysis_routes.py      # EDA, time series, outliers, comparison
│   ├── viz_routes.py           # Dashboard, chart builder, NLQ, live feed
│   ├── ml_routes.py            # K-Means, anomaly detection, feature importance, PCA
│   ├── export_routes.py        # CSV, Excel, JSON, Parquet, HTML, ZIP, Power BI
│   └── features_routes.py      # Forecasting, What-If, Regression, Text, Validation, Calculator
├── templates/
│   ├── base.html               # Base layout with sidebar navigation
│   ├── home.html
│   ├── upload.html
│   ├── profiling.html
│   ├── cleaning.html
│   ├── eda.html
│   ├── chart.html
│   ├── dashboard.html
│   ├── timeseries.html
│   ├── ml.html
│   ├── nlq.html
│   ├── live_feed.html
│   ├── annotations.html
│   ├── outliers.html
│   ├── comparison.html
│   ├── export.html
│   ├── forecasting.html
│   ├── whatif.html
│   ├── regression.html
│   ├── textanalytics.html
│   ├── validation.html
│   ├── calculator.html
│   ├── privacy.html
│   ├── terms.html
│   └── cookies.html
├── static/
│   ├── css/style.css           # Full custom dark theme
│   ├── favicon.svg
│   └── js/
│       ├── app.js              # Global utilities, toast, Plotly renderer, API helper
│       ├── upload.js
│       ├── profiling.js
│       ├── cleaning.js
│       ├── eda.js
│       ├── dashboard.js
│       ├── chart_builder.js
│       ├── timeseries.js
│       ├── ml.js
│       ├── nlq.js
│       ├── live_feed.js
│       ├── annotations.js
│       ├── outliers.js
│       ├── comparison.js
│       ├── export.js
│       ├── forecasting.js
│       ├── whatif.js
│       ├── regression.js
│       ├── textanalytics.js
│       ├── validation.js
│       └── calculator.js
└── requirements.txt
```

---

## Getting Started

### Run Locally

```bash
pip install -r requirements.txt
python web_app.py
```

Then open [http://localhost:5000](http://localhost:5000).

### Quick Start

1. Go to **Upload Data** and upload a CSV/Excel file, or click one of the sample datasets (Titanic, Iris, Tips, Diamonds)
2. Explore **Data Profiling** for an instant quality overview
3. Use **Data Cleaning** to fix missing values and duplicates
4. Open **Auto Dashboard** for auto-generated charts
5. Try **Ask Your Data** — type questions in plain English
6. Use **Forecasting** or **ML Insights** for advanced analysis
7. Download results from **Export & Reports**

---

## Supported File Formats

| Format | Extension | Notes |
|---|---|---|
| CSV | `.csv` | Configurable separator and encoding |
| Excel | `.xlsx`, `.xls` | First sheet loaded |
| JSON | `.json` | Records or object format |
| Parquet | `.parquet` | Fastest for large datasets |
| TSV | `.tsv`, `.txt` | Tab-separated |

---

## Column Calculator — Expression Reference

| Function | Example | Description |
|---|---|---|
| `log(x)` | `log(price + 1)` | Natural logarithm |
| `sqrt(x)` | `sqrt(area)` | Square root |
| `abs(x)` | `abs(delta)` | Absolute value |
| `exp(x)` | `exp(rate)` | Exponential |
| `round(x, n)` | `round(price, 2)` | Round to n decimals |
| `where(cond, a, b)` | `where(age > 18, 'adult', 'minor')` | Conditional |
| `clip(x, lo, hi)` | `revenue.clip(0, 1e6)` | Clip to range |
| Arithmetic | `price * qty` | `+`, `-`, `*`, `/`, `**` |
| Pandas methods | `col.mean()`, `col.quantile(0.9)` | Full pandas Series API |

---

## Data Validation Rule Types

| Type | Description | Example |
|---|---|---|
| **Numeric Range** | Value must be between min and max | Age: 0 – 120 |
| **Regex Pattern** | String must match a pattern | Email: `^[\w.]+@[\w.]+$` |
| **Allowed Values** | Value must be in a list | Status: active, inactive, pending |
| **Not Null** | No missing/null values allowed | Any required field |

---

## ARIMA Forecasting Guide

- **p** (AR order): number of lag observations. Start at 1–2.
- **d** (differencing): 1 for most non-stationary series, 0 if already stationary.
- **q** (MA order): number of lagged forecast errors. Start at 1.
- Use **Daily** frequency for daily data, **Monthly** for monthly, etc.
- The shaded band shows the **95% confidence interval**.

---

## Notes

- All data is stored in **server-side memory** per session — nothing is persisted to disk or sent externally.
- Session data is cleared when the server restarts or after inactivity.
- For production deployment, replace the in-memory store with Redis or a database-backed session.
- Plotly charts are rendered client-side using **Plotly.js** from a CDN.
