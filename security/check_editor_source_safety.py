"""Fail-closed source check; never executes editor tasks or font assets.

This guards a known workspace-startup injection path, not the user's editor,
installed extensions, local machine, or all conceivable code-execution paths.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys


# Stable original Font Awesome bytes also present in historical clean Git trees
# elsewhere in the portfolio. SVG hashes normalize *only* line endings.
# These were not in t-kal-in-ket before the unrelated 6ed9639 merge.
PINNED_FONTS = {
    "fa-brands-400.eot": "811e1577184066108ceca86d5a624a9012303df5206c5cb0b27d5e3fedcba5a3",
    "fa-brands-400.svg": "02340ba1789d09bcc507563c89c4a847ba537bb8132082777a50519cf74bcb5b",
    "fa-brands-400.ttf": "a0c145382acfe59767d1487d6505f349665b685c2885cd91b621d141a292b0f8",
    "fa-brands-400.woff": "e836c5d5dfc13e18170c5bddefb4fdac7c65ac0ad43a4b431acdc4a98865a260",
    "fa-brands-400.woff2": "5d9190292acdd48ba0fc35080f7e7448f3cdf0d79199a4d23f0f49b5341fdf29",
    "fa-regular-400.eot": "01f4416f5db59e2dd6b6fbd9dc32336d99db18f7eb623a49f584d04afd279473",
    "fa-regular-400.svg": "865fd23de13b1920280e182359579e09eff7a09eb24676eceec7552838559f55",
    "fa-regular-400.ttf": "f32b94a29060dfec0c797a1dfe111357eb1d682f1aca4ac4b95cf0f4c3e2bfa9",
    "fa-regular-400.woff": "8e2d96198711b63752e5f2f5987b8ffc536df6156a065bdbe28cb7231cad793d",
    "fa-regular-400.woff2": "6a8c8e9e1e7f692c21af1956de163f3d026778e6449fe93a09a671847ca1ae65",
    "fa-solid-900.eot": "32501727bb23fc77615b1ec76b5f298ec22198c0f3d6a3e7d6fe4ac3cf315db9",
    "fa-solid-900.svg": "e768539808757f7eec20f09c9ee9b36b0e6c5636e90c9ee697995cbbc6ee0555",
    "fa-solid-900.ttf": "231d68cefbc6846fb78cafca8467401a4f371e226418662e8900e3d52adc00ab",
    "fa-solid-900.woff": "352f8ead280419dd953d2bc7843386bb9430e8152c2dbd2c2d2494f6b9567ee7",
    "fa-solid-900.woff2": "7f4d3fd0a705dbf8403298aad91d5de6972e6b5d536068eba8b24954a5a0a8c7",
}

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
    if path.is_symlink() or not path.is_file():
        raise UnsafeEditorSource(f"missing, nonregular or symlinked editor source: {path}")
    try:
        data = json.loads(_jsonc_text(path.read_bytes()), object_pairs_hook=_unique_pairs)
    except (UnicodeError, ValueError) as exc:
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
    fonts = root / "public" / "fonts"
    if fonts.is_symlink() or not fonts.is_dir():
        violations.append("missing or symlinked font directory")
        return violations
    expected = set(PINNED_FONTS) | {"README.md"}
    for path in sorted(fonts.iterdir()):
        if path.name not in expected:
            violations.append(f"unapproved font-directory entry: {path.name}")
    if (fonts / "README.md").is_symlink() or not (fonts / "README.md").is_file():
        violations.append("missing or symlinked font README")
    for name, pinned in PINNED_FONTS.items():
        path = fonts / name
        if path.is_symlink() or not path.is_file():
            violations.append(f"missing or symlinked pinned font: {name}")
            continue
        data = path.read_bytes()
        if path.suffix == ".svg":
            data = data.replace(b"\r\n", b"\n")
        if hashlib.sha256(data).hexdigest() != pinned:
            violations.append(f"font SHA256 mismatch: {name}")
    return violations


def main() -> int:
    violations = check_tree(Path(__file__).resolve().parents[1])
    if violations:
        for violation in violations:
            print(f"EDITOR_SOURCE_UNSAFE: {violation}", file=sys.stderr)
        return 1
    print(f"EDITOR_SOURCE_OK: no automatic startup; {len(PINNED_FONTS)} pinned fonts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
