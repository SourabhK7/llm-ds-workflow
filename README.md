# LLM-Accelerated DS Workflow

[![test](https://github.com/SourabhK7/llm-ds-workflow/actions/workflows/test.yml/badge.svg)](https://github.com/SourabhK7/llm-ds-workflow/actions/workflows/test.yml)

A working playbook of prompt patterns for product data science: warehouse SQL drafting, A/B test readouts, and stakeholder summaries. Built around Claude (chat + API) and Cursor.

These are patterns I actually use day-to-day. They cut my analysis turnaround by roughly 50% — informally measured by tracking time-to-first-draft across a handful of recurring work types (ad-hoc SQL, experiment readouts, exec summaries) over several weeks.

The goal isn't prompts that sound clever. It's prompts that reliably produce first drafts good enough to edit rather than rewrite.

---

## Why this exists

Most "AI for data science" content is either (a) toy examples that break on real warehouse schemas, or (b) vague advice like "give Claude more context." Neither is useful when you have a Slack from your PM at 4pm asking for a readout by EOD.

The patterns here are narrower and more opinionated:

- **SQL drafting** assumes you work in a messy, undocumented warehouse with partitioned event tables and no clean dbt models.
- **A/B readouts** assume the reader is a PM or design lead, not a statistician — so the language has to be calibrated, not jargon-heavy.
- **Stakeholder summaries** assume you've already done the analysis and just need to compress it without losing the caveats.

Each pattern includes the prompt, a short example of what it produces, and — importantly — the failure modes I've hit and how I mitigate them.

---

## The 11 patterns

### Warehouse SQL
1. [Schema-anchored query drafting](patterns/01-schema-anchored-sql.md) — how to get Claude to write SQL against a warehouse it's never seen without hallucinating columns
2. [Cohort definition clarifier](patterns/02-cohort-clarifier.md) — turning a vague PM request ("engaged users who churned") into a defensible operational definition before writing any SQL
3. [SQL self-review](patterns/03-sql-self-review.md) — a second-pass prompt that catches the specific mistakes LLMs make in window functions and joins

### A/B test readouts
4. [Experiment readout skeleton](patterns/04-ab-readout-skeleton.md) — a structured first draft that forces the right sections in the right order
5. [Calibrated language pass](patterns/05-calibrated-language.md) — rewrites over-confident claims ("X caused a lift") into honest ones ("X is consistent with a lift") without becoming mealy-mouthed
6. [Null result framing](patterns/06-null-result-framing.md) — the single hardest writing task in product DS, and the one LLMs help with most

### Stakeholder communication
7. [Exec TL;DR compression](patterns/07-exec-tldr.md) — producing a 3-bullet summary that preserves the caveats the PM will otherwise drop
8. [Slack-ready explanation](patterns/08-slack-ready.md) — same finding, different register; optimized for "can be understood without opening a doc"
9. [Pre-mortem for analyses](patterns/09-pre-mortem.md) — before you run the query, have Claude surface the ways this analysis could be wrong or misleading

### Metric hygiene & diagnostics
10. [Metric interpretation sanity check](patterns/10-metric-sanity-check.md) — before you share a number, a fast check that the numerator/denominator/time window actually means what you think it means
11. [Anomaly decomposition](patterns/11-anomaly-decomposition.md) — when a metric moves and a PM asks "why?", a ranked decomposition tree that forces you to rule out instrumentation and composition shifts *before* talking about behavior

---

## How I use this in practice

Daily workflow looks roughly like:

1. **Morning**: if I have an experiment readout or deep-dive due, I open the relevant pattern in Cursor alongside the notebook. I paste the schema / experiment config / raw numbers into the prompt template and get a first draft in under a minute.
2. **Midday**: for ad-hoc SQL, I keep pattern 01 (schema-anchored drafting) in a saved Claude chat with my warehouse's key table schemas already loaded as context. New queries take ~30 seconds to draft, ~2 minutes to review.
3. **End of day**: if I'm writing a summary for a PM or exec, I use pattern 07 on the raw analysis doc. I almost always edit the output — but editing takes 5 minutes instead of writing taking 30.

The compounding value is less about any single prompt and more about **having a consistent structure** to fall back on when I'm tired or context-switching.

---

## What these patterns do NOT do

Being honest about this because it matters for anyone using them:

- **They do not replace judgment on statistical validity.** Pattern 05 helps calibrate *language*, not methodology. If your test had a peeking problem or an SRM, the LLM won't catch it.
- **They do not work well on truly novel analyses.** These are leverage tools for recurring work types. The first time you analyze a new kind of experiment or metric, you still have to think from scratch.
- **They do not remove the need to read the output carefully.** I've caught Claude confidently inventing a column name, misinterpreting a funnel step, and flipping the direction of an effect. All three happen rarely, but they happen. Every draft gets a human review pass.
- **They are not a substitute for warehouse documentation.** If your schemas are genuinely chaotic, no prompt pattern will save you — you need a data dictionary. The patterns assume you can provide decent schema context.

---

## Measured impact (on my own work)

Tracked informally across ~6 weeks on Adobe Acrobat B2B analytics work:

| Task type | Median time before | Median time after | Notes |
|---|---|---|---|
| Ad-hoc SQL (simple) | ~15 min | ~5 min | Biggest gains here |
| Ad-hoc SQL (multi-CTE) | ~45 min | ~25 min | LLM drafts the skeleton; I do the thinking on joins |
| Experiment readout | ~90 min | ~45 min | Mostly structural time savings |
| Exec summary | ~30 min | ~10 min | Format consistency is the main win |
| Pre-mortem / analysis planning | N/A (didn't do it) | ~10 min | New habit the LLM enabled |
| Anomaly investigation ("why is X down?") | ~60 min | ~25 min | Ordering discipline is where the savings come from |

Caveats: these are my own timings on my own work, not a controlled study. The "before" numbers are from memory and project retrospectives, not a log. Take them as directional.

---

## Structure

```
llm-ds-workflow/
├── README.md                  # this file
├── patterns/                  # the 10 pattern docs
├── llm_ds_workflow/           # Python library: load + render templates
│   ├── __init__.py
│   ├── core.py                # discovery + render logic
│   └── __main__.py            # CLI: list / show / render
├── tests/                     # pytest coverage of the library
├── examples/                  # full before/after examples with real(istic) inputs
│   ├── ab-readout-example.md
│   ├── sql-drafting-example.md
│   ├── exec-summary-example.md
│   ├── anomaly-decomposition-example.md
│   ├── run_ab_readout.py                    # runnable end-to-end demo
│   └── ab-readout-rendered-example.md       # checked-in demo output
└── templates/                 # copy-paste prompt templates
    ├── sql-draft.txt
    ├── ab-readout.txt
    └── exec-summary.txt
```

---

## Using from Python (optional)

The patterns and templates are also exposed as a small Python library so you can render a filled-in prompt programmatically instead of copy-pasting.

```bash
pip install -e .
```

```python
from llm_ds_workflow import render, list_templates

for t in list_templates():
    print(t.name, t.placeholders)

filled = render("ab-readout", {
    "experiment name": "onboarding_v2",
    "hypothesis": "adding a save-progress modal improves activation",
    # ...
})
print(filled.text)         # the ready-to-send prompt
print(filled.missing)      # placeholders you didn't fill
```

CLI equivalent:

```bash
python -m llm_ds_workflow list
python -m llm_ds_workflow list --templates
python -m llm_ds_workflow render ab-readout --var-file experiment.yaml --output prompt.txt
```

A complete end-to-end demo (fabricated experiment result → filled template → optional Claude call) is at [`examples/run_ab_readout.py`](examples/run_ab_readout.py). A checked-in rendered example at [`examples/ab-readout-rendered-example.md`](examples/ab-readout-rendered-example.md) shows what the filled prompt looks like without needing to run anything.

This library exists so the templates can plug into notebooks and analysis scripts, not just chat windows. The prose patterns in `patterns/` are still the primary artifact — the library is a convenience layer over them.

---

## Using with Cursor

Cursor's composer + `@docs` and `@code` references make these patterns work well against a live notebook or SQL file. My Cursor setup:

- **Rules file** (`.cursorrules`) includes the language calibration guidance from pattern 05, applied repo-wide so any AI-generated analysis text in notebooks inherits it.
- **Saved prompts** for patterns 01, 04, and 07 — the three I use most.
- **Context hygiene**: I paste the schema at the top of each SQL session rather than relying on Cursor to find it. Explicit > implicit.

A minimal `.cursorrules` example is in [templates/cursorrules-example.txt](templates/cursorrules-example.txt).

---

## Contributing / feedback

This is a personal playbook, so I'm not looking for PRs, but if you try a pattern and it breaks in an interesting way, open an issue — I'd genuinely like to know. Especially interested in failure modes on warehouse types I don't use (Snowflake, BigQuery — I mostly work in Databricks).

---

## Author

Sourabh Koul — Data Scientist, San Jose CA. [LinkedIn](https://www.linkedin.com/in/sourabhkoul/) · [GitHub](https://github.com/SourabhK7)
