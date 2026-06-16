from __future__ import annotations

import re
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from .config import AppPaths


DATE_IN_NAME_PATTERN = re.compile(r"(?P<day>\d{2})[-_](?P<month>\d{2})[-_](?P<year>\d{4})")


@dataclass(slots=True)
class StoredFileInfo:
    name: str
    path: str
    size: int
    modified_at: str

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


def build_app_paths(data_root: Path) -> AppPaths:
    uploads_root = data_root / "uploads"
    return AppPaths(
        data_root=data_root,
        uploads_root=uploads_root,
        uploads_catalog=uploads_root / "catalog",
        uploads_inventory=uploads_root / "inventory",
        generated_root=data_root / "generated",
        generated_runs=data_root / "generated" / "runs",
        generated_latest=data_root / "generated" / "latest",
    )


def ensure_app_directories(paths: AppPaths) -> None:
    for path in [
        paths.data_root,
        paths.uploads_root,
        paths.uploads_catalog,
        paths.uploads_inventory,
        paths.generated_root,
        paths.generated_runs,
        paths.generated_latest,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", filename.strip())
    return sanitized.strip(".-") or "upload.bin"


def timestamped_filename(filename: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{sanitize_filename(filename)}"


def save_uploaded_file(file_storage: object, destination_dir: Path) -> Path:
    filename = sanitize_filename(getattr(file_storage, "filename", "") or "upload.bin")
    target = destination_dir / timestamped_filename(filename)
    destination_dir.mkdir(parents=True, exist_ok=True)
    file_storage.save(target)
    return target


def parse_snapshot_date(path: Path) -> datetime | None:
    match = DATE_IN_NAME_PATTERN.search(path.name)
    if not match:
        return None
    try:
        return datetime(
            year=int(match.group("year")),
            month=int(match.group("month")),
            day=int(match.group("day")),
            tzinfo=UTC,
        )
    except ValueError:
        return None


def latest_uploaded_file(directory: Path, suffixes: tuple[str, ...]) -> Path | None:
    candidates = [path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in suffixes]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda path: (
            parse_snapshot_date(path) is not None,
            parse_snapshot_date(path) or datetime.fromtimestamp(path.stat().st_mtime, tz=UTC),
            path.stat().st_mtime,
            path.name,
        ),
    )


def new_run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def file_info(path: Path | None) -> StoredFileInfo | None:
    if path is None or not path.exists():
        return None
    stat = path.stat()
    return StoredFileInfo(
        name=path.name,
        path=str(path),
        size=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
    )


def copy_run_to_latest(run_dir: Path, latest_dir: Path) -> None:
    latest_dir.mkdir(parents=True, exist_ok=True)
    for path in latest_dir.iterdir():
        if path.is_file():
            path.unlink()

    for source in run_dir.iterdir():
        if source.is_file():
            shutil.copy2(source, latest_dir / source.name)
