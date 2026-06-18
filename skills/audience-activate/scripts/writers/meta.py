#!/usr/bin/env python3
"""Meta audience writer — turns a materialized Watt audience CSV into a
Meta upload file.

Owns its audience-size-critical transform in this one file — the column layout,
the hash-vs-raw decisions, the phone normalizer, and the CLI runner. The
can't-vary plumbing (SHA-256, RFC 4180 escaping, the Watt CSV reader, address
and name parsing, presence checks) is imported from ``_common`` — see that
module's header for why the line falls where it does.

Audience-size-critical, so keep the hashing and column layout stable: Meta SHA-256
hashes every field except the mobile-ad ID (sent raw), and wants phone digits
only (no leading ``+``). Deterministic — the same input always produces the
same output.

Requires ``_common.py`` beside it in ``scripts/writers/``.
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
    read_watt_csv,
    _csv_field,
)

# entity_find `domains` the Meta export needs materialized.
IDENTIFIERS = ["email", "phone", "name", "address", "maid"]


# ----- Meta normalization policy -----

def email_lower_trim(e):
    return e.strip().lower() if e else ""


def phone_strip_plus(p):
    """Drop leading ``+`` — Meta wants digits only, country code included."""
    if not p:
        return ""
    i = 0
    while i < len(p) and p[i] == "+":
        i += 1
    return p[i:]


def has_required(row):
    """True if the row has an identifier Meta can match on (email or phone)."""
    return any_email(row) or any_phone(row)


def write_csv(path, headers, rows):
    """Write rows (dicts) as RFC 4180 CSV — CRLF line endings, minimal quoting."""
    lines = [",".join(_csv_field(h) for h in headers)]
    for r in rows:
        lines.append(",".join(_csv_field(r.get(h, "")) for h in headers))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")


def write_meta(rows, out_dir):
    """Write ``meta_audience.csv``.

    PII columns are SHA-256-hashed; ``madid`` rides raw (Meta's one unhashed
    match key). Each person explodes into one row per email/phone pair, and a
    row with neither is dropped (Meta requires at least one identifier per row).
    """
    path = os.path.join(out_dir, "meta_audience.csv")
    headers = ["email", "phone", "fn", "ln", "country", "zip", "ct", "st", "external_id", "madid"]
    out = []
    for r in rows:
        fn, ln = split_name(r.get("name1") or "")
        addr = parse_address(r.get("address1") or "")
        base = {
            "fn": sha256_hex(fn.strip().lower()),
            "ln": sha256_hex(ln.strip().lower()),
            "country": sha256_hex("us"),
            "zip": sha256_hex(addr["zip5"]) if addr["zip5"] else "",
            "ct": sha256_hex(addr["city"].lower()) if addr["city"] else "",
            "st": sha256_hex(addr["state"].lower()) if addr["state"] else "",
            "external_id": sha256_hex(str(r.get("entity_id") or "")),
            "madid": (r.get("maid1") or "").lower(),  # raw — Meta's one unhashed match key
        }
        emails, phones = [], []
        for i in range(1, MAX_PER_TYPE + 1):
            if r.get(f"email{i}"):
                emails.append(sha256_hex(email_lower_trim(r[f"email{i}"])))
            if r.get(f"phone{i}"):
                phones.append(sha256_hex(phone_strip_plus(r[f"phone{i}"])))
        for i in range(max(len(emails), len(phones), 1)):
            row_out = dict(base)
            row_out["email"] = emails[i] if i < len(emails) else ""
            row_out["phone"] = phones[i] if i < len(phones) else ""
            if not row_out["email"] and not row_out["phone"]:
                continue
            out.append(row_out)
    write_csv(path, headers, out)


USAGE = """usage: meta.py [--help] [--list-identifiers]
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
        print(f"Prune: dropped {total_in - len(rows)} of {total_in} persons missing required identifiers for platform 'meta'.")
    else:
        missing = sum(1 for r in rows if not has_required(r))
        if missing:
            print(f"NOTE: {missing} of {total_in} persons have no required identifier for platform 'meta' (not pruned; pass --prune-missing to drop them).")

    write_meta(rows, args["out_dir"])
    print(f"OK: wrote meta output to {args['out_dir']} (persons in: {len(rows)})")
    return 0


sys.exit(main(sys.argv[1:]))
