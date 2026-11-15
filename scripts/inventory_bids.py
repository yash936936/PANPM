"""Build an aggregate-only inventory of a locally downloaded BIDS dataset.

Example:
    python scripts/inventory_bids.py --root /data/ds005892 --output /secure/phase0/bids.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.bids_inventory import inventory_bids_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="Local BIDS dataset root")
    parser.add_argument("--output", type=Path, help="Aggregate JSON output; defaults to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = inventory_bids_dataset(args.root)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output.resolve()
        repository_root = ROOT.resolve()
        if output == repository_root or repository_root in output.parents:
            raise ValueError("Aggregate output must be outside the PANPM Git worktree")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
