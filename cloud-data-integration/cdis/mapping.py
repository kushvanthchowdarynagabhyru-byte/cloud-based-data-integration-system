"""Map source-specific fields onto the unified schema."""

UNIFIED_FIELDS = ["customer_id", "name", "email", "city", "country", "balance"]


def _clean(field: str, value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    if field == "email" and value:
        return value.lower()
    if field == "name" and value:
        return value.title()
    if field == "balance" and value is not None:
        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            return None
    return value


def map_records(records: list[dict], mapping: dict, source: str) -> list[dict]:
    """mapping = {unified_field: source_field}"""
    out = []
    for r in records:
        row = {f: _clean(f, r.get(mapping[f])) if f in mapping else None for f in UNIFIED_FIELDS}
        row["source"] = source
        out.append(row)
    return out
