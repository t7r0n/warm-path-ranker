from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import core


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-demo")
    sub.add_parser("analyze")
    sub.add_parser("verify")
    sub.add_parser("dashboard")
    sub.add_parser("benchmark")
    sub.add_parser("export-demo-pack")
    sub.add_parser("all")
    args = parser.parse_args()
    root = Path.cwd()
    if args.command == "init-demo":
        result = core.init_demo(root)
    elif args.command == "analyze":
        result = core.analyze(root)
    elif args.command == "verify":
        result = core.verify(root)
    elif args.command == "dashboard":
        result = {"dashboard": str(core.dashboard(root))}
    elif args.command == "benchmark":
        result = core.benchmark(root)
    elif args.command == "export-demo-pack":
        result = {"demo_pack": str(core.export_demo_pack(root))}
    else:
        result = core.run_all(root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
