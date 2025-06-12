#!/usr/bin/env python3
"""Unified runner for the Yōsai dashboard."""
import os
import sys
from packaging.version import Version

import dash_cytoscape as cyto

# Ensure the correct dash-cytoscape version is installed before importing app
if Version(cyto.__version__) < Version("0.3.0"):
    raise RuntimeError(
        f"dash-cytoscape>=0.3.0 required, found {cyto.__version__}. "
        "Please run 'pip install -r requirements.txt'"
    )

from app_factory import create_app

MODE = (sys.argv[1] if len(sys.argv) > 1 else os.getenv("MODE", "development")).lower()

app = create_app(MODE)

if MODE in ("prod", "production"):
    from waitress import serve
    serve(app.server, host="0.0.0.0", port=8050)
else:
    port = int(os.getenv("PORT", "8050"))
    host = os.getenv("HOST", "127.0.0.1")
    debug = MODE in ("dev", "development")
    # Use Dash's run_server for proper type hints (expects int port)
    app.run_server(
        debug=debug,
        host=host,
        port=port,
        dev_tools_hot_reload=True,
        dev_tools_ui=True,
        dev_tools_props_check=False,
    )
