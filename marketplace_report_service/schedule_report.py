from __future__ import annotations

import argparse
import json

from .infrai_client import InfraiClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Schedule the marketplace report job")
    parser.add_argument("--cron", required=True, help="Cron expression for the report")
    parser.add_argument("--task", required=True, help="URL to invoke on schedule")
    args = parser.parse_args()

    infrai = InfraiClient()
    response = infrai.cron_create(cron_expr=args.cron, task=args.task)

    print(json.dumps({
        "job_id": response["data"]["job_id"],
        "metadata": response.get("metadata", {}),
    }, indent=2))


if __name__ == "__main__":
    main()
