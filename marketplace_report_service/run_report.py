from __future__ import annotations

import argparse
import json
from pathlib import Path

from .archive_store import archive_report
from .infrai_client import InfraiClient
from .models import MarketplaceReportRequest
from .report_logic import build_marketplace_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Render and archive a marketplace report PDF")
    parser.add_argument("input", help="Path to a MarketplaceReportRequest JSON file")
    parser.add_argument("--out-dir", default="tmp/report", help="Directory for PDF and archive output")
    args = parser.parse_args()

    request_data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    request = MarketplaceReportRequest.model_validate(request_data)
    report = build_marketplace_report(request)

    infrai = InfraiClient()
    pdf_response = infrai.pdf_generate(markdown=report.markdown, page_size="A4", orientation="portrait", store=True)
    archive = archive_report(Path(args.out_dir), request, report, pdf_response)

    print(json.dumps({
        "report_id": report.report_id,
        "decisions": [decision.model_dump() for decision in report.decisions],
        "archive": archive,
    }, indent=2))


if __name__ == "__main__":
    main()
