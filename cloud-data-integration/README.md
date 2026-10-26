# Cloud-Based Data Integration System (base)

Pulls customer data from several heterogeneous sources, maps them to one unified schema,
merges duplicates by email, and publishes the result to cloud object storage plus a SQL database.

```
CSV (CRM) ─┐
JSON (web) ─┼─> connectors -> field mapping -> merge by email ─> cloud bucket (raw/ + curated/)
SQLite (billing) ┘                                            └─> unified.db
```

## Run

```bash
python setup_sample_data.py     # creates sample_data/
python main.py                  # runs the integration, writes cloud_bucket/ and unified.db
```
No third-party packages are needed for the default (local) mode.

## Using real cloud storage (AWS S3)
```bash
pip install boto3
```
Set in `config.json`: `"storage": {"type": "s3", "bucket": "my-bucket", "region": "ap-south-1"}`
and provide AWS credentials the usual way (env vars or `aws configure`).

## Adding a source
Add an entry to `sources` in `config.json` with `type` (`csv`, `json`, `sqlite`), its location,
and a `mapping` of unified field -> source field. The JSON connector also accepts an http(s) URL as `path`.

## Layout
- `cdis/connectors.py` source connectors
- `cdis/mapping.py` unified schema and field cleaning
- `cdis/storage.py` local and S3 object storage
- `cdis/integrator.py` extract, merge and load logic
