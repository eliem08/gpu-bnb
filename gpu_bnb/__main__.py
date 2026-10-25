import argparse
import csv
import os
import sys
from datetime import datetime

from .core import BookingError, Market


def demo():
    m = Market()
    m.list_gpu("sam", "RTX 4090", 24, 0.45, windows=[(0, 8), (13, 17)])
    m.list_gpu("lee", "RTX 3090", 24, 0.30)
    m.list_gpu("ana", "RTX 6000 Ada", 48, 0.95)
    start, end = datetime(2026, 10, 25, 1), datetime(2026, 10, 25, 6)
    print(f"Search 24GB+, {start:%a %H:%M}-{end:%H:%M}:")
    for l in m.search(start, end, min_vram=24):
        host, fee = m.quote(l, start, end)
        print(f"  {l.listing_id} {l.gpu:<14} {l.vram_gb}GB ${l.hourly:.2f}/h  host {l.host:<4} total ${host + fee:.2f}")
    b = m.book("L1", "researcher", start, end)
    print(f"Booked {b.booking_id}: ${b.total:.2f} (host ${b.host_amount}, fee ${b.fee})")
    try:
        m.book("L1", "other", datetime(2026, 10, 25, 3), datetime(2026, 10, 25, 4))
    except BookingError as e:
        print(f"Double-book blocked: {e}")
    m.complete(b.booking_id)
    print("Payouts:", dict(m.payouts))


def _run(argv=None):
    ap = argparse.ArgumentParser(prog="gpu-bnb")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo")
    ap.parse_args(argv)
    demo()
    return 0


def main(argv=None):
    """Run the CLI; a bad input file or argument exits 2 with a one-line error instead of a traceback.

    Set AGENT_ECONOMY_DEBUG=1 to see the full traceback.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    try:
        return _run(argv)
    except (OSError, ValueError, KeyError, csv.Error) as e:
        if os.environ.get("AGENT_ECONOMY_DEBUG"):
            raise
        msg = e.args[0] if isinstance(e, KeyError) and e.args else e
        print(f"error: {msg}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
