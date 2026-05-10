from flask import Flask, render_template, session, redirect, url_for
import os, secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

from api.data_routes import data_bp
from api.viz_routes import viz_bp
from api.analysis_routes import analysis_bp
from api.ml_routes import ml_bp
from api.export_routes import export_bp
from api.features_routes import features_bp

app.register_blueprint(data_bp)
app.register_blueprint(viz_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(ml_bp)
app.register_blueprint(export_bp)
app.register_blueprint(features_bp)

PAGES = [
    ("home",          "⬡", "Home"),
    ("upload",        "⬆", "Upload Data"),
    ("profiling",     "◎", "Data Profiling"),
    ("cleaning",      "✦", "Data Cleaning"),
    ("eda",           "∿", "EDA & Statistics"),
    ("chart",         "▦", "Chart Builder"),
    ("dashboard",     "⚡", "Auto Dashboard"),
    ("timeseries",    "⏱", "Time Series"),
    ("ml",            "◈", "ML Insights"),
    ("forecasting",   "◑", "Forecasting"),
    ("regression",    "⌇", "Regression"),
    ("whatif",        "⟁", "What-If Simulator"),
    ("textanalytics", "❂", "Text Analytics"),
    ("validation",    "✔", "Data Validation"),
    ("calculator",    "∑", "Column Calculator"),
    ("nlq",           "◐", "Ask Your Data"),
    ("live_feed",     "⟳", "Live Data Feed"),
    ("annotations",   "✎", "Annotations"),
    ("outliers",      "◎", "Outlier Detection"),
    ("comparison",    "⟺", "Data Comparison"),
    ("export",        "↓", "Export & Reports"),
]

LEGAL_PAGES = [
    ("privacy",  "Privacy Policy"),
    ("terms",    "Terms of Service"),
    ("cookies",  "Cookie Policy"),
]

@app.context_processor
def inject_nav():
    from api.store import get_store
    store = get_store()
    ds_info = None
    if store.get("df") is not None:
        df = store["df"]
        ds_info = {
            "filename": store.get("filename", "dataset"),
            "rows": f"{df.shape[0]:,}",
            "cols": df.shape[1],
        }
    return dict(nav_pages=PAGES, legal_pages=LEGAL_PAGES, ds_info=ds_info)

@app.route("/")
def home():
    return render_template("home.html", active="home")

@app.route("/upload")
def upload():
    return render_template("upload.html", active="upload")

@app.route("/profiling")
def profiling():
    return render_template("profiling.html", active="profiling")

@app.route("/cleaning")
def cleaning():
    return render_template("cleaning.html", active="cleaning")

@app.route("/eda")
def eda():
    return render_template("eda.html", active="eda")

@app.route("/chart")
def chart():
    return render_template("chart.html", active="chart")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", active="dashboard")

@app.route("/timeseries")
def timeseries():
    return render_template("timeseries.html", active="timeseries")

@app.route("/ml")
def ml():
    return render_template("ml.html", active="ml")

@app.route("/nlq")
def nlq():
    return render_template("nlq.html", active="nlq")

@app.route("/live_feed")
def live_feed():
    return render_template("live_feed.html", active="live_feed")

@app.route("/annotations")
def annotations():
    return render_template("annotations.html", active="annotations")

@app.route("/outliers")
def outliers():
    return render_template("outliers.html", active="outliers")

@app.route("/comparison")
def comparison():
    return render_template("comparison.html", active="comparison")

@app.route("/export")
def export():
    return render_template("export.html", active="export")

@app.route("/forecasting")
def forecasting():
    return render_template("forecasting.html", active="forecasting")

@app.route("/whatif")
def whatif():
    return render_template("whatif.html", active="whatif")

@app.route("/regression")
def regression():
    return render_template("regression.html", active="regression")

@app.route("/textanalytics")
def textanalytics():
    return render_template("textanalytics.html", active="textanalytics")

@app.route("/validation")
def validation():
    return render_template("validation.html", active="validation")

@app.route("/calculator")
def calculator():
    return render_template("calculator.html", active="calculator")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html", active="privacy")

@app.route("/terms")
def terms():
    return render_template("terms.html", active="terms")

@app.route("/cookies")
def cookies():
    return render_template("cookies.html", active="cookies")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
