"""Cloud storage layer.

LocalObjectStorage mimics a bucket on disk (works with no credentials).
S3Storage uses boto3 and is selected with storage.type = "s3" in config.json.
"""
from abc import ABC, abstractmethod
from pathlib import Path


class ObjectStorage(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes) -> str: ...

    @abstractmethod
    def list(self, prefix: str = "") -> list[str]: ...


class LocalObjectStorage(ObjectStorage):
    def __init__(self, bucket_dir: str = "cloud_bucket"):
        self.root = Path(bucket_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key, data):
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return f"file://{path.resolve()}"

    def list(self, prefix=""):
        return sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")
                      if p.is_file() and str(p.relative_to(self.root)).startswith(prefix))


class S3Storage(ObjectStorage):
    def __init__(self, bucket: str, region: str | None = None):
        import boto3  # optional dependency

        self.bucket = bucket
        self.s3 = boto3.client("s3", region_name=region)

    def put(self, key, data):
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)
        return f"s3://{self.bucket}/{key}"

    def list(self, prefix=""):
        resp = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [o["Key"] for o in resp.get("Contents", [])]


def build_storage(cfg: dict) -> ObjectStorage:
    if cfg.get("type") == "s3":
        return S3Storage(cfg["bucket"], cfg.get("region"))
    return LocalObjectStorage(cfg.get("bucket_dir", "cloud_bucket"))
