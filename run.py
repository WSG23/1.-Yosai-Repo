#!/usr/bin/env python3
"""Unified runner for the Yōsai dashboard."""
from __future__ import annotations

import argparse
import os


def _parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Yōsai dashboard")
    parser.add_argument(
        "--mode",
        default=os.getenv("MODE", "dev"),
        choices=["dev", "prod", "production"],
        help="Run mode (dev or prod). Can also be set via MODE env var",
    )
    return parser.parse_args()


def _run_dev() -> None:
    """Start the development server."""
    from app import app

    app.run(
        debug=True,
        host="127.0.0.1",
        port=8050,
        dev_tools_hot_reload=True,
        dev_tools_ui=True,
        dev_tools_props_check=False,
    )


def _run_prod() -> None:
    """Start the production server via Waitress."""
    from app_production import create_production_app
    from waitress import serve

    app = create_production_app()
    serve(app.server, host="0.0.0.0", port=8050)


def main() -> None:
    args = _parse_args()
    mode = args.mode.lower()

    if mode in ("prod", "production"):
        _run_prod()
    else:
        _run_dev()


if __name__ == "__main__":
    main()

