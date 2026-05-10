from flask import Blueprint, request, jsonify, session
import pandas as pd
import numpy as np
import io, json, traceback
from api.store import get_store, set_store
from shared_store import save_shared, load_shared, get_meta as bridge_meta

data_bp = Blueprint("data", __name__, url_prefix="/api")

# ── separator auto-detection ──────────────────────────────────────────────────
def _smart_read_csv(raw, preferred_sep, enc):
    """Parse CSV with preferred separator; if only 1 column results, try others."""
    SEPS = [preferred_sep, ",", ";", "|", "\t"]
    seen = set()
    for sep in SEPS:
        if sep in seen:
            continue
        seen.add(sep)
        try:
            df = pd.read_csv(io.BytesIO(raw), sep=sep, encoding=enc, nrows=5)
            if df.shape[1] > 1:
                # Re-read the full file with the winning separator
                full_df = pd.read_csv(io.BytesIO(raw), sep=sep, encoding=enc)
                return full_df, sep
        except Exception:
            continue
    # Fallback: return whatever the preferred sep gives (even if 1 col)
    return pd.read_csv(io.BytesIO(raw), sep=preferred_sep, encoding=enc), preferred_sep

# ── helpers ──────────────────────────────────────────────────────────────────
def _df_safe(df, max_rows=500):
    d = df.copy()
    for c in d.select_dtypes(include="datetimetz").columns:
        d[c] = d[c].astype(str)
    for c in d.select_dtypes(include=["datetime64"]).columns:
        d[c] = d[c].astype(str)
    return d.where(pd.notnull(d), None).head(max_rows).to_dict(orient="records")

def _col_types(df):
    out = {}
    for c in df.columns:
        dt = str(df[c].dtype)
        if "int" in dt or "float" in dt:
            out[c] = "numeric"
        elif "datetime" in dt:
            out[c] = "datetime"
        elif "bool" in dt:
            out[c] = "bool"
        else:
            out[c] = "categorical"
    return out

# ── data quality score ────────────────────────────────────────────────────────
def _quality_score(df):
    """Return a 0-100 score, letter grade, and per-dimension breakdown."""
    rows, cols = df.shape

    # 1. Completeness (40 pts): how complete the data is (no missing values)
    total_cells = rows * cols
    missing_cells = int(df.isnull().sum().sum())
    completeness = max(0.0, 1.0 - missing_cells / total_cells) if total_cells else 1.0
    completeness_pts = round(completeness * 40, 1)

    # 2. Uniqueness (30 pts): penalise for duplicate rows
    dup_count = int(df.duplicated().sum())
    uniqueness = max(0.0, 1.0 - dup_count / rows) if rows else 1.0
    uniqueness_pts = round(uniqueness * 30, 1)

    # 3. Type richness (20 pts): ratio of non-object columns
    typed_cols = df.select_dtypes(exclude="object").shape[1]
    type_ratio = typed_cols / cols if cols else 0
    type_pts = round(type_ratio * 20, 1)

    # 4. Column naming (10 pts): penalise unnamed/blank headers
    bad_names = sum(
        1 for c in df.columns
        if str(c).strip() == "" or str(c).lower().startswith("unnamed")
    )
    naming_pts = round(max(0.0, 1.0 - bad_names / cols) * 10, 1)

    score = round(completeness_pts + uniqueness_pts + type_pts + naming_pts, 1)

    if score >= 90:   grade, color = "A", "#10B981"
    elif score >= 80: grade, color = "B", "#00D4FF"
    elif score >= 70: grade, color = "C", "#F59E0B"
    elif score >= 60: grade, color = "D", "#FF6B00"
    else:             grade, color = "F", "#EF4444"

    tips = []
    if completeness < 0.95:
        pct = round((1 - completeness) * 100, 1)
        tips.append(f"{pct}% of values are missing — consider imputation or dropping columns")
    if dup_count > 0:
        tips.append(f"{dup_count:,} duplicate rows found — use Data Cleaning to remove them")
    if type_ratio < 0.3:
        tips.append("Most columns are text — consider casting numeric columns for analysis")
    if bad_names > 0:
        tips.append(f"{bad_names} unnamed column(s) — rename them for better readability")
    if not tips:
        tips.append("Dataset looks clean and well-structured!")

    return {
        "score": score,
        "grade": grade,
        "color": color,
        "dimensions": {
            "completeness": {"score": completeness_pts, "max": 40,
                             "label": "Completeness", "pct": round(completeness * 100, 1)},
            "uniqueness":   {"score": uniqueness_pts,   "max": 30,
                             "label": "Uniqueness",    "pct": round(uniqueness * 100, 1)},
            "type_richness":{"score": type_pts,         "max": 20,
                             "label": "Type Richness",  "pct": round(type_ratio * 100, 1)},
            "naming":       {"score": naming_pts,        "max": 10,
                             "label": "Column Naming",  "pct": round((1 - bad_names / cols) * 100 if cols else 100, 1)},
        },
        "tips": tips,
        "missing_cells": missing_cells,
        "dup_rows": dup_count,
    }

