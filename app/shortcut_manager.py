import re
from dataclasses import dataclass
from pathlib import Path

from .errors import ArchiveError

_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


@dataclass(frozen=True)
class ShortcutResult:
    status: str
    path: Path


def safe_filename(value: str, max_length: int = 180) -> str:
    cleaned = _INVALID.sub("", value).strip().rstrip(". ")
    return cleaned[:max_length].rstrip(". ") or "Unknown customer"


def _shell():
    import win32com.client
    return win32com.client.Dispatch("WScript.Shell")


def _same_target(left: str, right: Path) -> bool:
    return str(Path(left)).rstrip("\\/").casefold() == str(right).rstrip("\\/").casefold()


def shortcut_paths(archive_dir: Path, job_number: str, customer: str, create_job_subfolder: bool = False) -> tuple[Path, Path]:
    item_name = safe_filename(f"{job_number} - {customer}")
    container = Path(archive_dir) / item_name if create_job_subfolder else Path(archive_dir)
    return container, container / f"{item_name}.lnk"


def create_or_update_shortcut(job_folder: Path, archive_dir: Path, job_number: str, customer: str,
                              create_job_subfolder: bool = False) -> ShortcutResult:
    try:
        archive, desired = shortcut_paths(archive_dir, job_number, customer, create_job_subfolder)
        archive.mkdir(parents=True, exist_ok=True)
        target = Path(job_folder)
        shell = _shell()
        existing = None
        # Search the destination tree so a corrected customer name updates the
        # existing job shortcut instead of creating a second job folder.
        search_root = Path(archive_dir)
        for candidate in search_root.rglob("*.lnk"):
            try:
                if _same_target(shell.CreateShortCut(str(candidate)).Targetpath, target):
                    existing = candidate
                    break
            except Exception:
                continue
        if existing == desired:
            return ShortcutResult("exists", desired)
        if existing and existing != desired:
            if desired.exists():
                raise ArchiveError("A conflicting shortcut already exists.")
            old_parent = existing.parent
            existing.replace(desired)
            if create_job_subfolder and old_parent != Path(archive_dir) and old_parent != archive:
                try:
                    old_parent.rmdir()
                except OSError:
                    pass
            shortcut = shell.CreateShortCut(str(desired))
            shortcut.Targetpath = str(target)
            shortcut.WorkingDirectory = str(target)
            shortcut.Description = f"Job {job_number} - {customer}"
            shortcut.IconLocation = r"%SystemRoot%\System32\shell32.dll,3"
            shortcut.save()
            return ShortcutResult("updated", desired)
        shortcut = shell.CreateShortCut(str(desired))
        shortcut.Targetpath = str(target)
        shortcut.WorkingDirectory = str(target)
        shortcut.Description = f"Job {job_number} - {customer}"
        shortcut.IconLocation = r"%SystemRoot%\System32\shell32.dll,3"
        shortcut.save()
        return ShortcutResult("created", desired)
    except ArchiveError:
        raise
    except Exception as exc:
        raise ArchiveError("Unable to create shortcut.") from exc

