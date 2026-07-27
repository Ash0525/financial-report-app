"""Resolve writable locations for application-owned data."""

import os
import sys
from pathlib import Path

APP_NAME = "Financial Report App"
DATA_DIRECTORY_ENVIRONMENT_VARIABLE = "FINANCIAL_REPORT_APP_DATA_DIR"


def get_application_data_directory() -> Path:
    """Return the platform-appropriate directory for persistent app data."""

    configured_directory = os.environ.get(
        DATA_DIRECTORY_ENVIRONMENT_VARIABLE
    )
    if configured_directory:
        return Path(configured_directory).expanduser()

    home_directory = Path.home()

    if sys.platform == "darwin":
        return home_directory / "Library" / "Application Support" / APP_NAME

    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / APP_NAME
        return home_directory / "AppData" / "Local" / APP_NAME

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / APP_NAME

    return home_directory / ".local" / "share" / APP_NAME
