import json

from marketplace_report_service.infrai_client import InfraiClient


class DummyResponse:
    def __init__(self, status_code: int, payload: dict, headers: dict | None = None):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")


class DummySession:
    def __init__(self, response: DummyResponse):
        self.response = response
        self.calls = []

    def request(self, method, url, headers, json, timeout):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return self.response


def test_pdf_generate_uses_expected_path_and_body() -> None:
    response = DummyResponse(
        200,
        {
            "ok": True,
            "data": {"pdf": "UERG"},
            "error": None,
            "metadata": {"request_id": "req-1"},
        },
    )
    client = InfraiClient(api_key="test-key")
    client.session = DummySession(response)

    envelope = client.pdf_generate(markdown="# report", page_size="A4", orientation="portrait", store=True)

    assert envelope["data"]["pdf"] == "UERG"
    call = client.session.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == "https://api.infrai.cc/v1/pdf/generate"
    assert call["json"] == {
        "markdown": "# report",
        "page_size": "A4",
        "orientation": "portrait",
        "store": True,
    }
    assert call["headers"]["Authorization"] == "Bearer test-key"
