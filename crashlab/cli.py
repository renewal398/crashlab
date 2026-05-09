#!/usr/bin/env python3
"""
CrashLab – production‑ready CLI
Usage:
    crashlab --config config.yaml
"""

import argparse
import sys
from crashlab.core import CoreEngine

def main():
    parser = argparse.ArgumentParser(
        description="CrashLab – educational DoS stress‑testing lab"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Path to configuration YAML file (default: config.yaml)"
    )
    parser.add_argument(
        "-t", "--target",
        help="Quick target URL (overrides config)"
    )
    parser.add_argument(
        "--attack",
        choices=["slowloris", "flood", "exhaust", "all"],
        default="all",
        help="Which attack to run (default: all)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List discovered endpoints only, do not attack"
    )
    args = parser.parse_args()

    try:
        engine = CoreEngine(args.config)
        if args.target:
            engine.override_target(args.target)

        if args.list:
            engine.discover_endpoints()
            engine.print_discovered()
            return

        engine.run(args.attack)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Shutting down cleanly.")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
