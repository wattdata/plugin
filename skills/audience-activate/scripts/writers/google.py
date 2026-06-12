#!/usr/bin/env python3
"""Google Customer Match writer — turns a materialized Watt audience CSV into
Google Customer Match upload files.

Owns its match-rate-critical transform in this one file — the column layout,
the hash-vs-raw decisions, the phone normalizer, and the CLI runner. The
can't-vary plumbing (SHA-256, RFC 4180 escaping, the Watt CSV reader, address
and name parsing, presence checks) is imported from ``_common`` — see that
module's header for why the line falls where it does.

Match-rate-critical, so keep the hashing and column layout stable: Google
SHA-256 hashes email / phone / first / last, leaves country and zip in the
clear, keeps phone in E.164 (the leading ``+``), and writes mobile device IDs
raw to a separate one-column file. (That is the inverse of Meta on country/zip,
the ``+``, and the device ID.) Deterministic — the same input always produces
the same output.

Writes ``google_audience.csv`` and ``google_audience_maid.csv``. Requires
``_common.py`` beside it in ``scripts/writers/``.
"""
import os
import sys

from _common import (
    MAX_PER_TYPE,
    sha256_hex,
    parse_address,
    split_name,
    any_email,
    any_phone,
    any_maid,
    read_watt_csv,
    _csv_field,
)

# entity_find `domains` the Google export needs materialized.
IDENTIFIERS = ["email", "phone", "name", "address", "maid"]


# ----- Google normalization policy -----

def email_lower_trim(e):
    return e.strip().lower() if e else ""


def phone_keep_plus(p):
    """Keep the value as-is — Google wants E.164 (leading ``+``) before hashing."""
    return p if p else ""


def has_required(row):
    """True if Google can match the row. Maid counts — Google has a separate
    device-ID match path, so a maid-only person is still reachable."""
    return any_email(row) or any_phone(row) or any_maid(row)


def write_rows(path, header_row, rows):
    """Write positional rows (lists of cells) as RFC 4180 CSV — CRLF, minimal
    quoting. Positional because Google repeats column headers (Email×3, Phone×3).
    """
    lines = [",".join(_csv_field(h) for h in header_row)]
    for cells in rows:
        lines.append(",".join(_csv_field(c) for c in cells))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")


def write_google(rows, out_dir):
    """Write ``google_audience.csv`` and ``google_audience_maid.csv``.

    Email/phone/first/last are SHA-256-hashed; country and zip ride plaintext.
    Mobile device IDs go to a separate one-column file, unhashed (Google's
    device list cannot mix with other identifiers).
    """
    rows = list(rows)

    path = os.path.join(out_dir, "google_audience.csv")
    header = (["Email"] * MAX_PER_TYPE) + (["Phone"] * MAX_PER_TYPE) + ["First Name", "Last Name", "Country", "Zip"]
    out = []
    for r in rows:
        fn, ln = split_name(r.get("name1") or "")
        addr = parse_address(r.get("address1") or "")
        cells = []
        for i in range(1, MAX_PER_TYPE + 1):
            e = r.get(f"email{i}") or ""
            cells.append(sha256_hex(email_lower_trim(e)) if e else "")
        for i in range(1, MAX_PER_TYPE + 1):
            p = r.get(f"phone{i}") or ""
            cells.append(sha256_hex(phone_keep_plus(p)) if p else "")
        cells += [
            sha256_hex(fn.strip().lower()),
            sha256_hex(ln.strip().lower()),
            "US",            # plaintext — Google does not hash country
            addr["zip5"],    # plaintext — Google does not hash zip
        ]
        out.append(cells)
    write_rows(path, header, out)

    maid_rows = [[r.get("maid1") or ""] for r in rows if (r.get("maid1") or "")]
    write_rows(os.path.join(out_dir, "google_audience_maid.csv"), ["Mobile Device ID"], maid_rows)


USAGE = """usage: google.py [--help] [--list-identifiers]
                 [--input CSV --out-dir DIR] [--prune-missing]

  --list-identifiers  Print the entity_find domains this writer needs and exit.
  --input CSV         Materialized audience CSV (Watt v2 entity_find schema).
  --out-dir DIR       Output directory for the platform file(s).
  --prune-missing     Drop persons with no usable identifier before writing.
                      Default: pass them through.

  Exit codes: 0 success · 2 bad arguments."""


def main(argv):
    args = {"list_identifiers": False, "input": "", "out_dir": "", "prune_missing": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--help", "-h"):
            print(USAGE)
            return 0
        elif a == "--list-identifiers":
            args["list_identifiers"] = True
        elif a == "--input":
            i += 1
            args["input"] = argv[i] if i < len(argv) else ""
        elif a == "--out-dir":
            i += 1
            args["out_dir"] = argv[i] if i < len(argv) else ""
        elif a == "--prune-missing":
            args["prune_missing"] = True
        else:
            print(f"Unknown argument: {a}\n{USAGE}", file=sys.stderr)
            return 2
        i += 1

    if args["list_identifiers"]:
        print(",".join(IDENTIFIERS))
        return 0

    if not (args["input"] and args["out_dir"]):
        print(f"Provide either --list-identifiers, or both --input and --out-dir.\n{USAGE}", file=sys.stderr)
        return 2

    os.makedirs(args["out_dir"], exist_ok=True)
    rows = read_watt_csv(args["input"])
    total_in = len(rows)

    if args["prune_missing"]:
        rows = [r for r in rows if has_required(r)]
        print(f"Prune: dropped {total_in - len(rows)} of {total_in} persons missing required identifiers for platform 'google'.")
    else:
        missing = sum(1 for r in rows if not has_required(r))
        if missing:
            print(f"NOTE: {missing} of {total_in} persons have no required identifier for platform 'google' (not pruned; pass --prune-missing to drop them).")

    write_google(rows, args["out_dir"])
    print(f"OK: wrote google output to {args['out_dir']} (persons in: {len(rows)})")
    return 0


sys.exit(main(sys.argv[1:]))
