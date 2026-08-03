import logging
from typing import Any

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None  # type: ignore[assignment]

    class ClientError(Exception):  # type: ignore[no-redef]
        pass

logger = logging.getLogger(__name__)


class BackblazeClient:
    def __init__(self, key_id: str, application_key: str, bucket: str, endpoint: str) -> None:
        self.key_id = key_id
        self.application_key = application_key
        self.bucket = bucket
        self.endpoint = endpoint
        self._s3_client: Any = None

    @property
    def s3_client(self) -> Any:
        if self._s3_client is None:
            if boto3 is None:
                raise RuntimeError(
                    "boto3 package is not installed. Please install boto3 to perform Backblaze S3 operations."
                )
            endpoint_url = (
                self.endpoint
                if self.endpoint.startswith(("http://", "https://"))
                else f"https://{self.endpoint}"
            )
            self._s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.application_key,
                endpoint_url=endpoint_url,
            )
        return self._s3_client

    def _get_public_url(self, key: str) -> str:
        clean_endpoint = self.endpoint.replace("https://", "").replace("http://", "")
        return f"https://{self.bucket}.{clean_endpoint}/{key}"

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        logger.info("Uploading key %s to bucket %s", key, self.bucket)
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return self._get_public_url(key)

    def download(self, key: str) -> bytes:
        logger.info("Downloading key %s from bucket %s", key, self.bucket)
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            body: bytes = response["Body"].read()
            return body
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code in ("NoSuchKey", "404"):
                raise FileNotFoundError(f"Key '{key}' not found in bucket '{self.bucket}'") from exc
            raise

    def delete(self, key: str) -> None:
        logger.info("Deleting key %s from bucket %s", key, self.bucket)
        self.s3_client.delete_object(Bucket=self.bucket, Key=key)

    def delete_prefix(self, prefix: str) -> None:
        logger.info("Deleting prefix %s from bucket %s", prefix, self.bucket)
        keys = self.list_keys(prefix)
        for key in keys:
            self.delete(key)

    def list_keys(self, prefix: str = "") -> list[str]:
        logger.info("Listing keys with prefix '%s' in bucket %s", prefix, self.bucket)
        keys: list[str] = []
        paginator = self.s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = str(obj["Key"])
                keys.append(key)
        return keys
