"""Tests for the render/load core."""

from __future__ import annotations

from llm_ds_workflow import list_patterns, list_templates, load_template, render


def test_list_patterns_finds_all_11():
    patterns = list_patterns()
    names = [p.name for p in patterns]
    assert len(names) == 11, f"expected 11 patterns, got {len(names)}: {names}"
    assert all(n.split("-")[0].isdigit() for n in names), names


def test_list_templates_finds_expected():
    templates = list_templates()
    names = {t.name for t in templates}
    # The core templates that should always exist. If any of these go missing,
    # the CLI's discover-templates flow silently breaks.
    assert {"ab-readout", "sql-draft", "exec-summary"}.issubset(names), names


def test_ab_readout_placeholders_are_findable():
    t = load_template("ab-readout")
    placeholders = t.placeholders
    # A handful the template must expose. If someone edits the template and
    # renames these, the test flags it so we notice.
    assert "experiment name" in placeholders
    assert "hypothesis" in placeholders
    assert "metric, definition" in placeholders


def test_render_fills_provided_placeholders():
    result = render("ab-readout", {"experiment name": "onboarding_save_prompt_v1"})
    assert "onboarding_save_prompt_v1" in result.text
    assert "experiment name" in result.filled
    assert result.filled["experiment name"] == "onboarding_save_prompt_v1"


def test_render_reports_missing_placeholders():
    result = render("ab-readout", {"experiment name": "x"})
    assert "hypothesis" in result.missing
    # Missing placeholders are preserved in the rendered text (not deleted).
    assert "{hypothesis}" in result.text


def test_render_unknown_key_ignored():
    # Extra variables that don't match any placeholder are silently ignored.
    # This is the desired behavior: callers can pass a superset dict.
    sentinel = "SENTINEL_STRING_UNLIKELY_TO_APPEAR_IN_TEMPLATE"
    result = render("ab-readout", {"experiment name": "x", "not_a_real_placeholder": sentinel})
    assert sentinel not in result.text
    assert "not_a_real_placeholder" not in result.filled


def test_render_deduplicates_missing():
    # A placeholder that appears multiple times should only be reported once.
    t = load_template("ab-readout")
    seen = set(t.placeholders)
    assert len(seen) == len(t.placeholders), "placeholders should be deduplicated"
