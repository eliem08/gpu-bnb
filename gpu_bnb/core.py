"""Listings, availability, bookings, pricing and payouts for a peer-to-peer GPU marketplace."""

from __future__ import annotations

import itertools
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

__all__ = ["Listing", "Booking", "Market", "BookingError", "PLATFORM_FEE"]

PLATFORM_FEE = 0.15


class BookingError(Exception):
    pass


@dataclass
class Listing:
    listing_id: str
    host: str
    gpu: str
    vram_gb: int
    count: int
    hourly: float
    region: str
    windows: list  # [(start_hour, end_hour)] daily, end exclusive; (0, 24) = always
    delivered: int = 0
    failed: int = 0

    @property
    def reliability(self) -> float:
        return (self.delivered + 2) / (self.delivered + self.failed + 2)

    def available(self, start: datetime, end: datetime) -> bool:
        t = start
        while t < end:
            if not any(a <= t.hour < b for a, b in self.windows):
                return False
            t += timedelta(hours=1)
        return True


@dataclass
class Booking:
    booking_id: str
    listing_id: str
    renter: str
    start: datetime
    end: datetime
    host_amount: float
    fee: float
    status: str = "confirmed"
    refund: float = 0.0

    @property
    def total(self):
        return round(self.host_amount + self.fee, 2)


def _overlaps(a0, a1, b0, b1):
    return a0 < b1 and b0 < a1


class Market:
    def __init__(self):
        self.listings: dict[str, Listing] = {}
        self.bookings: dict[str, Booking] = {}
        self.payouts: dict[str, float] = defaultdict(float)
        self._ids = itertools.count(1)

    def list_gpu(self, host, gpu, vram_gb, hourly, region="us", count=1, windows=((0, 24),)) -> Listing:
        lid = f"L{next(self._ids)}"
        self.listings[lid] = Listing(lid, host, gpu, vram_gb, count, hourly, region, list(windows))
        return self.listings[lid]

    def _free(self, lid, start, end):
        return not any(
            b.listing_id == lid and b.status == "confirmed" and _overlaps(start, end, b.start, b.end)
            for b in self.bookings.values()
        )

    def search(
        self, start: datetime, end: datetime, min_vram=0, gpu=None, region=None, max_price=None
    ) -> list[Listing]:
        res = [
            l
            for l in self.listings.values()
            if l.vram_gb >= min_vram
            and (not gpu or gpu.lower() in l.gpu.lower())
            and (not region or l.region == region)
            and (max_price is None or l.hourly <= max_price)
            and l.available(start, end)
            and self._free(l.listing_id, start, end)
        ]
        return sorted(res, key=lambda l: (l.hourly / l.reliability, -l.vram_gb))

    @staticmethod
    def quote(listing: Listing, start: datetime, end: datetime) -> tuple[float, float]:
        hours = (end - start).total_seconds() / 3600
        if hours <= 0:
            raise BookingError("end must be after start")
        discount = 0.10 if hours >= 24 else 0.0
        host = round(listing.hourly * hours * (1 - discount), 2)
        return host, round(host * PLATFORM_FEE, 2)

    def book(self, listing_id, renter, start, end) -> Booking:
        l = self.listings[listing_id]
        if not l.available(start, end):
            raise BookingError("outside host availability windows")
        if not self._free(listing_id, start, end):
            raise BookingError("slot already booked")
        host, fee = self.quote(l, start, end)
        b = Booking(f"B{next(self._ids)}", listing_id, renter, start, end, host, fee)
        self.bookings[b.booking_id] = b
        return b

    def cancel(self, booking_id, now: datetime, by: str = "renter") -> Booking:
        b = self.bookings[booking_id]
        if b.status != "confirmed":
            raise BookingError("booking not active")
        if by == "host":
            b.refund = b.total
            self.listings[b.listing_id].failed += 1
        elif now <= b.start - timedelta(hours=24):
            b.refund = b.total
        elif now < b.start:
            b.refund = round(b.total * 0.5, 2)
            self.payouts[self.listings[b.listing_id].host] += round(b.host_amount * 0.5, 2)
        b.status = "cancelled"
        return b

    def complete(self, booking_id, interrupted_hours: float = 0.0) -> Booking:
        b = self.bookings[booking_id]
        l = self.listings[b.listing_id]
        hours = (b.end - b.start).total_seconds() / 3600
        share = max(0.0, 1 - interrupted_hours / hours)
        if interrupted_hours:
            l.failed += 1
            b.refund = round(b.total * (1 - share), 2)
        else:
            l.delivered += 1
        self.payouts[l.host] += round(b.host_amount * share, 2)
        b.status = "completed"
        return b
