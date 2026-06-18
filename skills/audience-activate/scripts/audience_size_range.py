#!/usr/bin/env python3
"""Turn an exported-people count into the expected audience size on the platform.

When an export file is uploaded, the platform reaches only the share of
people it already has on its own side — always fewer than the count we hand over,
and driven by factors outside Watt's control (the platform's identity graph, the
customer's ad account, identifier recency, channel). Watt's language for that
linked subset is the **expected audience size** — the real-people range the
platform will likely reach. We never quote a percentage (it anchors the customer
on a number we don't control); we translate it into a concrete **count range** for
*this* export's size, so the expectation is set in people, not a rate.

This script is the **single source of the band**: the same low/high fraction is
applied everywhere the range is shown (the confirmation gate and the delivery
reconciliation), so the two can never drift. The band is a deliberately
platform-agnostic, conservative estimate — change it here and every surface moves
together.

Usage:
    python3 audience_size_range.py <people_count>

Emits one line on stdout — the human-rounded range string the skill quotes,
e.g. ``300K–480K``. Stdlib-only, zero-dep; reads no files, no network.
"""
import sys

# The expected-audience-size band — the ONE place it lives. Low/high fractions of
# the exported people we tell the customer to realistically expect the platform to
# reach. Platform-agnostic and conservative on purpose; the percentage itself is
# never shown — only the count range it produces.
BAND_LOW = 0.50
BAND_HIGH = 0.80


def _round_human(n):
    """House-style rounding: 417K, 1.4M — integers under 1K, K under 1M, M above."""
    n = int(round(n))
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return "%dK" % round(n / 1000)
    s = "%.1f" % (n / 1_000_000)
    return s[:-2] + "M" if s.endswith(".0") else s + "M"


def size_range(people):
    """Return the rounded ``low–high`` expected-audience-size range for a people count."""
    low = _round_human(people * BAND_LOW)
    high = _round_human(people * BAND_HIGH)
    return low if low == high else "%s–%s" % (low, high)


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: audience_size_range.py <people_count>\n")
        return 2
    try:
        people = int(float(argv[1]))
    except ValueError:
        sys.stderr.write("people_count must be a number\n")
        return 2
    if people < 0:
        sys.stderr.write("people_count must be non-negative\n")
        return 2
    sys.stdout.write(size_range(people) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
