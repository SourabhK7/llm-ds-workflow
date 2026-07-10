"""
CLI entry point.

    python -m llm_ds_workflow list
    python -m llm_ds_workflow list --templates
    python -m llm_ds_workflow show ab-readout
    python -m llm_ds_workflow render ab-readout --var-file vars.yaml
    python -m llm_ds_workflow render ab-readout --var "experiment name=onboarding_v1" \\
        --var "hypothesis=..." --output filled.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .core import list_patterns, list_templates, load_pattern, load_template, render


def _load_var_file(path: Path) -> dict[str, Any]:
    if path.suffix in (".json",):
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as e:
            raise SystemExit(
                "PyYAML not installed. `pip install pyyaml`, or pass --var-file as JSON."
            ) from e
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raise SystemExit(f"Unrecognized var-file extension: {path.suffix}. Use .json, .yaml, or .yml.")


def cmd_list(args: argparse.Namespace) -> int:
    if args.templates:
        for t in list_templates():
            print(f"{t.name}  (placeholders: {', '.join(t.placeholders) or 'none'})")
    else:
        for p in list_patterns():
            print(f"{p.name}  —  {p.title}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    # Try template first, then pattern. `show ab-readout` shows the template;
    # `show 01-schema-anchored-sql` shows the pattern doc.
    try:
        t = load_template(args.name)
        print(t.read())
        return 0
    except KeyError:
        pass
    try:
        p = load_pattern(args.name)
        print(p.read())
        return 0
    except KeyError:
        print(f"No template or pattern named {args.name!r}.", file=sys.stderr)
        return 1


def cmd_render(args: argparse.Namespace) -> int:
    variables: dict[str, Any] = {}
    if args.var_file:
        variables.update(_load_var_file(Path(args.var_file)))
    for kv in args.var or []:
        if "=" not in kv:
            print(f"--var expects key=value, got {kv!r}", file=sys.stderr)
            return 1
        k, v = kv.split("=", 1)
        variables[k.strip()] = v

    try:
        result = render(args.name, variables)
    except KeyError as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.output:
        Path(args.output).write_text(result.text, encoding="utf-8")
        print(f"Rendered -> {args.output}", file=sys.stderr)
    else:
        print(result.text)

    if result.missing:
        print(
            f"\n[warning] {len(result.missing)} placeholder(s) unfilled: "
            f"{', '.join(result.missing)}",
            file=sys.stderr,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m llm_ds_workflow")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List patterns (default) or templates.")
    p_list.add_argument("--templates", action="store_true", help="List templates instead of patterns.")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Print a template or pattern by name.")
    p_show.add_argument("name")
    p_show.set_defaults(func=cmd_show)

    p_render = sub.add_parser("render", help="Fill a template with variables.")
    p_render.add_argument("name", help="Template name (e.g. ab-readout).")
    p_render.add_argument("--var-file", help="Path to a JSON or YAML file of variables.")
    p_render.add_argument("--var", action="append", help="Key=value variable. Repeatable.")
    p_render.add_argument("--output", help="Write to file. Default: stdout.")
    p_render.set_defaults(func=cmd_render)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
