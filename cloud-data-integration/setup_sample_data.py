"""Creates the three sample source systems (CSV, JSON, SQLite)."""
import json
import sqlite3
from pathlib import Path

d = Path("sample_data")
d.mkdir(exist_ok=True)

(d / "crm_customers.csv").write_text(
    "cust_id,name,email_addr,city\n"
    "C001,alice smith,Alice@Example.com,Hyderabad\n"
    "C002,bob jones,bob@example.com,Mumbai\n"
    "C003,carol white,carol@example.com,Delhi\n"
    "C004,dave brown,,Chennai\n"
)

(d / "web_signups.json").write_text(json.dumps({"users": [
    {"userId": "W10", "fullName": "Alice Smith", "mail": "alice@example.com", "country": "India"},
    {"userId": "W11", "fullName": "Eve Black", "mail": "eve@example.com", "country": "USA"},
    {"userId": "W12", "fullName": "Bob Jones", "mail": "BOB@example.com", "country": "India"},
]}, indent=2))

db = d / "billing.db"
db.unlink(missing_ok=True)
with sqlite3.connect(db) as c:
    c.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, customer_name TEXT, email TEXT, balance REAL)")
    c.executemany("INSERT INTO customers VALUES (?,?,?,?)", [
        (1, "Alice Smith", "alice@example.com", 120.5),
        (2, "Carol White", "carol@example.com", 75.0),
        (3, "Frank Green", "frank@example.com", 300.25),
    ])
print("Sample data created in sample_data/")
