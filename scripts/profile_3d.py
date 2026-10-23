#!/usr/bin/env python3
"""Public-only preflight and SVG validation for the pinned 3D renderer.

Use only the workflow's repository-scoped GITHUB_TOKEN, never an owner PAT.
GitHub can expose anonymized private counts on a public calendar. Refuse those
calendars instead of silently including them. No private repositories are queried.
"""
import argparse
import json
import os
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2000/svg}"
QUERY = """query($login:String!){user(login:$login){contributionsCollection{
  hasAnyRestrictedContributions restrictedContributionsCount
}}}"""


def require_public(data):
    if data.get("errors"):
        raise ValueError("GitHub returned GraphQL errors; not rendering")
    collection = data["data"]["user"]["contributionsCollection"]
    if (collection.get("hasAnyRestrictedContributions") is not False
            or type(collection.get("restrictedContributionsCount")) is not int
            or collection["restrictedContributionsCount"] != 0):
        raise ValueError("Calendar contains restricted counts; public-only render stopped")


def guard(user):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
                 "Content-Type": "application/json", "User-Agent": "profile-3d-public-only"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        require_public(json.load(response))
    print("Public-only guard passed: zero restricted contributions")


def validate(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Expected a regular SVG file")
    data = path.read_bytes()
    if not 1000 <= len(data) <= 2_000_000:
        raise ValueError("Unexpected SVG size")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("SVG must not contain a DTD or entities")
    root = ET.fromstring(data)
    if root.tag != NS + "svg" or root.get("viewBox") != "0 0 1280 850":
        raise ValueError("Unexpected SVG root or dimensions")
    allowed = {"svg", "style", "rect", "g", "animateTransform", "animate",
               "path", "polygon", "line", "circle", "text", "title", "desc",
               "defs", "pattern", "polyline"}
    for element in root.iter():
        if element.tag not in {NS + tag for tag in allowed}:
            raise ValueError("Unexpected SVG element")
        for key, value in element.attrib.items():
            local = key.rsplit("}", 1)[-1].lower()
            if local.startswith("on") or local in {"href", "src"}:
                raise ValueError("SVG must not contain events or resource references")
            if "url(" in value.lower() and not value.lower().startswith("url(#"):
                raise ValueError("External SVG resource")
        if element.tag == NS + "style":
            css = (element.text or "").lower()
            if "@import" in css or "url(" in css:
                raise ValueError("External CSS resource")
    if not root.findall(".//" + NS + "animateTransform"):
        raise ValueError("Expected growing-bar animation")
    if len(root.findall(".//" + NS + "rect")) < 300:
        raise ValueError("Expected a full contribution calendar")
    print("Validated animated, self-contained 1280x850 SVG (%d bytes)" % len(data))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("guard").add_argument("--user", required=True)
    sub.add_parser("validate").add_argument("path")
    args = parser.parse_args()
    if args.command == "guard":
        guard(args.user)
    else:
        validate(args.path)


if __name__ == "__main__":
    main()
