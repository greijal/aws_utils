from typing import Optional, List
import boto3
import webbrowser
import os
from boto3.session import Session


class S3Utils:
    LOG_PREFIX = "[S3Utils]"

    def __init__(self, session: Optional[Session] = None) -> None:
        self._log("Initializing S3 client...")
        self.client = (session or boto3.Session()).client("s3")

    def _log(self, message: str) -> None:
        print(f"{self.LOG_PREFIX} {message}")

    def list_buckets(self) -> List[str]:
        self._log("Listing S3 buckets...")
        resp = self.client.list_buckets()
        return [b["Name"] for b in resp.get("Buckets", [])]

    def open_bucket_in_console(self, bucket: str) -> None:
        if not bucket:
            self._log("No bucket specified to open in console.")
            return

        region = self.client.meta.region_name
        url = f"https://s3.console.aws.amazon.com/s3/buckets/{bucket}?region={region}&tab=objects"
        self._log(f"Opening bucket in console: {url}")
        webbrowser.open(url)

    def delete_object(self, bucket: str, key: str) -> None:
        if not bucket or not key:
            raise ValueError("Bucket and key are required")

        self._log(f"Deleting object '{key}' from bucket '{bucket}'...")
        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            self._log(f"Object '{key}' successfully deleted.")
        except Exception as e:
            self._log(f"Error deleting object: {e}")
            raise

    def upload_file(self, file_path: str, bucket: str, key: Optional[str] = None) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        key = key or os.path.basename(file_path)
        self._log(f"Uploading file '{file_path}' to bucket '{bucket}' with key '{key}'...")
        self.client.upload_file(file_path, bucket, key)

    def upload_directory(self, dir_path: str, bucket: str, prefix: str = "") -> None:
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"Directory not found: {dir_path}")

        self._log(f"Uploading directory '{dir_path}' to bucket '{bucket}' with prefix '{prefix}'...")
        for root, _, files in os.walk(dir_path):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, dir_path)
                s3_key = os.path.join(prefix, rel_path).replace("\\", "/")
                self._log(f"Uploading file '{local_path}' to key '{s3_key}'...")
                self.upload_file(local_path, bucket, s3_key)
