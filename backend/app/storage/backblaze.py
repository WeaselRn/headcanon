import logging

logger = logging.getLogger(__name__)


class BackblazeClient:
    def __init__(self, key_id: str, application_key: str, bucket: str, endpoint: str) -> None:
        self.key_id = key_id
        self.application_key = application_key
        self.bucket = bucket
        self.endpoint = endpoint

    def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        raise NotImplementedError

    def download(self, key: str) -> bytes:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def list_keys(self, prefix: str) -> list[str]:
        raise NotImplementedError
