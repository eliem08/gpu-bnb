# gpu-bnb

[![CI](https://github.com/eliem08/gpu-bnb/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/gpu-bnb/actions/workflows/ci.yml)

> **Airbnb for idle GPUs** — rent out computing power you're not using.

Millions of gaming PCs and workstations sit idle 20 hours a day while
researchers and indie AI builders queue for cloud GPUs. `gpu-bnb` is the
marketplace engine: hosts list machines with availability windows, renters
book time slots, the platform handles pricing, payouts, cancellations and
reliability ratings.

## What the MVP does

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
- Verified hardware via gpu-carfax health reports
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
