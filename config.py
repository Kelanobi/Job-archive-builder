"""Single place for deployment paths and application constants."""
import sys
from pathlib import Path

APP_NAME = "Qualitrol Job Archive"
NETWORK_ROOT = Path(r"S:\Manufacturing\Public\2 Jobfiles Released")


def archive_directory() -> Path:
    """Select the packaged user profile from the executable name."""
    executable_name = Path(sys.executable).stem.casefold()
    if "afeez" in executable_name:
        return Path(r"C:\Users\Afeez.Sotannde\OneDrive - Ralliant\Job files")
    return Path(r"C:\Users\kelvin.obi\OneDrive - Ralliant\Job files")


ARCHIVE_DIR = archive_directory()
CREATE_JOB_SUBFOLDER = True
LOG_DIR = Path.home() / "AppData" / "Local" / "Qualitrol Job Archive" / "logs"
WINDOW_SIZE = "820x570"

