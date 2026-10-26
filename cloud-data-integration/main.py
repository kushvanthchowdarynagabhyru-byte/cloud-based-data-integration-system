"""CLI entry point.

Usage:
    python setup_sample_data.py          # create sample sources (once)
    python main.py                       # run with config.json
    python main.py --config my.json --db out.db
"""
import argparse
import json

from cdis.integrator import run_integration


def main():
    ap = argparse.ArgumentParser(description="Cloud-Based Data Integration System")
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--db", default="unified.db")
    a = ap.parse_args()

    with open(a.config, encoding="utf-8") as f:
        config = json.load(f)

    print("Running integration...")
    summary = run_integration(config, a.db)
    print("\nDone:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
