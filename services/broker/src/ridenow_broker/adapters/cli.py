"""CLI inbound adapter for the Broker service."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import TYPE_CHECKING

from ridenow_broker.bootstrap.runtime import create_runtime
from ridenow_broker.core.application import (
    IssueSubmissionCommand,
    RequestRideCommand,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for supported Broker commands."""

    parser = argparse.ArgumentParser(prog="ridenow-broker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health")

    request_ride = subparsers.add_parser("request-ride")
    request_ride.add_argument("--customer-id", required=True)
    request_ride.add_argument("--pickup-lat", type=float, required=True)
    request_ride.add_argument("--pickup-lon", type=float, required=True)
    request_ride.add_argument("--dropoff-lat", type=float, required=True)
    request_ride.add_argument("--dropoff-lon", type=float, required=True)

    submit_issue = subparsers.add_parser("submit-issue")
    submit_issue.add_argument("--ride-id", required=True)
    submit_issue.add_argument("--customer-id", required=True)
    submit_issue.add_argument("--category", required=True)
    submit_issue.add_argument("--description", required=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Broker CLI adapter and print JSON responses."""

    args = build_parser().parse_args(list(argv) if argv is not None else None)
    runtime = create_runtime()

    if args.command == "health":
        health = runtime.health_check.execute()
        payload = {"service": health.service, "status": health.status}
    elif args.command == "request-ride":
        ride = asyncio.run(
            runtime.request_ride.execute(
                RequestRideCommand(
                    customer_id=args.customer_id,
                    pickup={"lat": args.pickup_lat, "lon": args.pickup_lon},
                    dropoff={"lat": args.dropoff_lat, "lon": args.dropoff_lon},
                )
            )
        )
        payload = {"ride_id": ride.ride_id, "status": ride.status}
    else:
        issue = asyncio.run(
            runtime.issue_submission.execute(
                IssueSubmissionCommand(
                    ride_id=args.ride_id,
                    customer_id=args.customer_id,
                    category=args.category,
                    description=args.description,
                )
            )
        )
        payload = {"issue_id": issue.issue_id, "status": issue.status}

    sys.stdout.write(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
