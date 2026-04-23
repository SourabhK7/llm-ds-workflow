# Pattern 04 — Experiment readout skeleton

**Problem this solves:** Writing an A/B test readout from scratch eats 60-90 minutes, mostly on structure and transitions. The analysis itself is usually 15 minutes of thinking. This pattern gets the structure drafted in under a minute so you can spend your time on the interpretation.

**The pattern:** Feed Claude the raw experiment metadata and top-line numbers, and have it produce a skeleton readout in a structure you've pre-specified. You then fill in the interpretation.

---

## The prompt template

```
Draft an A/B test readout using the structure below. Write in paragraphs,
not bullets. Be calibrated — do not claim causality beyond what the data
supports. Where the data is ambiguous, say so explicitly rather than
smoothing it over.

EXPERIMENT METADATA:
- Name: {experiment name}
- Hypothesis: {hypothesis}
- Audience: {segment, size}
- Duration: {start} to {end} ({N} days)
- Primary metric: {metric, definition}
- Guardrail metrics: {list}
- Randomization unit: {user / session / device}

RESULTS:
Primary metric:
- Control: {mean, N, confidence interval}
- Treatment: {mean, N, confidence interval}
- Relative lift: {%}
- p-value: {value}
- Practical significance threshold: {what you set pre-registration, if any}

Guardrails:
- {metric 1}: {result, direction, significance}
- {metric 2}: {result, direction, significance}

Segment breakdowns (if any):
- {segment}: {result}

STRUCTURE:
1. TL;DR (2-3 sentences): the decision you're recommending and why.
2. What we tested and why: the hypothesis in plain language.
3. What we found: primary metric result, in calibrated language.
4. Guardrails: did anything move that shouldn't have?
5. Segments / heterogeneity: was the effect uniform or concentrated?
6. What this means: the business interpretation.
7. Caveats: what this readout cannot tell us. Be specific.
8. Recommendation: ship / don't ship / iterate, with reasoning.

Do not invent numbers. If a section has no data provided, write
"[placeholder: need to fill in]" rather than guessing.
```

## Why this structure

Each section exists because experienced readers look for it:

- **TL;DR first** — exec readers stop here 80% of the time. Put the decision at the top.
- **"What we tested"** before "what we found" — frames the result in context. Readers who missed the pre-reg need this.
- **Guardrails as their own section** — not a footnote. Secondary metrics moving in unexpected directions is often the most interesting part of an experiment.
- **Segments/heterogeneity** — average treatment effects lie. Explicit heterogeneity analysis separates adequate from good readouts.
- **Caveats as their own section** — if caveats are sprinkled through the results, readers miss them. Grouping them forces the writer to acknowledge limitations explicitly.
- **Recommendation last** — logical conclusion, not a forced summary.

## What Claude is good at here

- Producing clean, readable prose for sections 2, 3, and 6. These are mostly restatement and framing work.
- Catching internal inconsistencies (e.g., a TL;DR that says "ship" while the caveats say "underpowered").
- Suggesting caveats you might have missed (section 7).

## What Claude is bad at here

- Deciding ship vs. don't ship. It will default to ship if anything is positive, or hedge endlessly if anything is mixed. **You decide; the LLM drafts the language around your decision.**
- Weighing guardrail trade-offs against primary metric lift. This is judgment.
- Knowing your org's bar for shipping (some orgs ship anything non-negative; others require a clear lift + no guardrail deterioration).

## Example

Full input/output example in [examples/ab-readout-example.md](../examples/ab-readout-example.md).

---

## Failure mode

If you give Claude marginal or null results, it tends to reach for language that implies more signal than the data supports ("suggests a potential trend toward..."). Pattern 05 (calibrated language pass) is specifically a second prompt to strip this out. In practice, I run 04 then 05 for any experiment where the primary result is non-significant or close to null.

## When to skip

- Experiments with a clear dominant outcome (e.g., p < 0.001, 10% lift on primary metric, no guardrail issues). You can write these in 15 minutes without a skeleton.
- Exploratory analyses that aren't real A/B tests. Use a different structure.
