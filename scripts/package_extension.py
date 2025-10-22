"""Package the YABQOLA Blender extension into a distributable zip archive."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_FILE = ROOT / "blender_manifest.toml"
DEFAULT_DIST_DIR = ROOT / "dist"
EXCLUDED_DIRS = {".git", ".github", "dist", "scripts", "__pycache__"}
EXCLUDED_FILES = {".gitignore"}

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for Python <3.11
    import tomli as tomllib  # type: ignore[no-redef]


def _parse_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Unable to locate {manifest_path}")

    with manifest_path.open("rb") as handle:
        manifest = tomllib.load(handle)

    missing = {key for key in ("id", "version") if key not in manifest}
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise KeyError(f"Manifest missing required fields: {missing_list}")

    return manifest


def _discover_files(base: Path) -> Iterable[Path]:
    for path in base.iterdir():
        if path.name in EXCLUDED_DIRS and path.is_dir():
            continue
        if path.name.startswith(".") and path.is_dir():
            continue
        if path.is_file():
            if path.name in EXCLUDED_FILES:
                continue
            yield path
        elif path.is_dir():
            yield from _discover_files(path)


def build_archive(output_dir: Path, zip_name: str, extension_id: str) -> Path:
    files = list(_discover_files(ROOT))
    if not files:
        raise RuntimeError("No files discovered to package.")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / zip_name
    if archive_path.exists():
        archive_path.unlink()

    root_folder = extension_id

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as zf:
        for file_path in files:
            relative_path = file_path.relative_to(ROOT)
            arcname = Path(root_folder) / relative_path
            zf.write(file_path, arcname.as_posix())

    return archive_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package the YABQOLA Blender extension.")
    parser.add_argument(
        "--dist",
        dest="dist",
        type=Path,
        default=DEFAULT_DIST_DIR,
        help="Output directory for the generated zip (default: ./dist)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove the dist directory before packaging to ensure a clean build.",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="",
        help="Optional suffix to append to the zip filename (e.g. build metadata)",
    )

    args = parser.parse_args(argv)

    manifest = _parse_manifest(MANIFEST_FILE)
    version_raw = manifest.get("version")
    if not isinstance(version_raw, str) or not version_raw:
        raise TypeError("Manifest 'version' must be a non-empty string")
    extension_id = manifest["id"]

    if args.force and args.dist.exists():
        shutil.rmtree(args.dist)

    zip_base = f"{extension_id}-{version_raw}"
    if args.suffix:
        zip_base = f"{zip_base}-{args.suffix}"
    zip_filename = f"{zip_base}.zip"

    archive_path = build_archive(args.dist, zip_filename, extension_id)
    print(f"Created archive: {archive_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
