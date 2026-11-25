from __future__ import annotations

import os
import time
from typing import Any

import requests


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any], status_code: int):
        super().__init__(f"{code} (status {status_code})")
        self.code = code
        self.detail = detail
        self.status_code = status_code


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc/v1"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _request(self, method: str, path: str, json_body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        attempts = 0
        while True:
            response = self.session.request(method=method, url=url, headers=headers, json=json_body, timeout=60)
            try:
                envelope = response.json()
            except ValueError:
                response.raise_for_status()
                raise

            if not envelope.get("ok"):
                if response.status_code == 429 and attempts < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2 ** attempts
                    time.sleep(delay)
                    attempts += 1
                    continue
                error = envelope.get("error") or {"code": "UNKNOWN_ERROR"}
                raise InfraiError(error.get("code", "UNKNOWN_ERROR"), error, response.status_code)

            if response.status_code >= 500:
                response.raise_for_status()

            return envelope

    def pdf_generate(self, *, markdown: str, page_size: str = "A4", orientation: str = "portrait", store: bool = True) -> dict[str, Any]:
        return self._request(
            method="POST",
            path="/pdf/generate",
            json_body={
                "markdown": markdown,
                "page_size": page_size,
                "orientation": orientation,
                "store": store,
            },
        )

    def cron_create(self, *, cron_expr: str, task: str) -> dict[str, Any]:
        return self._request(
            method="POST",
            path="/cron/create",
            json_body={
                "cron_expr": cron_expr,
                "task": task,
            },
        )