# ── upload ────────────────────────────────────────────────────────────────────
@data_bp.route("/upload", methods=["POST"])
def api_upload():
    try:
        f = request.files.get("file")
        if not f:
            return jsonify(error="No file"), 400
        fname = f.filename
        raw = f.read()
        ext = fname.rsplit(".", 1)[-1].lower()
        sep = request.form.get("sep", ",")
        enc = request.form.get("encoding", "utf-8")
        if ext == "csv":
            df, sep = _smart_read_csv(raw, sep, enc)
        elif ext in ("xls", "xlsx"):
            df = pd.read_excel(io.BytesIO(raw))
        elif ext == "json":
            df = pd.read_json(io.BytesIO(raw))
        elif ext == "parquet":
            df = pd.read_parquet(io.BytesIO(raw))
        elif ext in ("txt", "tsv"):
            df = pd.read_csv(io.BytesIO(raw), sep="\t", encoding=enc)
        else:
            return jsonify(error=f"Unsupported format: {ext}"), 400
        df.columns = [str(c).strip() for c in df.columns]
        set_store(raw_df=df.copy(), df=df.copy(), filename=fname,
                  annotations={})
        store = get_store()
        save_shared(df, fname, source="flask")
        return jsonify(
            ok=True, filename=fname,
            rows=df.shape[0], cols=df.shape[1],
            columns=list(df.columns),
            col_types=_col_types(df),
            preview=_df_safe(df, 100),
            dtypes={c: str(df[c].dtype) for c in df.columns},
            missing={c: int(df[c].isna().sum()) for c in df.columns},
            detected_sep=sep,
            quality=_quality_score(df),
        )
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

@data_bp.route("/dataset-info")
def api_dataset_info():
    store = get_store()
    df = store.get("df")
    if df is None:
        return jsonify(loaded=False)
    return jsonify(
        loaded=True, filename=store.get("filename"),
        rows=df.shape[0], cols=df.shape[1],
        columns=list(df.columns),
        col_types=_col_types(df),
        dtypes={c: str(df[c].dtype) for c in df.columns},
        missing={c: int(df[c].isna().sum()) for c in df.columns},
        numeric_cols=[c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])],
        cat_cols=[c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and str(df[c].dtype) != "datetime64[ns]"],
        date_cols=[c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])],
    )

@data_bp.route("/preview")
def api_preview():
    store = get_store()
    df = store.get("df")
    if df is None:
        return jsonify(error="No dataset"), 400
    n = min(int(request.args.get("n", 100)), len(df))
    return jsonify(rows=_df_safe(df, n), columns=list(df.columns))

