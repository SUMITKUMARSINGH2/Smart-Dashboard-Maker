"""
Shared data bridge between Flask (port 5000) and Streamlit (port 8080).
Both apps read/write to the same pickle + JSON metadata files on disk.
"""
import os, pickle, json, time
from datetime import datetime

BRIDGE_PKL  = "/tmp/dataviz_bridge.pkl"
BRIDGE_META = "/tmp/dataviz_bridge_meta.json"


def save_shared(df, filename, source="flask"):
    """Persist dataframe + metadata to the shared bridge. Returns True on success."""
    try:
        import pandas as pd
        with open(BRIDGE_PKL, "wb") as f:
            pickle.dump(df, f, protocol=4)
        meta = {
            "filename": filename,
            "rows": int(df.shape[0]),
            "cols": int(df.shape[1]),
            "columns": list(df.columns),
            "updated_at": datetime.now().isoformat(),
            "updated_ts": time.time(),
            "source": source,
        }
        with open(BRIDGE_META, "w") as f:
            json.dump(meta, f)
        return True
    except Exception as e:
        return False


def load_shared():
    """Load dataframe from shared bridge. Returns (df, meta) or (None, None)."""
    try:
        if not os.path.exists(BRIDGE_PKL) or not os.path.exists(BRIDGE_META):
            return None, None
        with open(BRIDGE_PKL, "rb") as f:
            df = pickle.load(f)
        with open(BRIDGE_META, "r") as f:
            meta = json.load(f)
        return df, meta
    except Exception:
        return None, None


def get_meta():
    """Return metadata dict without loading the full dataframe, or None."""
    try:
        if not os.path.exists(BRIDGE_META):
            return None
        with open(BRIDGE_META, "r") as f:
            return json.load(f)
    except Exception:
        return None


def bridge_exists():
    return os.path.exists(BRIDGE_PKL) and os.path.exists(BRIDGE_META)


def clear_bridge():
    for p in (BRIDGE_PKL, BRIDGE_META):
        try:
            os.remove(p)
        except FileNotFoundError:
            pass
