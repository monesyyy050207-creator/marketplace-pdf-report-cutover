from __future__ import annotations

from .models import (
    BuyerUpdate,
    HandoffDecision,
    MarketplaceReportRequest,
    MarketplaceReportResult,
    SellerAsset,
)


def _asset_map(assets: list[SellerAsset]) -> dict[str, SellerAsset]:
    return {asset.sku: asset for asset in assets}


def _buyer_map(updates: list[BuyerUpdate]) -> dict[str, BuyerUpdate]:
    return {update.order_id: update for update in updates}


def build_marketplace_report(request: MarketplaceReportRequest) -> MarketplaceReportResult:
    assets = _asset_map(request.seller_assets)
    buyers = _buyer_map(request.buyer_updates)
    decisions: list[HandoffDecision] = []

    for handoff in request.order_handoffs:
        asset = assets[handoff.sku]
        buyer = buyers[handoff.order_id]

        if asset.quantity_available < handoff.quantity:
            decisions.append(
                HandoffDecision(
                    order_id=handoff.order_id,
                    status="cancelled",
                    reason="inventory shortfall",
                )
            )
            continue

        if not asset.ready_to_ship:
            decisions.append(
                HandoffDecision(
                    order_id=handoff.order_id,
                    status="hold",
                    reason="seller asset not ready to ship",
                )
            )
            continue

        if not buyer.address_confirmed or buyer.fraud_review == "hold":
            decisions.append(
                HandoffDecision(
                    order_id=handoff.order_id,
                    status="hold",
                    reason="buyer update requires review",
                )
            )
            continue

        decisions.append(
            HandoffDecision(
                order_id=handoff.order_id,
                status="ready",
                reason="cleared for fulfillment handoff",
            )
        )

    markdown = render_report_markdown(request, decisions)
    return MarketplaceReportResult(
        report_id=request.report_id,
        decisions=decisions,
        markdown=markdown,
    )


def render_report_markdown(
    request: MarketplaceReportRequest, decisions: list[HandoffDecision]
) -> str:
    lines = [
        f"# {request.marketplace_name} marketplace report",
        "",
        f"Period: {request.period_label}",
        f"Report ID: {request.report_id}",
        "",
        "## Seller assets",
        "",
        "| SKU | Title | Qty Available | Ready to Ship |",
        "| --- | --- | ---: | --- |",
    ]

    for asset in request.seller_assets:
        lines.append(
            f"| {asset.sku} | {asset.title} | {asset.quantity_available} | {'yes' if asset.ready_to_ship else 'no'} |"
        )

    lines.extend(
        [
            "",
            "## Buyer updates",
            "",
            "| Order | Buyer | Address Confirmed | Fraud Review | Note |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    buyer_map = _buyer_map(request.buyer_updates)
    for buyer in request.buyer_updates:
        lines.append(
            f"| {buyer.order_id} | {buyer.buyer_name} | {'yes' if buyer.address_confirmed else 'no'} | {buyer.fraud_review} | {buyer.note or ''} |"
        )

    lines.extend(
        [
            "",
            "## Order handoff decisions",
            "",
            "| Order | SKU | Qty | Carrier | Decision | Reason |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )

    decision_map = {decision.order_id: decision for decision in decisions}
    for handoff in request.order_handoffs:
        decision = decision_map[handoff.order_id]
        buyer = buyer_map[handoff.order_id]
        lines.append(
            f"| {handoff.order_id} | {handoff.sku} | {handoff.quantity} | {handoff.carrier} | {decision.status} | {decision.reason}; buyer={buyer.buyer_name} |"
        )

    return "\n".join(lines) + "\n"