# ── profiling ─────────────────────────────────────────────────────────────────
@data_bp.route("/profile")
def api_profile():
    store = get_store()
    df = store.get("df")
    if df is None:
        return jsonify(error="No dataset"), 400
    try:
        out = []
        for c in df.columns:
            col = df[c]
            n_miss = int(col.isna().sum())
            n_uniq = int(col.nunique())
            entry = {
                "col": c, "dtype": str(col.dtype),
                "missing": n_miss, "missing_pct": round(n_miss / len(df) * 100, 2),
                "unique": n_uniq,
            }
            if pd.api.types.is_numeric_dtype(col):
                s = col.dropna()
                entry.update({
                    "min": float(s.min()) if len(s) else None,
                    "max": float(s.max()) if len(s) else None,
                    "mean": float(s.mean()) if len(s) else None,
                    "median": float(s.median()) if len(s) else None,
                    "std": float(s.std()) if len(s) else None,
                    "q25": float(s.quantile(0.25)) if len(s) else None,
                    "q75": float(s.quantile(0.75)) if len(s) else None,
                    "skew": float(s.skew()) if len(s) else None,
                    "kurt": float(s.kurt()) if len(s) else None,
                    "zeros": int((s == 0).sum()),
                })
                # top values histogram
                hist, bins = np.histogram(s, bins=min(20, n_uniq or 20))
                entry["hist"] = {"counts": hist.tolist(), "edges": [round(x,4) for x in bins.tolist()]}
            else:
                vc = col.value_counts().head(10)
                entry["top_values"] = [{"value": str(k), "count": int(v)} for k, v in vc.items()]
            out.append(entry)
        total = len(df)
        dup = int(df.duplicated().sum())
        return jsonify(
            profile=out, total_rows=total, total_cols=len(df.columns),
            duplicates=dup, dup_pct=round(dup/total*100,2) if total else 0,
            memory_mb=round(df.memory_usage(deep=True).sum()/1024/1024, 3),
        )
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ── cleaning ──────────────────────────────────────────────────────────────────
@data_bp.route("/clean", methods=["POST"])
def api_clean():
    store = get_store()
    df = store.get("df")
    if df is None:
        return jsonify(error="No dataset"), 400
    try:
        body = request.json or {}
        op = body.get("op")
        rows_before = len(df)
        cols_before = len(df.columns)
        msg = ""

        if op == "drop_duplicates":
            df = df.drop_duplicates()
            msg = f"Removed {rows_before - len(df)} duplicate rows"

        elif op == "drop_missing":
            thresh = float(body.get("threshold", 50))
            col = body.get("col")
            if col:
                df = df.dropna(subset=[col])
                msg = f"Dropped rows with missing '{col}'"
            else:
                df_clean = df.dropna(thresh=int(len(df.columns)*(1-thresh/100)))
                msg = f"Removed {rows_before - len(df_clean)} rows with >{thresh}% missing"
                df = df_clean

        elif op == "fill_missing":
            col = body.get("col")
            method = body.get("method", "mean")
            value = body.get("value")
            cols = [col] if col else df.select_dtypes(include="number").columns.tolist()
            for c in cols:
                if method == "mean":
                    df[c] = df[c].fillna(df[c].mean())
                elif method == "median":
                    df[c] = df[c].fillna(df[c].median())
                elif method == "mode":
                    mv = df[c].mode()
                    if len(mv): df[c] = df[c].fillna(mv[0])
                elif method == "zero":
                    df[c] = df[c].fillna(0)
                elif method == "ffill":
                    df[c] = df[c].ffill()
                elif method == "bfill":
                    df[c] = df[c].bfill()
                elif method == "value":
                    df[c] = df[c].fillna(value)
            msg = f"Filled missing values in {len(cols)} column(s) using {method}"

        elif op == "drop_col":
            col = body.get("col")
            if col and col in df.columns:
                df = df.drop(columns=[col])
                msg = f"Dropped column '{col}'"

        elif op == "rename_col":
            old = body.get("old"); new = body.get("new")
            if old and new:
                df = df.rename(columns={old: new})
                msg = f"Renamed '{old}' → '{new}'"

        elif op == "cast_col":
            col = body.get("col"); dtype = body.get("dtype")
            if col and dtype:
                if dtype == "numeric":
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                elif dtype == "string":
                    df[col] = df[col].astype(str)
                elif dtype == "datetime":
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                elif dtype == "bool":
                    df[col] = df[col].astype(bool)
                msg = f"Cast '{col}' to {dtype}"

        elif op == "strip_whitespace":
            str_cols = df.select_dtypes(include="object").columns
            for c in str_cols:
                df[c] = df[c].str.strip()
            msg = f"Stripped whitespace from {len(str_cols)} text columns"

        elif op == "lowercase_cols":
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            msg = "Converted column names to lowercase"

        elif op == "remove_outliers":
            col = body.get("col")
            method = body.get("method", "iqr")
            if col and col in df.columns:
                s = df[col].dropna()
                if method == "iqr":
                    q1, q3 = s.quantile(0.25), s.quantile(0.75)
                    iqr = q3 - q1
                    df = df[(df[col] >= q1 - 1.5*iqr) & (df[col] <= q3 + 1.5*iqr)]
                elif method == "zscore":
                    from scipy import stats as sp
                    zs = np.abs(sp.zscore(s))
                    mask = pd.Series(True, index=df.index)
                    mask[s.index] = zs < 3
                    df = df[mask]
                msg = f"Removed outliers from '{col}' using {method.upper()}"

        elif op == "filter_rows":
            col = body.get("col")
            op2 = body.get("filter_op", "==")
            val = body.get("val")
            if col and col in df.columns:
                try:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        val = float(val)
                    if op2 == "==": df = df[df[col] == val]
                    elif op2 == "!=": df = df[df[col] != val]
                    elif op2 == ">": df = df[df[col] > val]
                    elif op2 == "<": df = df[df[col] < val]
                    elif op2 == ">=": df = df[df[col] >= val]
                    elif op2 == "<=": df = df[df[col] <= val]
                    elif op2 == "contains": df = df[df[col].astype(str).str.contains(str(val), na=False)]
                except:
                    pass
                msg = f"Filtered rows where '{col}' {op2} {val}"

        elif op == "reset":
            raw = store.get("raw_df")
            if raw is not None:
                df = raw.copy()
                msg = "Reset to original uploaded data"

        set_store(df=df)
        return jsonify(ok=True, msg=msg, rows=len(df), cols=len(df.columns))
    except Exception as e:
        return jsonify(error=str(e), tb=traceback.format_exc()), 500

