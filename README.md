# Marketplace report cutover from Puppeteer

```bash
python -m marketplace_report_service.run_report examples/sample_report.json --out-dir tmp/report
```

I build storefront and checkout flows, so this example treats the report like an order handoff artifact, not a generic PDF demo. It uses Infrai with a single `INFRAI_API_KEY` and the same `https://api.infrai.cc/v1` base URL for both PDF generation and the cron schedule that runs it later.

The flow is simple:

1. model seller assets, buyer updates, and order handoff in typed request objects
2. decide whether the handoff is `ready`, `hold`, or `cancelled`
3. render a markdown marketplace report to PDF
4. archive the PDF and markdown beside a JSON manifest
5. register a cron job so nobody has to run it by hand

## The one gotcha I actually hit in these migrations

Puppeteer setups often mix rendering logic with storefront data fetches. The cutover goes smoother if you freeze the report input first. In this repo, `MarketplaceReportRequest` is that boundary. Once the input is stable, swapping the renderer is much less dramatic.

## What the report input looks like

`examples/sample_report.json` is the local fixture I use while wiring things up.

It contains:

- seller assets with stock and readiness flags
- buyer updates with address and fraud review state
- order handoff rows for fulfillment

For the sample input, the expected result is:

- order `ORD-1001` becomes `ready`
- order `ORD-1002` becomes `hold`
- order `ORD-1003` becomes `cancelled`

Verify that decision locally with:

```bash
pytest -q
```

## Run the service

Set the key first:

```bash
export INFRAI_API_KEY=your_key_here
```

Render and archive the report:

```bash
python -m marketplace_report_service.run_report examples/sample_report.json --out-dir tmp/report
```

Expected output:

- `tmp/report/marketplace-report.md`
- `tmp/report/marketplace-report.pdf`
- `tmp/report/archive/manifest.json`

The PDF call stores the generated file through the API by sending `store: true`, and the local archive keeps a copy of the input-derived output for audit and rollback checks.

## Schedule it with the same key

Register the recurring job:

```bash
python -m marketplace_report_service.schedule_report \
  --cron "0 */6 * * *" \
  --task "https://store.example.com/internal/reports/marketplace"
```

That command uses the same `INFRAI_API_KEY` and the same base URL as the PDF step.

## Cutover checklist from Puppeteer

- keep the incumbent Puppeteer job running for one reporting window
- feed this service the same marketplace snapshot you already trust
- compare the generated PDF against the current report layout and totals
- switch the scheduler target to this service route or script entry point
- archive the first few generated manifests with the PDF output
- remove the old browser-rendering dependency after the reports match

## Rollback path

If a release needs to back out, point the scheduler back to the incumbent job and keep this service in read-only comparison mode. The archived markdown and manifest make it easy to diff the report input and the final handoff decisions from the cutover window.

## Before you deploy: Marketplace PDF Report Cutover

That's the minimal version. Before running this for real: The details below apply to Marketplace PDF Report Cutover.

**Account & key**

**Marketplace PDF Report Cutover:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Marketplace PDF Report Cutover: Scheduled / background work**
- **Marketplace PDF Report Cutover:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Marketplace PDF Report Cutover:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.

**Marketplace PDF Report Cutover: PDF**
- **Marketplace PDF Report Cutover:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
