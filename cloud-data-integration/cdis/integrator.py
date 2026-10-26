"""Integration engine: extract -> map -> merge -> store."""
import csv
import io
import json
import sqlite3
from datetime import datetime, timezone

from .connectors import build_connector
from .mapping import UNIFIED_FIELDS, map_records
from .storage import build_storage


def merge_records(rows: list[dict]) -> list[dict]:
    """Merge records that share an email; first non-null value wins, sources are combined."""
    merged: dict[str, dict] = {}
    no_email = []
    for r in rows:
        key = r.get("email")
        if not key:
            no_email.append({**r, "sources": r["source"]})
            continue
        if key not in merged:
            merged[key] = {**r, "sources": r["source"]}
            continue
        m = merged[key]
        for f in UNIFIED_FIELDS:
            if m.get(f) is None and r.get(f) is not None:
                m[f] = r[f]
        if r["source"] not in m["sources"].split(","):
            m["sources"] += "," + r["source"]
    out = list(merged.values()) + no_email
    for i, r in enumerate(out, 1):
        r["unified_id"] = f"U{i:04d}"
        r.pop("source", None)
    return out


def run_integration(config: dict, db_path: str = "unified.db") -> dict:
    raw_total, mapped = 0, []
    storage = build_storage(config.get("storage", {}))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for src in config["sources"]:
        conn = build_connector(src)
        records = conn.fetch()
        raw_total += len(records)
        print(f"  extracted {len(records):>3} records from {src['name']} ({src['type']})")
        # land the raw extract in the cloud "raw" zone
        storage.put(f"raw/{src['name']}/{stamp}.json", json.dumps(records, indent=2).encode())
        mapped += map_records(records, src["mapping"], src["name"])

    unified = merge_records(mapped)
    cols = ["unified_id"] + UNIFIED_FIELDS + ["sources"]

    # curated zone: CSV + JSON in the cloud store
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(unified)
    csv_url = storage.put(f"curated/customers/{stamp}.csv", buf.getvalue().encode())
    storage.put("curated/customers/latest.json", json.dumps(unified, indent=2).encode())

    # serving layer: SQLite
    with sqlite3.connect(db_path) as db:
        db.execute("DROP TABLE IF EXISTS unified_customers")
        db.execute("CREATE TABLE unified_customers (unified_id TEXT PRIMARY KEY, customer_id TEXT, name TEXT, "
                   "email TEXT, city TEXT, country TEXT, balance REAL, sources TEXT)")
        db.executemany(
            "INSERT INTO unified_customers VALUES (?,?,?,?,?,?,?,?)",
            [tuple(r.get(c) for c in cols) for r in unified],
        )

    return {"raw_records": raw_total, "unified_records": len(unified), "curated_file": csv_url, "database": db_path}
