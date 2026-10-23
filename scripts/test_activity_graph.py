"""Checks for activity_graph.py (standard library only).  Run: python3 scripts/test_activity_graph.py"""
import datetime as dt
import json
import os
import random
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import activity_graph as ag  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"


def days(counts, start="2026-09-23"):
    d0 = dt.date.fromisoformat(start)
    return [{"date": (d0 + dt.timedelta(i)).isoformat(), "count": c} for i, c in enumerate(counts)]


class RenderChecks(unittest.TestCase):
    def test_random_series_render_valid_and_faithful(self):
        rng = random.Random(23)
        for _ in range(300):
            n = rng.randint(2, 60)
            counts = [rng.choice([0, 0, 1, 3, 10, 47, 118, 999]) for _ in range(n)]
            svg = ag.render(ag.validate(days(counts), n))
            root = ET.fromstring(svg)                                   # well-formed XML
            circles = root.findall(".//%scircle" % NS)
            self.assertEqual(len(circles), n)                           # one point per day
            got = [int(c.find("%stitle" % NS).text.split(": ")[1]) for c in circles]
            self.assertEqual(got, counts)                               # per-day values carried exactly
            self.assertIn("%s contributions" % format(sum(counts), ","), svg)
            ys = [float(c.get("cy")) for c in circles]
            base, top = ag.TOP + (ag.H - ag.TOP - ag.BOTTOM), ag.TOP
            for y, c in zip(ys, counts):
                self.assertTrue(top - 1e-6 <= y <= base + 1e-6)         # inside the plot
                if c == 0:
                    self.assertAlmostEqual(y, base, places=1)           # zero sits on the baseline
            for i in range(n):                                          # height order matches count order
                for j in range(n):
                    if counts[i] > counts[j]:
                        self.assertLess(ys[i], ys[j])

    def test_deterministic(self):
        s = ag.validate(days([5, 0, 9, 118, 2]), 5)
        self.assertEqual(ag.render(s), ag.render(s))

    def test_nice_max_bounds(self):
        for m in range(0, 5000):
            top = ag.nice_max(m)
            self.assertGreaterEqual(top, m)
            self.assertEqual(top % 4, 0)                                 # four integer tick steps
            self.assertLessEqual(top, max(4, 1.6 * m))                  # not wastefully tall


class FailClosed(unittest.TestCase):
    def run_main(self, payload, n=31):
        d = tempfile.mkdtemp()
        src, out = os.path.join(d, "in.json"), os.path.join(d, "out.svg")
        with open(src, "w") as f:
            json.dump(payload, f)
        rc = ag.main(["--from-json", src, "--days", str(n), "--out", out])
        return rc, os.path.exists(out)

    def test_good_input_writes(self):
        self.assertEqual(self.run_main(days([1] * 31)), (0, True))

    def test_bad_inputs_write_nothing(self):
        gap = days([1] * 31)
        del gap[10]
        bad = {
            "empty": [],
            "not_a_list": {"date": "2026-10-01", "count": 1},
            "too_few_days": days([1] * 30),
            "gap_in_dates": gap,
            "negative": days([1] * 30 + [-1]),
            "float_count": days([1] * 30 + [2.0]),
            "bool_count": days([1] * 30 + [True]),
            "bad_date": [{"date": "2026-13-01", "count": 1}] * 31,
            "missing_key": [{"date": "2026-10-01"}] * 31,
        }
        for name, payload in bad.items():
            with self.subTest(name):
                self.assertEqual(self.run_main(payload), (1, False))

    def test_no_token_writes_nothing(self):
        env = os.environ.pop("GITHUB_TOKEN", None)
        try:
            out = os.path.join(tempfile.mkdtemp(), "out.svg")
            self.assertEqual(ag.main(["--user", "x", "--out", out]), 1)
            self.assertFalse(os.path.exists(out))
        finally:
            if env is not None:
                os.environ["GITHUB_TOKEN"] = env


class AntiVacuity(unittest.TestCase):
    """The checks above must be able to fail: a renderer that drops or scales a point is caught."""

    def test_checks_catch_a_planted_fault(self):
        original = ag.render

        def broken(series):
            svg = original(series)
            return re.sub(r'(<circle cx="[^"]+" cy=")([^"]+)', lambda m: m.group(1) + "0.0", svg, count=1)
        ag.render = broken
        try:
            result = unittest.TestResult()
            RenderChecks("test_random_series_render_valid_and_faithful").run(result)
            self.assertFalse(result.wasSuccessful())
        finally:
            ag.render = original


if __name__ == "__main__":
    unittest.main(verbosity=1)
