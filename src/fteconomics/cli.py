"""Command-line interface for fault-tolerance resource estimation.

Examples
--------
    fteconomics estimate --profile baseline
    fteconomics report --output reports/shor-rsa2048-resource-estimate.md
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .algorithm_cost import SHOR_RSA_2048
from .cost_model import estimate_resources
from .hardware_profiles import DEFAULT_PROFILES
from .report import write_report


def _cmd_estimate(args: argparse.Namespace) -> int:
    if args.profile not in DEFAULT_PROFILES:
        raise SystemExit(f"unknown profile '{args.profile}'; choose from {sorted(DEFAULT_PROFILES)}")
    estimate = estimate_resources(SHOR_RSA_2048, DEFAULT_PROFILES[args.profile])
    print(estimate.model_dump_json(indent=2))
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    estimate = write_report(args.output)
    print(f"wrote report to {args.output}")
    print(f"baseline: {estimate.total_physical_qubits:,} physical qubits, "
          f"d={estimate.code_distance}, {estimate.runtime_hours:.1f} h")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fteconomics", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    estimate = sub.add_parser("estimate", help="Print a single resource estimate.")
    estimate.add_argument("--profile", default="baseline", help="Hardware profile name.")
    estimate.set_defaults(func=_cmd_estimate)

    report = sub.add_parser("report", help="Generate the markdown technical report.")
    report.add_argument("--output", default="reports/shor-rsa2048-resource-estimate.md")
    report.set_defaults(func=_cmd_report)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
