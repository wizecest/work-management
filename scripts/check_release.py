"""Validate the explicit public file list using only the standard library."""

from __future__ import annotations

import json
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {".git", "__pycache__", ".venv", "private", "local", "dist"}
PATTERNS = {
    "absolute drive path": re.compile(r"(?i)(?<![\w/])[a-z]:[\\/]"),
    "personal home path": re.compile(r"/(?:Users|home)/[\w.-]+/"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "common access token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{24,})\b"),
    "credential assignment": re.compile(r'''(?im)^\s*["']?(?:api_key|access_token|client_secret|password)["']?\s*[:=]\s*["']?[A-Za-z0-9_./+\-=]{12,}'''),
}


def is_link(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & 0x400
    )


def public_paths(root: Path = ROOT) -> list[Path]:
    root = root.resolve()
    manifest = json.loads((root / "release-files.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, list) or not manifest:
        raise ValueError("release-files.json must be a non-empty list")
    names: set[str] = set()
    result = []
    for name in manifest:
        if not isinstance(name, str):
            raise ValueError("Manifest entries must be strings")
        relative = PurePosixPath(name)
        if (relative.is_absolute() or ".." in relative.parts or "\\" in name
                or ":" in name or name != relative.as_posix()
                or any(part in IGNORED_DIRS for part in relative.parts)):
            raise ValueError(f"Unsafe public path: {name}")
        folded = name.casefold()
        if folded in names:
            raise ValueError(f"Duplicate public path: {name}")
        names.add(folded)
        path = root
        for part in relative.parts:
            path = path / part
            if not path.exists() or is_link(path):
                raise ValueError(f"Missing file or linked path: {name}")
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f"Public entry is not a contained file: {name}")
        result.append(path)
    if "release-files.json" not in manifest:
        raise ValueError("The public manifest must include itself")
    return result


def actual_files(root: Path):
    for path in root.iterdir():
        if path.name in IGNORED_DIRS and path.is_dir():
            continue
        if is_link(path):
            raise ValueError(f"Unexpected linked path: {path.relative_to(ROOT)}")
        if path.is_dir():
            yield from actual_files(path)
        elif path.is_file():
            yield path


def validate(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    try:
        paths = public_paths(root)
        extras = set(actual_files(root)) - set(paths)
        errors.extend(f"Unlisted file: {p.relative_to(root)}" for p in sorted(extras))
    except (OSError, ValueError, TypeError) as error:
        return [str(error)]
    for path in paths:
        name = path.relative_to(root).as_posix()
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"Cannot read UTF-8 file {name}: {error}")
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(content):
                errors.append(f"Review {label}: {name}")
        if path.suffix == ".md":
            for match in re.finditer(r"\]\(([^\s)]+)\)", content):
                link = match.group(1)
                parsed = urlsplit(link)
                if parsed.scheme or link.startswith("#"):
                    continue
                target = (path.parent / unquote(parsed.path)).resolve()
                if not target.is_relative_to(root) or not target.exists():
                    errors.append(f"Broken or escaping local link: {name}: {link}")
    skill = root / "skills/work-management/SKILL.md"
    content = skill.read_text(encoding="utf-8")
    header = re.match(r"\A---\n(.*?)\n---\n", content, re.S)
    if not header or not re.search(r"(?m)^name: work-management$", header.group(1)):
        errors.append("Invalid SKILL.md name/frontmatter")
    if not header or not re.search(r"(?m)^description: .+", header.group(1)):
        errors.append("Missing skill description")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("VERSION must contain a semantic version")
    return errors


if __name__ == "__main__":
    try:
        failures = validate()
    except (OSError, ValueError) as error:
        failures = [str(error)]
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        sys.exit(1)
    print(f"PASS: {len(public_paths())} public files; links, manifest and configured privacy checks")
