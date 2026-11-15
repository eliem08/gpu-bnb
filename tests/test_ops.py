import contextlib
import io
import os
import tempfile
import unittest

from gpu_bnb.__main__ import main
from gpu_bnb.ops import load

SLOT = ["--start", "2026-12-01T18:00", "--end", "2026-12-01T22:00"]


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class GpuOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.s = ["--store", os.path.join(self.tmp.name, "gpu.json")]
        self.ok("host-list", "maya", "--gpu", "RTX 4090", "--vram-gb", "24", "--hourly", "0.6", "--window", "18-24")

    def tearDown(self):
        self.tmp.cleanup()

    def ok(self, *argv):
        code, out = run(*argv, *self.s)
        self.assertEqual(code, 0, out)
        return out

    def test_find_book_complete_and_pay_the_host(self):
        self.assertIn("L1", self.ok("find", *SLOT, "--min-vram", "24"))
        self.assertIn("$2.76", self.ok("book", "L1", "sam", *SLOT))
        self.assertIn("nothing free", self.ok("find", *SLOT))  # the only GPU is taken
        self.ok("complete", "B2")
        m = load(self.s[1])
        self.assertEqual(
            (m.payouts["maya"], m.bookings["B2"].status, m.listings["L1"].delivered), (2.4, "completed", 1)
        )
        self.assertEqual(run("complete", "B2", *self.s)[0], 1)  # never paid twice

    def test_double_booking_and_out_of_hours_are_refused(self):
        self.ok("book", "L1", "sam", *SLOT)
        self.assertEqual(run("book", "L1", "ann", *SLOT, *self.s)[0], 1)
        early = ["--start", "2026-12-01T10:00", "--end", "2026-12-01T12:00"]
        self.assertEqual(run("book", "L1", "ann", *early, *self.s)[0], 1)
        self.assertEqual(len(load(self.s[1]).bookings), 1)

    def test_interruption_refunds_renter_and_cuts_the_fee(self):
        self.ok("book", "L1", "sam", *SLOT)
        self.assertIn("refund $0.69", self.ok("complete", "B2", "--interrupted-hours", "1"))
        out = self.ok("payouts")
        self.assertIn("$1.80", out)
        self.assertIn("platform fees    $0.27", out)

    def test_host_cancellation_refunds_in_full(self):
        self.ok("book", "L1", "sam", *SLOT)
        self.assertIn("refund $2.76 of $2.76", self.ok("cancel", "B2", "--by", "host"))
        self.assertEqual(load(self.s[1]).listings["L1"].failed, 1)

    def test_bad_input_is_refused(self):
        for argv in (
            ["find", "--start", "tomorrow", "--end", "2026-12-01T22:00"],
            ["book", "L9", "sam", *SLOT],
            ["host-list", "x", "--gpu", "g", "--vram-gb", "8", "--hourly", "1", "--window", "22-6"],
            ["host-list", "x", "--gpu", "g", "--vram-gb", "8", "--hourly", "-1"],
            ["cancel", "B9"],
        ):
            with self.subTest(argv=argv):
                self.assertEqual(run(*argv, *self.s)[0], 1)


if __name__ == "__main__":
    unittest.main()
