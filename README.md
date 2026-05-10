# DataViz Pro

DataViz Pro is a dual-interface analytics project with separate apps for:
- **Flask web app** (`web/flask_app.py`) using Jinja2 templates and API routes
- **Streamlit dashboard** (`streamlitdashb/streamlit_app.py`) with interactive notebook-style pages

---

## Key Features

- Upload CSV, Excel, JSON, Parquet, TSV files
- Data profiling, cleaning, EDA, and visualization tools
- Auto dashboard and chart builder
- Time series analysis, forecasting, regression, and machine learning insights
- Natural language queries, live data feed, annotations, and export options

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Pandas, NumPy |
| Visualization | Plotly, Streamlit |
| Data Science | scikit-learn, SciPy, Statsmodels |
| NLP | TextBlob |
| Frontend | Jinja2 templates, HTML/CSS, JavaScript |

---

## Project Layout

```
Smart-Dashboard-Maker/
├── streamlitdashb/
│   ├── streamlit_app.py          # Streamlit app entrypoint
│   ├── home.py                   # Streamlit home page
│   ├── filesin.py                # File upload page
│   ├── connector.py              # Connect & import page
│   ├── dataover.py               # Data overview page
│   ├── quality.py                # Data quality page
│   ├── profiling.py              # Data profiling page
│   ├── eda_page.py               # EDA & statistics page
│   ├── viz_tools.py              # Visualization tools page
│   ├── dashgen.py                # Auto dashboard page
│   ├── editdash.py               # Chart builder page
│   ├── ml_page.py                # ML insights page
│   ├── export_share.py           # Export & share page
│   └── nlq_page.py               # NLQ page
├── web/
│   ├── flask_app.py              # Flask app entrypoint
│   ├── advanced_app.py           # Advanced Flask app
│   ├── api/                      # Flask API routes
│   ├── modules/                  # Flask page modules
│   ├── templates/                # Flask HTML templates
│   └── static/                   # Static assets for Flask
├── shared_store.py               # Shared data store
├── styles.py                     # Shared styles
├── sample_sales_data.csv
├── requirements.txt
└── README.md
```

---

## Operating Mode

The two apps are **completely independent**:
- Each app manages its own data and session state
- No data sharing or syncing between Flask and Streamlit
- Run one or both simultaneously on different ports

| App | Port | Data Storage | State |
|---|---|---|---|
| **Streamlit** | Auto (usually 8501) | Session memory (ephemeral) | Per-browser session |
| **Flask** | 5000 | Server-side store | Per-user session |

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Streamlit Dashboard

```bash
streamlit run streamlitdashb/streamlit_app.py
```

Open the URL displayed in terminal (usually `http://localhost:8501`)

---

## Run the Flask Web App

```bash
python web/flask_app.py
```

Open `http://localhost:5000` in your browser.

---

## Run Both Simultaneously

Open two terminals:

```bash
# Terminal 1: Streamlit
streamlit run streamlitdashb/streamlit_app.py

# Terminal 2: Flask
python web/flask_app.py
```

---

## Notes

- **Streamlit**: Real-time interactive dashboard, session-based data (cleared on refresh)
- **Flask**: Traditional web app with server-side sessions, persistent during browser session
- Choose based on your use case:
  - **Streamlit** for rapid exploration and prototyping
  - **Flask** for production-ready interface with persistent state
