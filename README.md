# LLM-Accelerated DS Workflow

[![test](https://github.com/SourabhK7/llm-ds-workflow/actions/workflows/test.yml/badge.svg)](https://github.com/SourabhK7/llm-ds-workflow/actions/workflows/test.yml)

The prompts I use for product data science work with Claude and Cursor: drafting SQL against a warehouse, A/B test readouts, exec summaries, figuring out why a metric moved, and a few more. There's also a small Python library that fills in the templates, and worked examples of what each one produces.

Patterns 1 to 11 are the ones I use regularly. On the recurring work (ad-hoc SQL, experiment readouts, exec summaries) my time to a first draft is down about 50%, tracked informally over a few weeks. The bigger change for me is that most of the work becomes editing a decent draft instead of writing from a blank page, which is a lot easier at 4pm on a Friday. Patterns 12 to 15 are newer and haven't been through as much real use yet.

None of these are clever prompt tricks. Each one is a structure that gets you a first draft worth editing, on messy warehouse data, for PMs and design leads who don't want jargon.

## Why I wrote these down

Most "AI for data science" material is either toy examples that fall apart on a real warehouse schema, or advice like "give Claude more context." Neither helps much when a PM pings you at 4pm wanting a readout by end of day.

These are narrower. The SQL patterns assume a messy, undocumented warehouse with partitioned event tables and no clean dbt models. The A/B readout patterns assume the reader is a PM, not a statistician, so the language has to be careful without being technical. The summary patterns assume the analysis is done and you just need to shorten it without losing the caveats.

Each pattern has the prompt, a short example of what it produces, and the ways it's gone wrong for me and what I do about it.

## The patterns

### Warehouse SQL
1. [Schema-anchored query drafting](patterns/01-schema-anchored-sql.md): getting Claude to write SQL against a warehouse it's never seen without inventing columns
2. [Cohort definition clarifier](patterns/02-cohort-clarifier.md): turning a vague request ("engaged users who churned") into a definition you can defend, before writing any SQL
3. [SQL self-review](patterns/03-sql-self-review.md): a second pass that catches the mistakes LLMs tend to make in window functions and joins

### A/B test readouts
4. [Experiment readout skeleton](patterns/04-ab-readout-skeleton.md): a first draft with the right sections in the right order
5. [Calibrated language pass](patterns/05-calibrated-language.md): rewriting "X caused a lift" as "X is consistent with a lift" without making it mushy
6. [Null result framing](patterns/06-null-result-framing.md): the hardest writing task in product DS, and the one where LLMs help me the most

### Stakeholder communication
7. [Exec TL;DR](patterns/07-exec-tldr.md): a 3-bullet summary that keeps the caveats a PM would otherwise drop
8. [Slack-ready explanation](patterns/08-slack-ready.md): the same finding, written so someone can follow it without opening a doc
9. [Pre-mortem for analyses](patterns/09-pre-mortem.md): before running the query, list the ways this analysis could be wrong or misleading

### Metric checks and diagnostics
10. [Metric sanity check](patterns/10-metric-sanity-check.md): before sharing a number, a quick check that the numerator, denominator and time window mean what you think
11. [Anomaly decomposition](patterns/11-anomaly-decomposition.md): when a metric moves and someone asks why, a ranked list of things to check, starting with instrumentation and traffic mix before behavior

### Evals and analysis design (newer)
12. [LLM-as-judge rubrics](patterns/12-llm-as-judge-rubric.md): writing eval rubrics where every score level describes something you can point to in the output
13. [Retention curve write-ups](patterns/13-retention-curve-narrative.md): describing D1/D7/D30 curves so a PM can act on them, without comparing cohorts that aren't old enough yet
14. [Explaining segments](patterns/14-segmentation-storytelling.md): turning clustering output into named segments people will remember and use
15. [Exec Q&A prep](patterns/15-exec-qa-prep.md): the hardest questions an exec is likely to ask about a readout, with draft answers

## How I use them

Mornings, if a readout or deep dive is due, I open the matching pattern in Cursor next to the notebook, paste in the schema, experiment config or numbers, and get a first draft in about a minute.

For ad-hoc SQL I keep pattern 1 in a saved Claude chat with the main table schemas already loaded. A new query takes about 30 seconds to draft and 2 minutes to review.

When I'm writing up something for a PM or exec, I run pattern 7 on the analysis doc. I almost always edit what comes out, but editing takes 5 minutes and writing it from scratch took 30.

Most of the value isn't any single prompt. It's having the same structure to fall back on when I'm tired or switching between things.

## What they don't do

- They don't replace your own judgment about whether the analysis is valid. Pattern 5 fixes the language, not the method. (I used to say here that an LLM won't notice a peeking problem or a sample ratio mismatch. When I actually tested that in [llm-data-guardrails](https://github.com/SourabhK7/llm-data-guardrails), Claude Sonnet and Opus caught both every time. I'd still check myself.)
- They don't help much with genuinely new analyses. They speed up work you do repeatedly. The first time you analyze a new kind of experiment or metric, you still have to think it through.
- You still have to read the output. I've caught Claude inventing a column name, misreading a funnel step, and flipping the direction of an effect. It's rare, but it happens, so everything gets a human read.
- They won't fix missing documentation. If your schemas are a mess, you need a data dictionary first. The patterns assume you can give decent schema context.

## Time saved on my own work

Tracked informally over about 6 weeks on Adobe Acrobat B2B analytics work:

| Task type | Median time before | Median time after | Notes |
|---|---|---|---|
| Ad-hoc SQL (simple) | ~15 min | ~5 min | Biggest gains here |
| Ad-hoc SQL (multi-CTE) | ~45 min | ~25 min | The LLM drafts the skeleton; I do the thinking on joins |
| Experiment readout | ~90 min | ~45 min | Mostly from not having to work out the structure each time |
| Exec summary | ~30 min | ~10 min | Consistent format is the main win |
| Pre-mortem / planning | didn't do it | ~10 min | A habit I only picked up because it got cheap |
| "Why is X down?" | ~60 min | ~25 min | Checking things in the right order is where the time goes |

These are my own timings on my own work, not a controlled study, and the "before" numbers come from memory and project retros, not a log. Treat them as rough.

## What's in the repo

```
llm-ds-workflow/
├── README.md
├── patterns/                  # the 15 pattern docs
├── llm_ds_workflow/           # Python library: load + render templates
│   ├── __init__.py
│   ├── core.py                # discovery + render logic
│   └── __main__.py            # CLI: list / show / render
├── tests/                     # pytest coverage of the library
├── examples/                  # full before/after examples with realistic inputs
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

## Using it from Python

The templates are also available as a small library, so you can fill one in from a notebook or script instead of copy-pasting.

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
print(filled.text)         # the prompt, ready to send
print(filled.missing)      # placeholders you didn't fill
```

Or from the command line:

```bash
python -m llm_ds_workflow list
python -m llm_ds_workflow list --templates
python -m llm_ds_workflow render ab-readout --var-file experiment.yaml --output prompt.txt
```

[`examples/run_ab_readout.py`](examples/run_ab_readout.py) goes end to end: a made-up experiment result, the filled template, and an optional Claude call. [`examples/ab-readout-rendered-example.md`](examples/ab-readout-rendered-example.md) shows the filled prompt if you don't want to run anything.

The pattern docs are still the main thing here. The library just saves copy-pasting.

## Using it with Cursor

With Cursor's composer and `@docs`/`@code` references, these work well against a live notebook or SQL file. My setup:

- A `.cursorrules` file with the language guidance from pattern 5, so any analysis text the AI writes in my notebooks follows it.
- Saved prompts for patterns 1, 4 and 7, the three I use most.
- I paste the schema at the top of each SQL session instead of trusting Cursor to find it.

There's a minimal `.cursorrules` example in [templates/cursorrules-example.txt](templates/cursorrules-example.txt).

## Feedback

This is a personal playbook, so I'm not really looking for PRs. But if you try a pattern and it breaks in an interesting way, please open an issue. I'm especially curious how they hold up on Snowflake or BigQuery, since I mostly use Databricks.

Sourabh Koul · [LinkedIn](https://www.linkedin.com/in/sourabhkoul/) · [GitHub](https://github.com/SourabhK7)
