"""Shared GWS credential env var names (local + Cloud Agent)."""
from __future__ import annotations

import os
from pathlib import Path

SECRET_AIRCLOSET = "GWS_CREDENTIALS_PICKLE_B64_AIRCLOSET"
SECRET_PERSONAL = "GWS_CREDENTIALS_PICKLE_B64_PERSONAL"
LEGACY_SECRET = "GWS_CREDENTIALS_PICKLE_B64"  # optional fallback → aircloset

CONFIG_AIRCLOSET = Path.home() / ".config/gws-aircloset"
CONFIG_PERSONAL = Path.home() / ".config/gws"

PROFILES = {
    "aircloset": {
        "config_dir": CONFIG_AIRCLOSET,
        "secret_env": SECRET_AIRCLOSET,
        "email_hint": "r.yaguchi@air-closet.com",
        "mcp_name": "google-workspace-aircloset",
    },
    "personal": {
        "config_dir": CONFIG_PERSONAL,
        "secret_env": SECRET_PERSONAL,
        "email_hint": "ewars2004@gmail.com",
        "mcp_name": "google-workspace-personal",
    },
}


def config_dir() -> Path:
    raw = os.environ.get("GWS_CONFIG_DIR", "").strip()
    if raw:
        return Path(raw).expanduser()
    return CONFIG_AIRCLOSET


def profile_key() -> str:
    name = config_dir().name
    if name == "gws":
        return "personal"
    return "aircloset"


def secret_env_name() -> str:
    explicit = os.environ.get("GWS_SECRET_ENV", "").strip()
    if explicit:
        return explicit
    legacy = os.environ.get(LEGACY_SECRET, "").strip()
    if legacy:
        return LEGACY_SECRET
    return PROFILES[profile_key()]["secret_env"]


def pickle_b64_from_environ() -> str:
    key = secret_env_name()
    val = os.environ.get(key, "").strip()
    if val:
        return val
    if key != LEGACY_SECRET:
        val = os.environ.get(LEGACY_SECRET, "").strip()
        if val and profile_key() == "aircloset":
            return val
    return ""
