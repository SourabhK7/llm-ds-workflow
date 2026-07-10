"""
llm-ds-workflow — a small library over the prompt patterns in this repo.

The patterns live in `patterns/` (prose) and the templates in `templates/`
(prompt scaffolds with placeholders). This module makes them programmatically
accessible so you can render a filled-in prompt from Python (or a notebook)
instead of copy-pasting text into a chat window.

Public API:
    list_patterns() -> list[Pattern]
    list_templates() -> list[Template]
    load_template(name) -> Template
    render(template, variables) -> RenderedPrompt
"""

from __future__ import annotations

from .core import (
    Pattern,
    RenderedPrompt,
    Template,
    list_patterns,
    list_templates,
    load_pattern,
    load_template,
    render,
)

__all__ = [
    "Pattern",
    "RenderedPrompt",
    "Template",
    "list_patterns",
    "list_templates",
    "load_pattern",
    "load_template",
    "render",
]

__version__ = "0.1.0"
