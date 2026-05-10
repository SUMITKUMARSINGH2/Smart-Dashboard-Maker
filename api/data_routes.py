from flask import Blueprint, request, jsonify, session
import pandas as pd
import numpy as np
import io, json, traceback
from api.store import get_store, set_store

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
        return jsonify(
            ok=True, filename=fname,
            rows=df.shape[0], cols=df.shape[1],
            columns=list(df.columns),
            col_types=_col_types(df),
            preview=_df_safe(df, 100),
            dtypes={c: str(df[c].dtype) for c in df.columns},
            missing={c: int(df[c].isna().sum()) for c in df.columns},
            detected_sep=sep,
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
