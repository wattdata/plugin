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
only (no leading ``+``). Country and zip are among the hashed fields — Meta
matches them in hashed form, so they ride as digests, not plaintext; the mobile-ad
ID is the lone raw match key (hashing it costs the device match). These ten
columns in this hash/raw split are exactly Meta's Customer Match spec — the
intended shape, deterministic: the same input always produces the same output.

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
    any_maid,
    read_watt_csv,
    csv_line,
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
    """True if the row has an identifier Meta can match — email, phone, or a
    mobile-ad ID (Meta matches a MADID-only record)."""
    return any_email(row) or any_phone(row) or any_maid(row)


def write_meta(rows, out_dir):
    """Stream ``meta_audience.csv``, returning ``(total, written)`` — persons
    seen and persons with a matchable identifier.

    PII columns are SHA-256-hashed; ``madid`` rides raw (Meta's one unhashed
    match key). Each person explodes into one row per email/phone pair; a person
    with a mobile-ad ID but no email or phone rides as a single madid-only row
    (Meta matches that). A person with none of the three is skipped, so the write
    path can never emit an all-empty row (Meta requires at least one identifier
    per row).

    Rows are written as they're transformed — the input streams in from
    ``read_watt_csv`` and each output row goes straight to the open file — so the
    writer holds one person at a time, never the whole audience.
    """
    path = os.path.join(out_dir, "meta_audience.csv")
    headers = ["email", "phone", "fn", "ln", "country", "zip", "ct", "st", "external_id", "madid"]
    total = written = 0
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(csv_line(headers))
        for r in rows:
            total += 1
            if not has_required(r):
                continue
            written += 1
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
            madid = base["madid"]
            for i in range(max(len(emails), len(phones), 1)):
                row_out = dict(base)
                row_out["email"] = emails[i] if i < len(emails) else ""
                row_out["phone"] = phones[i] if i < len(phones) else ""
                if not row_out["email"] and not row_out["phone"] and not madid:
                    continue
                f.write(csv_line(row_out.get(h, "") for h in headers))
    return total, written


USAGE = """usage: meta.py [--help] [--list-identifiers]
               [--input CSV --out-dir DIR]

  --list-identifiers  Print the entity_find domains this writer needs and exit.
  --input CSV         Materialized audience CSV (Watt v2 entity_find schema).
  --out-dir DIR       Output directory for the platform file(s).

  A person with no identifier Meta can match produces no row. The reported
  count is the people actually written.

  Exit codes: 0 success · 2 bad arguments."""


def main(argv):
    args = {"list_identifiers": False, "input": "", "out_dir": ""}
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
    total, written = write_meta(read_watt_csv(args["input"]), args["out_dir"])
    skipped = total - written
    note = f"; {skipped} skipped with no identifier Meta can match" if skipped else ""
    print(f"OK: wrote {written} of {total} persons to {args['out_dir']}{note}")
    return 0


sys.exit(main(sys.argv[1:]))
