"""Source connectors. Each returns a list of dict records."""
import csv
import json
import sqlite3
import urllib.request
from abc import ABC, abstractmethod


class Connector(ABC):
    def __init__(self, name: str, **options):
        self.name = name
        self.options = options

    @abstractmethod
    def fetch(self) -> list[dict]:
        ...


class CSVConnector(Connector):
    def fetch(self):
        with open(self.options["path"], newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))


class JSONConnector(Connector):
    """Reads a local JSON file or a REST endpoint (http/https URL)."""

    def fetch(self):
        src = self.options["path"]
        if src.startswith(("http://", "https://")):
            with urllib.request.urlopen(src, timeout=15) as r:
                data = json.load(r)
        else:
            with open(src, encoding="utf-8") as f:
                data = json.load(f)
        key = self.options.get("records_key")
        return data[key] if key else data


class SQLiteConnector(Connector):
    def fetch(self):
        conn = sqlite3.connect(self.options["path"])
        conn.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in conn.execute(self.options["query"])]
        finally:
            conn.close()


CONNECTORS = {"csv": CSVConnector, "json": JSONConnector, "sqlite": SQLiteConnector}


def build_connector(cfg: dict) -> Connector:
    cls = CONNECTORS.get(cfg["type"])
    if cls is None:
        raise ValueError(f"Unknown source type: {cfg['type']}")
    opts = {k: v for k, v in cfg.items() if k not in ("name", "type", "mapping")}
    return cls(cfg["name"], **opts)
