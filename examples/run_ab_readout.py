"""
End-to-end demo of pattern 04 (A/B readout skeleton) using the llm_ds_workflow
library. Takes a realistic (but fabricated) experiment result, renders the
ab-readout template, prints the filled prompt, and — if ANTHROPIC_API_KEY is
set — calls Claude to actually produce the readout.

Run:
    python examples/run_ab_readout.py             # just render, no API call
    python examples/run_ab_readout.py --call-api  # render AND call Claude

This is the shape of thing you'd script for real experiment analysis: read
the experiment config from your platform, plug it into the template, get a
first draft back that you can then edit.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make the package importable when running from the repo without installing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from llm_ds_workflow import render  # noqa: E402


# Fabricated experiment result. Realistic-shaped: well-powered primary metric,
# clean guardrails, mildly divergent segments. Real experiment data would come
# from your A/B testing platform's API or a warehouse query.
EXPERIMENT = {
    "experiment name": "onboarding_save_prompt_v2",
    "hypothesis": (
        "Adding an optional 'save your progress' modal at step 3 of onboarding "
        "reduces abandonment and increases Day 1 activation."
    ),
    "segment, size": "New web signups in US/CA/UK/AU, 50/50 split, ~24,800 users total",
    "start": "2026-06-02",
    "end": "2026-06-16",
    "N": "14",
    "metric, definition": (
        "Day 1 activation rate — fraction of new signups who complete a first "
        "meaningful in-app action within 24h of signup"
    ),
    "list": "Day 7 retention, support contact rate (first 7 days)",
    "user / session / device": "user_id (at signup)",
    "mean, N, confidence interval": (
        # Filled with a compact one-liner covering both arms — the template
        # expects "Control:" and "Treatment:" lines; we render one shared
        # summary and let the LLM narrate. (The template is flexible about
        # exact number formatting.)
        "38.1% control (N=12,450) · 40.9% treatment (N=12,388), 95% CI on "
        "relative lift [2.4%, 12.3%]"
    ),
    "%": "+7.3% relative",
    "value": "0.004",
    "what you set pre-registration, if any": "MDE = 3% relative lift",
    "metric 1": "Day 7 retention: 24.1% control vs 24.8% treatment, p=0.31 (not significant)",
    "metric 2": "Support contact rate: 4.2% control vs 4.5% treatment, p=0.48 (not significant)",
    "segment": (
        "US +8.1% (p=0.008), UK +7.8% (p=0.03), CA +6.9% (p=0.19, underpowered), "
        "AU +4.2% (p=0.41, underpowered) — effect directionally positive in all four"
    ),
    "result": "see segment breakdown above",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--call-api", action="store_true", help="Also call Claude and print the readout.")
    parser.add_argument("--output", help="Write rendered prompt (and readout if --call-api) to file.")
    args = parser.parse_args()

    rendered = render("ab-readout", EXPERIMENT)

    print("=" * 70, file=sys.stderr)
    print("Filled prompt (would be sent to Claude):", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(rendered.text)

    if rendered.missing:
        print(
            f"\n[warning] {len(rendered.missing)} placeholder(s) unfilled: "
            f"{', '.join(rendered.missing)}",
            file=sys.stderr,
        )

    if args.output and not args.call_api:
        Path(args.output).write_text(rendered.text, encoding="utf-8")
        print(f"\nRendered prompt written to {args.output}", file=sys.stderr)
        return 0

    if not args.call_api:
        return 0

    # --- Optional: actually call Claude. ---
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nERROR: --call-api requires ANTHROPIC_API_KEY.", file=sys.stderr)
        return 1

    try:
        from anthropic import Anthropic
    except ImportError:
        print("\nERROR: --call-api requires `pip install anthropic`.", file=sys.stderr)
        return 1

    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=os.environ.get("MODEL", "claude-sonnet-5"),
        max_tokens=2000,
        messages=[{"role": "user", "content": rendered.text}],
    )
    readout = "\n".join(b.text for b in resp.content if hasattr(b, "text")).strip()

    print("\n" + "=" * 70, file=sys.stderr)
    print("Claude's readout draft:", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(readout)

    if args.output:
        Path(args.output).write_text(
            "# Rendered prompt\n\n" + rendered.text + "\n\n---\n\n# Claude's draft\n\n" + readout,
            encoding="utf-8",
        )
        print(f"\nOutput written to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
