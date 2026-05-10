from flask import session
import uuid

_STORE = {}

def _sid():
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    return session["sid"]

def get_store():
    sid = _sid()
    if sid not in _STORE:
        _STORE[sid] = {
            "raw_df": None, "df": None, "filename": None,
            "annotations": {}, "cmp_df_b": None, "cmp_name_b": None,
            "live_df": None, "live_history": [], "live_connected": False,
            "live_url": "", "live_interval": 30, "live_paused": False,
            "live_fetch_count": 0, "live_last_fetch": 0.0,
        }
    return _STORE[sid]

def set_store(**kwargs):
    store = get_store()
    store.update(kwargs)
