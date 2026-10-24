# gpu-bnb

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
