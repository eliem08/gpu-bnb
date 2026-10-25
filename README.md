<!-- sell-kit:start -->
# GPU BnB

[![CI](https://github.com/eliem08/gpu-bnb/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/gpu-bnb/actions/workflows/ci.yml)

> **Rent out the GPUs you are not using, by the hour.**

**Who it's for:** People and labs with idle GPUs, and the developers who need short bursts of compute.

**The problem:** Idle GPUs earn nothing, and renters can't easily find trustworthy short-term capacity.

**What you get:** Listings with availability windows, overlap-safe booking for multi-GPU rigs, pricing and fees, cancellations and host reliability scores.

## Quickstart

Customers receive a release archive with the wheel and the examples. Python 3.10+ and no other dependencies.

```bash
pip install gpu_bnb-0.1.0-py3-none-any.whl
gpu-bnb search examples/listings.json --start 2026-11-01T01:00 --end 2026-11-01T04:00 --min-vram 24
gpu-bnb demo
```

## Web app and API

Every command is also a JSON API endpoint and a browser form, served by the built-in web app.

```bash
gpu-bnb-web --port 8000          # then open http://127.0.0.1:8000
gpu-bnb-web keys create --label "first customer"   # prints an API key (stored hashed)
docker build -t gpu-bnb . && docker run -p 8000:8000 -e API_KEYS=sk_... -v gpu-bnb-data:/data gpu-bnb
```

Every API call needs `Authorization: Bearer <key>` once any key exists; a server on a public address refuses to start without one. Calls are rate-limited per key (60/min, `--rate`) and metered: `gpu-bnb-web usage` prints calls per key for billing.

Endpoints: `POST /api/demo`, `POST /api/search`, plus `GET /healthz` and `GET /api/spec` (machine-readable field list).
Files are sent as `{"name": ..., "content": ...}`, folders as `{"files": [...]}` or a base64 zip.

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Host** | Free + 15% platform fee | List any GPU; Availability windows; Payouts |
| **Host Pro** | $19 per month, 10% fee | Multi-GPU rigs; Reliability badge; Priority placement |
| **Operator** | $999 per month | Run your own GPU marketplace; Custom fees; White label |

To start a trial or buy a plan, [request access](https://github.com/eliem08/gpu-bnb/issues/new?title=GPU%20BnB%20trial&labels=sales).

## Licence

Proprietary. Copyright (c) 2026 eliem08. All rights reserved. Use requires a paid plan or an active trial; see [LICENSE](LICENSE).
<!-- sell-kit:end -->

## What it does

- **Listings**: GPU model, VRAM, count, hourly price, region, availability
  windows (recurring daily hours, e.g. 00:00–08:00 and 13:00–17:00)
- **Search**: filter by min VRAM, GPU model, region, max price and a requested
  time window; sorted by price and host reliability
- **Booking** with no double-booking (interval overlap checks) and window validation
- **Pricing**: host rate × hours + 15% platform fee; long-booking discount
- **Cancellation policy**: full refund > 24h before start, 50% within 24h, none after start
- **Reliability**: sessions delivered vs. host-cancelled/interrupted → score shown in search
- **Payouts** ledger per host

## Quickstart

```bash
pip install -e .
gpu-bnb demo
```

## Roadmap

- Host agent: container sandbox (gVisor/Kata), auto-pause when owner starts gaming
- Verified hardware via gpuvitals health reports
- Spot-style dynamic pricing and job-level (not time-level) rentals

## Development

Zero runtime dependencies; Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m unittest discover -s tests -t .           # unit + CLI smoke tests
ruff check . && ruff format --check .               # lint + format
```

```
gpu_bnb/core.py       domain logic (pure, importable, fully tested)
gpu_bnb/__main__.py   CLI (`gpu-bnb ...` / `python -m gpu_bnb ...`)
tests/                unit tests + generated CLI smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #19).
