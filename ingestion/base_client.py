import logging
import time
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class APIClientError(RuntimeError):
    """Raised when an API request cannot be completed after retries."""


class BaseAPIClient:
    """Reusable REST API client with retries, backoff, and rate-limit handling."""

    def __init__(self, base_url: str, timeout_seconds: int = 10, max_retries: int = 3) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.session = requests.Session()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        params = params or {}
        headers = headers or {}

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, params=params, headers=headers, timeout=self.timeout_seconds)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "2"))
                    logger.warning("rate_limited", extra={"ctx_url": url, "ctx_retry_after": retry_after})
                    time.sleep(retry_after)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                sleep_seconds = min(2 ** attempt, 30)
                logger.warning(
                    "api_request_failed",
                    extra={"ctx_url": url, "ctx_attempt": attempt, "ctx_sleep_seconds": sleep_seconds},
                    exc_info=exc,
                )
                if attempt == self.max_retries:
                    raise APIClientError(f"Failed GET {url} after {self.max_retries} attempts") from exc
                time.sleep(sleep_seconds)
        raise APIClientError(f"Failed GET {url}")
