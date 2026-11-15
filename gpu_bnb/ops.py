"""Operating commands: run the GPU marketplace against a persistent store (also served by the web app).

Bookings and payouts here are a ledger. Charging renters and paying hosts is done by the operator's payment
provider; `payouts` prints what is owed.
"""

import itertools
import json
import os
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime

from .core import Booking, BookingError, Listing, Market

OPS = ("host-list", "find", "book", "cancel", "complete", "listings", "bookings", "payouts")


def when(text: str) -> datetime:
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        raise BookingError(f"{text!r} is not a date-time like 2026-12-01T18:00") from None


def load(path: str) -> Market:
    m = Market()
    try:
        with open(path, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except FileNotFoundError:
        return m
    if not isinstance(doc, dict) or "listings" not in doc:
        raise BookingError(f"{path}: not a gpu-bnb store")
    for k, v in doc["listings"].items():
        v["windows"] = [tuple(w) for w in v["windows"]]
        m.listings[k] = Listing(**v)
    for k, v in doc["bookings"].items():
        v["start"], v["end"] = datetime.fromisoformat(v["start"]), datetime.fromisoformat(v["end"])
        m.bookings[k] = Booking(**v)
    m.payouts = defaultdict(float, doc.get("payouts", {}))
    m._ids = itertools.count(int(doc.get("next_id", 1)))
    return m


def save(m: Market, path: str):
    next_id = next(m._ids)
    m._ids = itertools.count(next_id)
    bookings = {}
    for k, b in m.bookings.items():
        bookings[k] = {**asdict(b), "start": b.start.isoformat(), "end": b.end.isoformat()}
    doc = {
        "listings": {k: asdict(v) for k, v in m.listings.items()},
        "bookings": bookings,
        "payouts": dict(m.payouts),
        "next_id": next_id,
    }
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
    os.replace(tmp, path)


def _window(text: str) -> tuple[int, int]:
    try:
        a, b = (int(x) for x in text.split("-"))
    except ValueError:
        raise BookingError(f"window must look like 18-24 (hours), got {text!r}") from None
    if not 0 <= a < b <= 24:
        raise BookingError(f"window hours must satisfy 0 <= start < end <= 24, got {text!r}")
    return a, b


def add_ops(sub):
    store = os.environ.get("GPU_BNB_STORE", "gpu-bnb.json")
    p = sub.add_parser("host-list", help="a host lists a GPU for rent")
    p.add_argument("host")
    p.add_argument("--gpu", required=True, help="model, e.g. 'RTX 4090'")
    p.add_argument("--vram-gb", type=int, required=True)
    p.add_argument("--hourly", type=float, required=True, help="USD per hour")
    p.add_argument("--region", default="us")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--window", action="append", default=[], help="daily hours available, e.g. 18-24 (repeatable)")
    p = sub.add_parser("find", help="GPUs free for a time slot, best value first")
    p.add_argument("--start", required=True, help="e.g. 2026-12-01T18:00")
    p.add_argument("--end", required=True)
    p.add_argument("--min-vram", type=int, default=0)
    p.add_argument("--gpu")
    p.add_argument("--region")
    p.add_argument("--max-price", type=float)
    p = sub.add_parser("book", help="reserve a listing for a slot")
    p.add_argument("listing_id")
    p.add_argument("renter")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p = sub.add_parser("cancel", help="cancel a booking; the refund follows the cancellation policy")
    p.add_argument("booking_id")
    p.add_argument("--by", choices=["renter", "host"], default="renter")
    p = sub.add_parser("complete", help="close a finished booking and credit the host")
    p.add_argument("booking_id")
    p.add_argument("--interrupted-hours", type=float, default=0.0, help="hours the GPU was unavailable")
    sub.add_parser("listings", help="every listing with its reliability")
    sub.add_parser("bookings", help="every booking and its status")
    sub.add_parser("payouts", help="what each host is owed, and refunds due to renters")
    for name in OPS:
        sub.choices[name].add_argument("--store", default=store)


def _get(table: dict, key: str, what: str):
    if key not in table:
        raise BookingError(f"no {what} {key!r}")
    return table[key]


def run_ops(a) -> int:
    try:
        m = load(a.store)
        _run(m, a)
        save(m, a.store)
        return 0
    except BookingError as e:
        print(f"refused: {e}")
        return 1


def _run(m: Market, a):
    c = a.cmd
    if c == "host-list":
        windows = [_window(w) for w in a.window] or [(0, 24)]
        l = m.list_gpu(a.host, a.gpu, a.vram_gb, a.hourly, a.region, a.count, windows)
        print(f"{l.listing_id}: {l.count} x {l.gpu} {l.vram_gb}GB at ${l.hourly:.2f}/h in {l.region}")
    elif c == "find":
        start, end = when(a.start), when(a.end)
        found = m.search(start, end, a.min_vram, a.gpu, a.region, a.max_price)
        for l in found:
            host, fee = m.quote(l, start, end)
            print(
                f"{l.listing_id:<5}{l.gpu:<16}{l.vram_gb:>3}GB  ${host + fee:>8.2f} total  {l.reliability:.0%} reliable"
            )
        if not found:
            print("nothing free for that slot")
    elif c == "book":
        _get(m.listings, a.listing_id, "listing")
        b = m.book(a.listing_id, a.renter, when(a.start), when(a.end))
        print(f"{b.booking_id} confirmed: ${b.total:.2f} (host ${b.host_amount:.2f} + fee ${b.fee:.2f})")
    elif c == "cancel":
        _get(m.bookings, a.booking_id, "booking")
        b = m.cancel(a.booking_id, datetime.now(), a.by)
        print(f"{b.booking_id} cancelled by {a.by}: refund ${b.refund:.2f} of ${b.total:.2f}")
    elif c == "complete":
        _get(m.bookings, a.booking_id, "booking")
        b = m.complete(a.booking_id, a.interrupted_hours)
        print(f"{b.booking_id} completed" + (f"; refund ${b.refund:.2f} for the interruption" if b.refund else ""))
    elif c == "listings":
        for l in m.listings.values():
            hours = ", ".join(f"{s}-{e}" for s, e in l.windows)
            print(
                f"{l.listing_id:<5}{l.host:<14}{l.count} x {l.gpu:<14}${l.hourly:>6.2f}/h  {l.reliability:.0%}  {hours}"
            )
        if not m.listings:
            print("no listings yet")
    elif c == "bookings":
        for b in m.bookings.values():
            print(
                f"{b.booking_id:<5}{b.status:<11}{b.listing_id:<5}{b.renter:<14}{b.start:%Y-%m-%d %H:%M} to {b.end:%H:%M}"
            )
        if not m.bookings:
            print("no bookings yet")
    else:
        for host, amount in sorted(m.payouts.items()):
            print(f"pay host {host:<14} ${amount:,.2f}")
        refunds = sum(b.refund for b in m.bookings.values())
        # an interruption refund returns its share of the fee too
        fees = sum(b.fee * (1 - b.refund / b.total) for b in m.bookings.values() if b.status == "completed")
        print(f"refunds due      ${refunds:,.2f}\nplatform fees    ${fees:,.2f}")
