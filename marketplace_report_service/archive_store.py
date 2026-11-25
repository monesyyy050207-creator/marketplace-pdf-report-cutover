from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any
from urllib.parse import unquote_to_bytes

import requests

from .models import MarketplaceReportRequest, MarketplaceReportResult


class ArchiveResult(dict):
    pass


def archive_report(
    output_dir: Path,
    request: MarketplaceReportRequest,
    result: MarketplaceReportResult,
    pdf_response: dict[str, Any],
) -> ArchiveResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = output_dir / "marketplace-report.md"
    markdown_path.write_text(result.markdown, encoding="utf-8")

    pdf_payload = pdf_response.get("data", {})
    pdf_url = pdf_payload["url"]
    if pdf_url.startswith("data:"):
        header, encoded = pdf_url.split(",", 1)
        payload = unquote_to_bytes(encoded)
        pdf_bytes = base64.b64decode(payload, validate=True) if header.endswith(";base64") else payload
    else:
        pdf_download = requests.get(pdf_url, timeout=60)
        pdf_download.raise_for_status()
        pdf_bytes = pdf_download.content
    pdf_path = output_dir / "marketplace-report.pdf"
    pdf_path.write_bytes(pdf_bytes)

    manifest = {
        "report_id": request.report_id,
        "marketplace_name": request.marketplace_name,
        "period_label": request.period_label,
        "decisions": [decision.model_dump() for decision in result.decisions],
        "pdf_metadata": pdf_response.get("metadata", {}),
    }
    manifest_path = archive_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return ArchiveResult(
        markdown_path=str(markdown_path),
        pdf_path=str(pdf_path),
        manifest_path=str(manifest_path),
    )
