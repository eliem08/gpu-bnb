"""Stateless commands: read a JSON request, print a JSON decision (also served by the web app)."""

import json
from datetime import datetime

from .core import Market


def add_commands(sub):
    s = sub.add_parser("search", help="find available GPUs for a time slot, cheapest reliable first, with quotes")
    s.add_argument("listings", help="JSON list of GPU listings")
    s.add_argument("--start", required=True, help="ISO datetime, e.g. 2026-11-01T01:00")
    s.add_argument("--end", required=True)
    s.add_argument("--min-vram", type=int, default=0)
    s.add_argument("--gpu")
    s.add_argument("--max-price", type=float)


def run(a):
    with open(a.listings, encoding="utf-8-sig") as fh:
        listings = json.load(fh)
    if not isinstance(listings, list) or not all(isinstance(x, dict) for x in listings):
        raise ValueError("listings must be a JSON list of objects")
    start, end = datetime.fromisoformat(a.start), datetime.fromisoformat(a.end)
    if end <= start:
        raise ValueError("end must be after start")
    m = Market()
    for x in listings:
        m.list_gpu(
            x["host"],
            x["gpu"],
            int(x["vram_gb"]),
            float(x["hourly"]),
            x.get("region", "us"),
            int(x.get("count", 1)),
            [tuple(w) for w in x.get("windows", [[0, 24]])],
        )
    rows = []
    for lst in m.search(start, end, a.min_vram, a.gpu, None, a.max_price):
        host, fee = m.quote(lst, start, end)
        rows.append(
            {
                "listing": lst.listing_id,
                "host": lst.host,
                "gpu": lst.gpu,
                "vram_gb": lst.vram_gb,
                "host_amount": host,
                "platform_fee": fee,
                "total": round(host + fee, 2),
            }
        )
    print(json.dumps(rows, indent=2))
    return 0 if rows else 1
