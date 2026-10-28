"""Sell-ready billing shape: monthly checkout carries the 14-day trial, /pricing notes it."""

import pathlib
import tempfile
import unittest

from gpu_bnb import web

ENV = {
    "STRIPE_SECRET_KEY": "sk_test_x",
    "STRIPE_WEBHOOK_SECRET": "whsec_test",
    "STRIPE_PRICES": "host-pro=price_1,operator=price_2",
    "PUBLIC_URL": "https://example.test",
}


class BillingTests(unittest.TestCase):
    def test_monthly_checkout_carries_14_day_trial(self):
        with tempfile.TemporaryDirectory() as t:
            srv = web.make_server("127.0.0.1", 0, pathlib.Path(t), env=ENV)
            try:
                billing = srv.RequestHandlerClass.billing
                sent = {}
                billing._stripe = lambda path, form: sent.update(form) or {"url": "https://checkout.test/s"}
                self.assertEqual(billing.checkout("host-pro"), "https://checkout.test/s")
                self.assertEqual(sent["mode"], "subscription")
                self.assertEqual(sent["line_items[0][price]"], "price_1")
                self.assertEqual(sent["subscription_data[trial_period_days]"], "14")
            finally:
                srv.server_close()

    def test_pricing_page_notes_trial_and_free_host(self):
        with tempfile.TemporaryDirectory() as t:
            srv = web.make_server("127.0.0.1", 0, pathlib.Path(t), env=ENV)
            try:
                page = web.pricing_page(srv.RequestHandlerClass.billing)
                self.assertIn("14-day free trial", page)
                self.assertIn("Host is free", page)
            finally:
                srv.server_close()


if __name__ == "__main__":
    unittest.main()