# ── annotations ───────────────────────────────────────────────────────────────
@data_bp.route("/annotations", methods=["GET", "POST", "DELETE"])
def api_annotations():
    store = get_store()
    if request.method == "GET":
        return jsonify(annotations=store.get("annotations", {}))
    body = request.json or {}
    ann = store.get("annotations", {})
    if request.method == "POST":
        row = str(body.get("row"))
        note = body.get("note", "")
        tag = body.get("tag", "note")
        color = body.get("color", "#00D4FF")
        ann[row] = {"note": note, "tag": tag, "color": color}
        set_store(annotations=ann)
        return jsonify(ok=True)
    if request.method == "DELETE":
        row = str(body.get("row"))
        ann.pop(row, None)
        set_store(annotations=ann)
        return jsonify(ok=True)

@data_bp.route("/sample/<name>")
def api_sample(name):
    try:
        import seaborn as sns
        df = sns.load_dataset(name)
        df.columns = [str(c).strip() for c in df.columns]
        set_store(raw_df=df.copy(), df=df.copy(), filename=f"{name}.csv", annotations={})
        save_shared(df, f"{name}.csv", source="flask")
        return jsonify(
            ok=True, filename=f"{name}.csv",
            rows=df.shape[0], cols=df.shape[1],
            columns=list(df.columns),
            col_types=_col_types(df),
            preview=_df_safe(df, 100),
            dtypes={c: str(df[c].dtype) for c in df.columns},
            missing={c: int(df[c].isna().sum()) for c in df.columns},
        )
    except Exception as e:
        return jsonify(error=str(e)), 500


@data_bp.route("/bridge-meta")
def api_bridge_meta():
    """Return shared bridge metadata so either app can check if new data is available."""
    meta = bridge_meta()
    if meta is None:
        return jsonify(exists=False)
    return jsonify(exists=True, **meta)


@data_bp.route("/sync-from-bridge", methods=["POST"])
def api_sync_from_bridge():
    """Load the shared bridge file into the Flask session store."""
    try:
        df, meta = load_shared()
        if df is None:
            return jsonify(ok=False, error="No bridge data found"), 404
        fname = meta.get("filename", "synced_data.csv")
        set_store(raw_df=df.copy(), df=df.copy(), filename=fname, annotations={})
        return jsonify(
            ok=True, filename=fname,
            rows=df.shape[0], cols=df.shape[1],
            columns=list(df.columns),
            col_types=_col_types(df),
            preview=_df_safe(df, 100),
            dtypes={c: str(df[c].dtype) for c in df.columns},
            missing={c: int(df[c].isna().sum()) for c in df.columns},
            source=meta.get("source", "unknown"),
        )
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@data_bp.route("/annotated-data")
def api_annotated_data():
    store = get_store()
    df = store.get("df")
    ann = store.get("annotations", {})
    if df is None:
        return jsonify(error="No dataset"), 400
    rows = _df_safe(df, 1000)
    for i, r in enumerate(rows):
        r["_idx"] = i
        r["_ann"] = ann.get(str(i))
    return jsonify(rows=rows, columns=list(df.columns), annotations=ann)
