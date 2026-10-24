import unittest
from datetime import datetime, timedelta

from gpu_bnb import BookingError, Market

T0 = datetime(2026, 11, 1, 1)


class Tests(unittest.TestCase):
    def setUp(self):
        self.m = Market()
        self.night = self.m.list_gpu("sam", "RTX 4090", 24, 1.0, windows=[(0, 8)])
        self.always = self.m.list_gpu("lee", "RTX 3090", 24, 0.5)

    def test_windows_and_search(self):
        ids = [l.listing_id for l in self.m.search(T0, T0 + timedelta(hours=3), min_vram=24)]
        self.assertEqual(ids, [self.always.listing_id, self.night.listing_id])
        self.assertEqual(len(self.m.search(T0 + timedelta(hours=10), T0 + timedelta(hours=11))), 1)
        with self.assertRaises(BookingError):
            self.m.book(self.night.listing_id, "r", T0 + timedelta(hours=6), T0 + timedelta(hours=9))

    def test_no_double_booking(self):
        self.m.book(self.always.listing_id, "r", T0, T0 + timedelta(hours=2))
        with self.assertRaises(BookingError):
            self.m.book(self.always.listing_id, "r2", T0 + timedelta(hours=1), T0 + timedelta(hours=3))
        self.m.book(self.always.listing_id, "r2", T0 + timedelta(hours=2), T0 + timedelta(hours=3))

    def test_pricing_and_long_discount(self):
        b = self.m.book(self.always.listing_id, "r", T0, T0 + timedelta(hours=4))
        self.assertEqual((b.host_amount, b.fee, b.total), (2.0, 0.3, 2.3))
        long = self.m.book(self.always.listing_id, "r", T0 + timedelta(days=2), T0 + timedelta(days=3))
        self.assertAlmostEqual(long.host_amount, 0.5 * 24 * 0.9)

    def test_cancellation_policy(self):
        b = self.m.book(self.always.listing_id, "r", T0, T0 + timedelta(hours=4))
        self.assertEqual(self.m.cancel(b.booking_id, T0 - timedelta(hours=2)).refund, 1.15)
        b2 = self.m.book(self.always.listing_id, "r", T0, T0 + timedelta(hours=4))
        self.assertEqual(self.m.cancel(b2.booking_id, T0 - timedelta(days=2)).refund, 2.3)

    def test_completion_reliability_payouts(self):
        b = self.m.book(self.always.listing_id, "r", T0, T0 + timedelta(hours=4))
        self.m.complete(b.booking_id, interrupted_hours=1)
        self.assertEqual(self.m.payouts["lee"], 1.5)
        self.assertLess(self.always.reliability, 1.0)


if __name__ == "__main__":
    unittest.main()
