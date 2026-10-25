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
gpu-bnb demo
```

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Host** | Free + 15% platform fee | List any GPU; Availability windows; Payouts |
| **Host Pro** | $19 per month, 10% fee | Multi-GPU rigs; Reliability badge; Priority placement |
| **Operator** | $999 per month | Run your own GPU marketplace; Custom fees; White label |

To start a trial or buy a plan, email **sales@YOUR-DOMAIN.com**.

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
