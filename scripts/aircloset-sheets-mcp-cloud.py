#!/usr/bin/env python3
"""Cloud Agent wrapper → gws-python-mcp.py (supports GWS_CREDENTIALS_PICKLE_B64)."""
import os
import runpy

os.environ.setdefault("GWS_CONFIG_DIR", os.path.expanduser("~/.config/gws-aircloset"))
runpy.run_path(os.path.join(os.path.dirname(__file__), "gws-python-mcp.py"), run_name="__main__")
