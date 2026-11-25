#!/usr/bin/env python3
"""Maintain local, manually observed Xiaohongshu post records."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile


DEFAULT_FILE = Path(__file__).with_name("posts.jsonl")
POST_ID = re.compile(r"^[0-9a-f]{24}$")
STATUSES = ("partial", "complete")


def read_records(path):
    records = {}
    if not path.exists():
        return records
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                post_id = record["post_id"]
                if not isinstance(post_id, str) or not POST_ID.fullmatch(post_id):
                    raise ValueError("invalid post_id")
                if record.get("status") not in STATUSES:
                    raise ValueError("invalid status")
                if post_id in records:
                    raise ValueError("duplicate post_id")
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            records[post_id] = record
    return records


def write_records(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            for record in records.values():
                stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def upsert(records, supplied):
    if not isinstance(supplied, dict):
        raise ValueError("input must be one JSON object")
    post_id = supplied.get("post_id")
    if not isinstance(post_id, str) or not POST_ID.fullmatch(post_id):
        raise ValueError("post_id must be a 24-character lowercase hexadecimal ID")
    if supplied.get("status") not in STATUSES:
        raise ValueError("status must be partial or complete")
    merged = {**records.get(post_id, {}), **supplied}
    merged["hash_id"] = hashlib.sha256(f"xiaohongshu:{post_id}".encode()).hexdigest()
    records[post_id] = merged
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="JSONL store path")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("upsert", help="read one JSON record from stdin")
    list_parser = commands.add_parser("list", help="list post IDs by status")
    list_parser.add_argument("--status", choices=STATUSES, required=True)
    commands.add_parser("validate", help="validate records and their hashes")
    args = parser.parse_args()
    try:
        records = read_records(args.file)
        if args.command == "upsert":
            result = upsert(records, json.load(sys.stdin))
            write_records(args.file, records)
            print(json.dumps(result, ensure_ascii=False))
        elif args.command == "list":
            for post_id, record in records.items():
                if record["status"] == args.status:
                    print(post_id)
        else:
            for post_id, record in records.items():
                expected = hashlib.sha256(f"xiaohongshu:{post_id}".encode()).hexdigest()
                if record.get("hash_id") != expected:
                    raise ValueError(f"{post_id}: missing or incorrect hash_id")
            print(f"Valid: {len(records)} records")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
