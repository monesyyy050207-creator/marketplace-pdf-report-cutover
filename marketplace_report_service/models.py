from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class SellerAsset(BaseModel):
    sku: str
    title: str
    quantity_available: int = Field(ge=0)
    ready_to_ship: bool


class BuyerUpdate(BaseModel):
    order_id: str
    buyer_name: str
    address_confirmed: bool
    fraud_review: Literal["clear", "hold"]
    note: str | None = None


class OrderHandoff(BaseModel):
    order_id: str
    sku: str
    quantity: int = Field(gt=0)
    carrier: str


class MarketplaceReportRequest(BaseModel):
    report_id: str
    marketplace_name: str
    period_label: str
    seller_assets: list[SellerAsset]
    buyer_updates: list[BuyerUpdate]
    order_handoffs: list[OrderHandoff]


class HandoffDecision(BaseModel):
    order_id: str
    status: Literal["ready", "hold", "cancelled"]
    reason: str


class MarketplaceReportResult(BaseModel):
    report_id: str
    decisions: list[HandoffDecision]
    markdown: str
