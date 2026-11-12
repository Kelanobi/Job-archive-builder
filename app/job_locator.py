from pathlib import Path

from .errors import DCLNotFound, JobNotFound, NetworkUnavailable


def validate_job_number(value: str) -> str:
    job_number = value.strip()
    if not job_number or not job_number.isdecimal():
        raise ValueError("Enter a valid numeric job number.")
    return job_number


def locate_job(network_root: Path, job_number: str) -> Path:
    root = Path(network_root)
    try:
        if not root.exists() or not root.is_dir():
            raise NetworkUnavailable("Network drive unavailable.")
        job = root / job_number
        if not job.exists() or not job.is_dir():
            raise JobNotFound("Job folder not found.")
        return job
    except (NetworkUnavailable, JobNotFound):
        raise
    except OSError as exc:
        raise NetworkUnavailable("Network drive unavailable.") from exc


def locate_dcl_folder(job_folder: Path) -> Path:
    folder = Path(job_folder) / "DCL"
    try:
        if not folder.exists() or not folder.is_dir():
            raise DCLNotFound("DCL not found.")
        return folder
    except DCLNotFound:
        raise
    except OSError as exc:
        raise DCLNotFound("DCL not found.") from exc

