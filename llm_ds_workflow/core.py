"""
Core: load patterns and templates, render templates with variables.

Design notes:

1. Templates use {placeholder} syntax with human-readable placeholder names
   like "{experiment name}", "{schema.table_name}", "{start} to {end} ({N} days)".
   These aren't Python .format() compatible (spaces, dots, and repeated braces
   for prose examples). We use a permissive regex substitution instead.

2. Unfilled placeholders are preserved verbatim in the output AND collected in
   `RenderedPrompt.missing`, so the caller can decide whether to error, warn,
   or send-as-is. Some workflows deliberately leave placeholders in place for
   the user to fill in interactively — we don't force a specific policy.

3. Patterns and templates are discovered from the filesystem relative to the
   repo root (the directory containing `patterns/` and `templates/`). This
   works whether the package is imported from a checked-out repo or from a
   pip install (see `_find_repo_root`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

PLACEHOLDER_RE = re.compile(r"\{([^{}\n]+?)\}")


def _find_repo_root() -> Path:
    """
    Locate the repo root — the directory containing patterns/ and templates/.

    Walks up from this file's location until we find one, so `pip install -e .`
    from the repo root works. If the package is ever installed from a wheel
    without the patterns/templates dirs bundled, this raises with a clear
    error rather than silently returning an empty list.
    """
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "patterns").is_dir() and (candidate / "templates").is_dir():
            return candidate
    raise RuntimeError(
        "Could not locate patterns/ and templates/ directories. If you "
        "installed this package from a wheel, the pattern/template files "
        "were not bundled — install from source: `pip install -e .` from "
        "a checked-out repo."
    )


@dataclass(frozen=True)
class Pattern:
    """A prose pattern doc from patterns/."""
    name: str            # e.g. "01-schema-anchored-sql"
    path: Path
    title: str           # first-line heading text

    def read(self) -> str:
        return self.path.read_text(encoding="utf-8")


@dataclass(frozen=True)
class Template:
    """A prompt template from templates/."""
    name: str            # e.g. "ab-readout"
    path: Path

    def read(self) -> str:
        return self.path.read_text(encoding="utf-8")

    @property
    def placeholders(self) -> list[str]:
        """Return the (unique, order-preserved) list of {placeholders} in the template."""
        text = self.read()
        seen: dict[str, None] = {}
        for m in PLACEHOLDER_RE.finditer(text):
            key = m.group(1).strip()
            seen.setdefault(key, None)
        return list(seen.keys())


@dataclass
class RenderedPrompt:
    """Result of filling a template with variables."""
    text: str
    template: Template
    filled: dict[str, str] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return self.text


def _extract_title(md: str) -> str:
    for line in md.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def list_patterns(root: Path | None = None) -> list[Pattern]:
    """Return all pattern docs in patterns/, sorted by filename."""
    root = root or _find_repo_root()
    out: list[Pattern] = []
    for p in sorted((root / "patterns").glob("*.md")):
        title = _extract_title(p.read_text(encoding="utf-8"))
        out.append(Pattern(name=p.stem, path=p, title=title))
    return out


def list_templates(root: Path | None = None) -> list[Template]:
    """Return all templates in templates/, sorted by filename."""
    root = root or _find_repo_root()
    return [Template(name=p.stem, path=p) for p in sorted((root / "templates").glob("*.txt"))]


def load_pattern(name: str, root: Path | None = None) -> Pattern:
    """Load a pattern by filename stem. Raises KeyError if not found."""
    for p in list_patterns(root):
        if p.name == name:
            return p
    raise KeyError(f"Pattern not found: {name!r}. Available: {[p.name for p in list_patterns(root)]}")


def load_template(name: str, root: Path | None = None) -> Template:
    """Load a template by filename stem. Raises KeyError if not found."""
    for t in list_templates(root):
        if t.name == name:
            return t
    raise KeyError(f"Template not found: {name!r}. Available: {[t.name for t in list_templates(root)]}")


def render(template: Template | str, variables: Mapping[str, Any] | None = None) -> RenderedPrompt:
    """
    Render a template by substituting {placeholder} occurrences with values
    from `variables`.

    Placeholders whose names are not in `variables` are left as-is and
    reported in RenderedPrompt.missing. This is intentional: some workflows
    want to leave placeholders in place for interactive filling.

    `template` may be a Template object or a string name (looked up via
    load_template).
    """
    if isinstance(template, str):
        template = load_template(template)
    variables = dict(variables or {})

    filled: dict[str, str] = {}
    missing: list[str] = []
    seen_missing: set[str] = set()

    def _sub(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        if key in variables:
            value = str(variables[key])
            filled[key] = value
            return value
        if key not in seen_missing:
            seen_missing.add(key)
            missing.append(key)
        return match.group(0)

    text = PLACEHOLDER_RE.sub(_sub, template.read())
    return RenderedPrompt(text=text, template=template, filled=filled, missing=missing)
