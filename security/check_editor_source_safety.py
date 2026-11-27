"""Fail-closed source check; never executes editor tasks or font assets.

This guards a known workspace-startup injection path, not the user's editor,
installed extensions, local machine, or all conceivable code-execution paths.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import stat


SKIP_FOLDERS = {".git", ".venv", "node_modules", "__pycache__", ".tox", ".pytest_cache", "dist", "build"}


class UnsafeEditorSource(ValueError):
    """A configuration is unsafe or cannot be parsed convincingly."""


def _jsonc_text(raw: bytes) -> str:
    """Strip VS Code JSONC comments/trailing commas without touching strings."""
    source = raw.decode("utf-8-sig")
    out: list[str] = []
    quoted = False
    index = 0
    while index < len(source):
        token = source[index]
        if quoted:
            out.append(token)
            if token == "\\" and index + 1 < len(source):
                index += 1
                out.append(source[index])
            elif token == '"':
                quoted = False
            index += 1
            continue
        if token == '"':
            quoted = True
            out.append(token)
            index += 1
            continue
        if token == "/" and index + 1 < len(source) and source[index + 1] == "/":
            index += 2
            while index < len(source) and source[index] not in "\r\n":
                index += 1
            out.append(" ")
            continue
        if token == "/" and index + 1 < len(source) and source[index + 1] == "*":
            end = source.find("*/", index + 2)
            if end < 0:
                raise UnsafeEditorSource("unterminated block comment")
            out.append(" ")
            index = end + 2
            continue
        out.append(token)
        index += 1
    if quoted:
        raise UnsafeEditorSource("unterminated quoted string")
    uncom = "".join(out)
    cleaned: list[str] = []
    quoted = False
    index = 0
    while index < len(uncom):
        token = uncom[index]
        if quoted:
            cleaned.append(token)
            if token == "\\" and index + 1 < len(uncom):
                index += 1
                cleaned.append(uncom[index])
            elif token == '"':
                quoted = False
        elif token == '"':
            quoted = True
            cleaned.append(token)
        elif token == ",":
            following = index + 1
            while following < len(uncom) and uncom[following].isspace():
                following += 1
            prior = len(cleaned) - 1
            while prior >= 0 and cleaned[prior].isspace():
                prior -= 1
            if following < len(uncom) and uncom[following] in "}]" and prior >= 0 and cleaned[prior] not in "[{,:":
                index += 1
                continue
            cleaned.append(token)
        else:
            cleaned.append(token)
        index += 1
    return "".join(cleaned)


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise UnsafeEditorSource(f"duplicate JSONC key: {key}")
        result[key] = value
    return result


def _load(path: Path) -> dict:
    try:
        info = path.lstat()
    except OSError as exc:
        raise UnsafeEditorSource(f"unreadable editor source: {path}") from exc
    if not stat.S_ISREG(info.st_mode) or getattr(info, "st_file_attributes", 0) & 1024:
        raise UnsafeEditorSource(f"nonregular or linked editor source: {path}")
    try:
        data = json.loads(_jsonc_text(path.read_bytes()), object_pairs_hook=_unique_pairs)
    except (OSError, UnicodeError, ValueError) as exc:
        raise UnsafeEditorSource(f"invalid JSONC {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise UnsafeEditorSource(f"JSONC object expected: {path}")
    return data


def _walk_config(value: object, scope: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            field = f"{scope}.{key}"
            if key == "runOn" and isinstance(child, str) and child.strip().casefold() == "folderopen":
                raise UnsafeEditorSource(f"automatic folderOpen task: {field}")
            if key == "task.allowAutomaticTasks" and child != "off":
                raise UnsafeEditorSource(f"automatic task permission: {field}")
            if key == "tasks" and (
                scope == "settings" or scope.startswith("settings.")
                or scope.endswith(".settings") or ".settings." in scope
            ):
                raise UnsafeEditorSource(f"task embedded in settings: {field}")
            _walk_config(child, field)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_config(child, f"{scope}[{index}]")
    elif isinstance(value, str):
        value = value.replace("\\", "/").casefold()
        if "public/fonts/" in value and any(ext in value for ext in (".ttf", ".woff", ".woff2", ".eot", ".svg", ".lkf")):
            raise UnsafeEditorSource(f"font asset referenced as editor command: {scope}")


def _editor_configs(root: Path):
    for directory, subdirs, filenames in os.walk(root, followlinks=False):
        subdirs[:] = [folder for folder in subdirs if folder.casefold() not in SKIP_FOLDERS]
        parent = Path(directory)
        if parent.name.casefold() == ".vscode":
            for filename in filenames:
                if filename.casefold().endswith(".json"):
                    yield parent / filename
        for filename in filenames:
            if filename.casefold().endswith(".code-workspace"):
                yield parent / filename


def check_tree(root: Path) -> list[str]:
    """Return violations found without running any source file."""
    violations: list[str] = []
    editor = root / ".vscode"
    if editor.is_symlink() or not editor.is_dir():
        violations.append("missing or symlinked .vscode directory")
    for directory, subdirs, _ in os.walk(root, followlinks=False):
        for folder in subdirs:
            if folder.casefold() == ".vscode" and (Path(directory) / folder).is_symlink():
                violations.append(f"symlinked nested editor directory: {Path(directory) / folder}")
        subdirs[:] = [folder for folder in subdirs if folder.casefold() not in SKIP_FOLDERS]
    for required in (editor / "tasks.json", editor / "settings.json"):
        try:
            config = _load(required)
            if required.name == "tasks.json" and not isinstance(config.get("tasks"), list):
                raise UnsafeEditorSource("tasks.json must have an array of tasks")
            if required.name == "settings.json" and config.get("task.allowAutomaticTasks") != "off":
                raise UnsafeEditorSource("workspace task.allowAutomaticTasks must be 'off'")
        except UnsafeEditorSource as exc:
            violations.append(str(exc))
    for path in _editor_configs(root):
        try:
            config = _load(path)
            _walk_config(config, "settings" if path.name.casefold() == "settings.json" else path.stem)
        except UnsafeEditorSource as exc:
            violations.append(str(exc))
    for directory, subdirs, filenames in os.walk(root, followlinks=False):
        subdirs[:] = [n for n in subdirs if n.casefold() not in SKIP_FOLDERS]
        parent = Path(directory)
        if parent.name.casefold() == ".vscode":
            for name in subdirs + filenames:
                if name.casefold() in {"ini", "inq"}:
                    violations.append("unapproved editor entry")
    try:
        (root / "public" / "fonts").lstat()
    except FileNotFoundError:
        pass
    except OSError:
        violations.append("unable to inspect font directory")
    else:
        violations.append("unexpected font directory")
    return violations


def main() -> int:
    violations = check_tree(Path(__file__).resolve().parents[1])
    if violations:
        for violation in violations:
            print(f"EDITOR_SOURCE_UNSAFE: {violation}", file=sys.stderr)
        return 1
    print("EDITOR_SOURCE_OK: Python-only workspace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
