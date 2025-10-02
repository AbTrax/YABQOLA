"""Utility to package the YABQOLA Blender add-on into a distributable zip."""

from __future__ import annotations

import argparse
import ast
import shutil
import sys
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent
ADDON_NAME = ROOT.name
INIT_FILE = ROOT / "__init__.py"
DEFAULT_DIST_DIR = ROOT / "dist"
EXCLUDED_DIRS = {".git", ".github", "dist", "scripts", "__pycache__"}
EXCLUDED_FILES = {".gitignore"}


def _parse_bl_info(init_path: Path) -> dict:
    if not init_path.exists():
        raise FileNotFoundError(f"Unable to locate {init_path}")

    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "bl_info":
                    return ast.literal_eval(node.value)
    raise ValueError("Could not find bl_info dictionary in __init__.py")


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


def build_archive(output_dir: Path, zip_name: str) -> Path:
    files = list(_discover_files(ROOT))
    if not files:
        raise RuntimeError("No files discovered to package.")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / zip_name
    if archive_path.exists():
        archive_path.unlink()

    root_folder = ADDON_NAME

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as zf:
        for file_path in files:
            relative_path = file_path.relative_to(ROOT)
            arcname = Path(root_folder) / relative_path
            zf.write(file_path, arcname.as_posix())

    return archive_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package the YABQOLA Blender add-on.")
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

    bl_info = _parse_bl_info(INIT_FILE)
    version_tuple = bl_info.get("version")
    if not version_tuple:
        raise KeyError("bl_info missing 'version' entry")
    version = ".".join(str(part) for part in version_tuple)

    if args.force and args.dist.exists():
        shutil.rmtree(args.dist)

    zip_base = f"{ADDON_NAME}-{version}"
    if args.suffix:
        zip_base = f"{zip_base}-{args.suffix}"
    zip_filename = f"{zip_base}.zip"

    archive_path = build_archive(args.dist, zip_filename)
    print(f"Created archive: {archive_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
