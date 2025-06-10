#!/usr/bin/env python3
"""Unified runner for the Yōsai dashboard."""
import os
import sys

MODE = (sys.argv[1] if len(sys.argv) > 1 else os.getenv("MODE", "dev")).lower()

if MODE in ("prod", "production"):
    from app_production import create_production_app
    from waitress import serve

    app = create_production_app()
    serve(app.server, host="0.0.0.0", port=8050)
else:
    from app import app

    app.run(
        debug=True,
        host="127.0.0.1",
        port=8050,
        dev_tools_hot_reload=True,
        dev_tools_ui=True,
        dev_tools_props_check=False,
    )

