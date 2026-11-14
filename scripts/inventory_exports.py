#!/usr/bin/env python3
"""Create a metadata-only inventory of approved local CSV exports.

Example:
    python scripts/inventory_exports.py --root /secure/ppmi/export \
        --release-id ppmi-release-2025-05 --output /secure/reports/inventory.json

The output contains file paths, headers, row counts, sizes and checksums only.
It does not copy or serialize participant-level rows.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow execution as `python scripts/inventory_exports.py` from the repository root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.inventory import inventory_csv_tree  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        required=True,
        type=Path,
        help="Directory containing approved CSV exports (kept outside Git)",
    )
    parser.add_argument(
        "--release-id",
        required=True,
        help="Researcher-assigned identifier for the exact export release",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path; defaults to stdout",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    inventory = inventory_csv_tree(args.root, release_id=args.release_id)
    payload = {
        "release_id": args.release_id,
        "root_name": args.root.name,
        "file_count": len(inventory),
        "files": inventory,
    }
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
