#!/usr/bin/env python3
"""Download dataset archives from Drive, extract them in data/, and remove zip files."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

FOLDER_URL = "https://drive.google.com/drive/folders/15aDDoMD0Qxya8RqM9mwEq4fTqgwgrkET?usp=sharing"
OUTPUT_DIR = Path("data")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download dataset files from the shared Google Drive folder."
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output from the downloader.",
    )
    return parser.parse_args()


def _flatten_single_nested_directory(extract_dir: Path) -> None:
    entries = list(extract_dir.iterdir())
    dirs = [p for p in entries if p.is_dir()]
    files = [p for p in entries if p.is_file()]

    if files or len(dirs) != 1:
        return

    nested = dirs[0]
    if nested.name != extract_dir.name:
        return

    for item in nested.iterdir():
        target = extract_dir / item.name
        if target.exists():
            continue
        shutil.move(str(item), str(target))
    nested.rmdir()


def extract_zip_files(directory: Path) -> int:
    extracted = 0
    for zip_path in sorted(directory.glob("*.zip")):
        target_dir = directory / zip_path.stem

        if target_dir.exists() and any(target_dir.iterdir()):
            print(f"Skipping extraction (already exists): {target_dir}")
            try:
                zip_path.unlink()
                print(f"Removed zip: {zip_path.name}")
            except OSError as exc:
                print(f"Failed to remove {zip_path.name}: {exc}", file=sys.stderr)
            continue

        print(f"Extracting: {zip_path.name} -> {target_dir.name}/")
        target_dir.mkdir(parents=True, exist_ok=True)
        try:
            with ZipFile(zip_path, "r") as archive:
                archive.extractall(target_dir)
            _flatten_single_nested_directory(target_dir)
            zip_path.unlink()
            print(f"Removed zip: {zip_path.name}")
            extracted += 1
        except BadZipFile:
            print(f"Invalid zip file: {zip_path}", file=sys.stderr)
        except Exception as exc:  # pragma: no cover
            print(f"Failed to extract {zip_path.name}: {exc}", file=sys.stderr)

    return extracted


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import gdown
    except ImportError:
        print(
            "Dependency missing: install gdown with `pip install -r requirements.txt` and run again.",
            file=sys.stderr,
        )
        return 1

    print(f"Downloading files from Drive folder to: {OUTPUT_DIR.resolve()}")
    try:
        gdown.download_folder(
            url=FOLDER_URL,
            output=str(OUTPUT_DIR),
            quiet=args.quiet,
            use_cookies=False,
        )
    except Exception as exc:  # pragma: no cover
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1

    extracted_count = extract_zip_files(OUTPUT_DIR)
    if extracted_count:
        print(f"Extraction complete: {extracted_count} zip file(s) extracted.")
    else:
        print("No new zip files extracted.")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
