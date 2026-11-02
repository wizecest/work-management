"""Install only the skill folder; never overwrite an existing installation."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from check_release import ROOT, public_paths


def install(skills_dir: Path, root: Path = ROOT) -> Path:
    files = public_paths(root)
    source = root.resolve() / "skills/work-management"
    selected = [path for path in files if path.is_relative_to(source)]
    if not selected:
        raise ValueError("No skill files in public manifest")
    skills_dir = skills_dir.expanduser().resolve()
    destination = skills_dir / "work-management"
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Existing installation left unchanged: {destination}")
    skills_dir.mkdir(parents=True, exist_ok=True)
    destination.mkdir(exist_ok=False)
    try:
        for path in selected:
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    except OSError as error:
        raise OSError(f"Incomplete installation retained for inspection at {destination}: {error}") from error
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        target = install(args.skills_dir)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Installed skill: {target}")
    print("Ask your host to rediscover skills according to its own instructions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
