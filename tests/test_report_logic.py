from marketplace_report_service.models import MarketplaceReportRequest
from marketplace_report_service.report_logic import build_marketplace_report


def test_marketplace_handoff_decisions_follow_stock_and_review_rules() -> None:
    request = MarketplaceReportRequest.model_validate(
        {
            "report_id": "rpt-test",
            "marketplace_name": "Northwind Market",
            "period_label": "test window",
            "seller_assets": [
                {
                    "sku": "SKU-1",
                    "title": "Ready Item",
                    "quantity_available": 5,
                    "ready_to_ship": True,
                },
                {
                    "sku": "SKU-2",
                    "title": "Needs Prep",
                    "quantity_available": 5,
                    "ready_to_ship": False,
                },
                {
                    "sku": "SKU-3",
                    "title": "Sold Out",
                    "quantity_available": 0,
                    "ready_to_ship": True,
                },
            ],
            "buyer_updates": [
                {
                    "order_id": "ORD-1001",
                    "buyer_name": "A",
                    "address_confirmed": True,
                    "fraud_review": "clear",
                },
                {
                    "order_id": "ORD-1002",
                    "buyer_name": "B",
                    "address_confirmed": True,
                    "fraud_review": "clear",
                },
                {
                    "order_id": "ORD-1003",
                    "buyer_name": "C",
                    "address_confirmed": True,
                    "fraud_review": "clear",
                },
            ],
            "order_handoffs": [
                {
                    "order_id": "ORD-1001",
                    "sku": "SKU-1",
                    "quantity": 1,
                    "carrier": "DHL",
                },
                {
                    "order_id": "ORD-1002",
                    "sku": "SKU-2",
                    "quantity": 1,
                    "carrier": "UPS",
                },
                {
                    "order_id": "ORD-1003",
                    "sku": "SKU-3",
                    "quantity": 1,
                    "carrier": "FedEx",
                },
            ],
        }
    )

    result = build_marketplace_report(request)

    actual = {decision.order_id: decision.status for decision in result.decisions}
    assert actual == {
        "ORD-1001": "ready",
        "ORD-1002": "hold",
        "ORD-1003": "cancelled",
    }
    assert "Order handoff decisions" in result.markdown
