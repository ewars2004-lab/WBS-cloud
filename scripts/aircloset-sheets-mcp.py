#!/usr/bin/env python3
"""Backward-compatible wrapper → gws-python-mcp.py (aircloset profile)."""
import os
import runpy

os.environ.setdefault("GWS_CONFIG_DIR", os.path.expanduser("~/.config/gws-aircloset"))
runpy.run_path(os.path.join(os.path.dirname(__file__), "gws-python-mcp.py"), run_name="__main__")
