"""Privacy and unsafe-SVG regression checks. No network requests."""
import tempfile
import unittest
from pathlib import Path

import profile_3d as graph


class PrivacyChecks(unittest.TestCase):
    def payload(self, **values):
        return {"data": {"user": {"contributionsCollection": values}}}

    def test_public_only(self):
        graph.require_public(self.payload(hasAnyRestrictedContributions=False,
                                          restrictedContributionsCount=0))

    def test_private_counts_and_malformed_responses_fail(self):
        for payload in [self.payload(hasAnyRestrictedContributions=True,
                                     restrictedContributionsCount=1),
                        self.payload(hasAnyRestrictedContributions=False,
                                     restrictedContributionsCount=1),
                        self.payload(hasAnyRestrictedContributions=False,
                                     restrictedContributionsCount=False),
                        self.payload(), {"errors": [{"message": "denied"}]},
                        {"data": {"user": None}}]:
            with self.subTest(payload=payload), self.assertRaises((ValueError, KeyError, TypeError)):
                graph.require_public(payload)


class SvgChecks(unittest.TestCase):
    def validate(self, extra="", attrs="", css=""):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 850" %s>'
               '<style>%s</style><g><animateTransform attributeName="transform" '
               'type="translate" values="0 0;0 1" dur="3s"/></g>%s%s</svg>'
               % (attrs, css, '<rect width="1" height="1"/>' * 366, extra))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph.svg"
            path.write_text(svg)
            graph.validate(path)

    def test_safe_animation(self):
        self.validate()

    def test_active_or_external_content_rejected(self):
        for kwargs in [dict(extra="<script>alert(1)</script>"),
                       dict(extra='<image href="https://example.com/pixel"/>'),
                       dict(extra='<foreignObject/>'), dict(attrs='onload="bad()"'),
                       dict(css='@import "https://example.com/style";'),
                       dict(extra='<rect fill="url(https://example.com/a)"/>')]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.validate(**kwargs)


if __name__ == "__main__":
    unittest.main()
