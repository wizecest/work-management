"""Build a checked ZIP from the explicit public manifest."""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

from check_release import ROOT, public_paths, validate


def build(output_dir: Path, root: Path = ROOT) -> Path:
    root = root.resolve()
    errors = validate(root)
    if errors:
        raise ValueError("Release checks failed: " + "; ".join(errors))
    output_dir = output_dir.expanduser().resolve()
    if output_dir.is_relative_to(root):
        raise ValueError("Choose an output directory outside the repository")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"work-management-{version}.zip"
    checksum = archive.with_suffix(".zip.sha256")
    if archive.exists() or checksum.exists():
        raise FileExistsError("Release ZIP or checksum already exists; nothing overwritten")
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in public_paths(root):
            bundle.write(path, "work-management/" + path.relative_to(root).as_posix())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    with checksum.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{digest}  {archive.name}\n")
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.output_dir)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    print(f"Built: {result}")
