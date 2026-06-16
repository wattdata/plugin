#!/usr/bin/env python3
"""Extract one version's release notes from a Keep-a-Changelog CHANGELOG.

Usage:
    changelog_extract.py <version> [changelog_path]

Prints the body of the `## [<version>]` section — everything between that
header and the next `## ` header, the header line itself excluded — trimmed of
leading and trailing blank lines, to stdout. The version may be given with or
without a leading `v`.

Exits non-zero with a message on stderr when the version's section is missing
or empty, so the release workflow fails loudly instead of cutting a release
with empty notes.

Release tooling for .github/workflows/release.yml. Python, stdlib-only.
"""
import sys


def extract(version, text):
    """Return the trimmed body of the `## [<version>]` section, or None."""
    lines = text.splitlines()
    header = f"## [{version}]"
    start = None
    for i, line in enumerate(lines):
        if line.startswith(header):
            start = i + 1
            break
    if start is None:
        return None
    body = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    return "\n".join(body)


def main(argv):
    if len(argv) < 2:
        sys.exit("usage: changelog_extract.py <version> [changelog_path]")
    version = argv[1].lstrip("v")
    path = argv[2] if len(argv) > 2 else "CHANGELOG.md"
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        sys.exit(f"cannot read {path}: {e}")
    notes = extract(version, text)
    if not notes or not notes.strip():
        sys.exit(f"no non-empty changelog section for version {version!r} in {path}")
    sys.stdout.write(notes + "\n")


if __name__ == "__main__":
    main(sys.argv)
