# Pattern 12 — LLM-as-judge rubric authoring

**Problem this solves:** You're evaluating an LLM-powered feature (summarizer, agent, classifier, drafter) and you want more than eyeballed spot-checks. The standard move is LLM-as-judge: a stronger model scores each output against a rubric. But a bad rubric produces cheerful garbage — every output scores 4/5 and you learn nothing. A good rubric is harder to write than the feature it's evaluating.

**The pattern:** Before you run a single eval, use Claude to co-author the rubric with you. Feed it (a) the feature's purpose, (b) three or four example outputs you already know are good, bad, and borderline, and (c) the specific failure modes you're worried about. Ask it to produce criteria with *behavioral anchors at each score point*, not adjectives.

The single non-negotiable move: **every score point has to describe a concrete observable, not a feeling.** "Excellent" is not a score anchor. "Uses at least two of the three source facts and does not introduce a new claim" is.

---

## Why this exists

Most "LLM-as-judge" rubrics you see in blog posts are unusable:

- Score 1: poor
- Score 3: acceptable
- Score 5: excellent

Run this on 50 outputs and you'll find the judge scores almost everything a 4. The rubric has no discriminating power because the anchors have no content. You've spent API calls to learn that the judge is polite.

Worse, ambiguous rubrics let the judge and the developer both anchor on their priors. The judge says "this looks like a real analysis" and gives it a 5; the developer sees the score and ships it. Nobody has actually checked whether the output is correct.

A rubric with behavioral anchors forces both the judge and reviewer to look at specific features of the output. You stop grading vibes and start grading properties.

---

## The prompt template

```
I'm building an LLM-as-judge rubric for {feature description in one sentence}.

The judged output is: {what the LLM being evaluated produces —
e.g., "a written diagnosis of user drop-off in a funnel"}.

Here are 3-4 example outputs, each labeled with my ground-truth
assessment:

EXAMPLE 1 (I would rate this: strong):
{paste output}
Why it's strong: {2-3 sentences on what specifically works}

EXAMPLE 2 (I would rate this: weak):
{paste output}
Why it's weak: {2-3 sentences on what specifically fails}

EXAMPLE 3 (I would rate this: borderline):
{paste output}
Why it's borderline: {2-3 sentences on the ambiguity}

The specific failure modes I want the rubric to catch:
- {failure mode 1 — e.g., "the model invents numbers not in the input"}
- {failure mode 2 — e.g., "the model uses causal language on
  observational data"}
- {failure mode 3 — e.g., "the model produces valid prose but misses
  the biggest finding"}

Produce a rubric with 4-6 CRITERIA. For each criterion:

1. A one-line name.
2. What it measures, in one sentence — grounded in something an
   evaluator can point to in the output, not a feeling.
3. Anchors at scores {0, 1, 2} (or 0-2 / 0-3, your choice; keep
   the range narrow to force the judge to commit). Each anchor
   MUST describe an observable behavior in the output. Adjectives
   without behavior anchors ("clear", "helpful", "well-written")
   are banned.
4. For each anchor, 1-2 concrete examples of language or content
   that would qualify.

Also produce:

- A section on "criteria I considered but rejected", with reasons —
  so I can see what tradeoffs the rubric is making.
- A calibration check: for each of my 3 example outputs, predict
  the score the rubric should give on each criterion. This lets me
  spot immediately whether the rubric matches my priors or not.
```

---

## Why the anchors matter more than the criteria

The failure mode I hit repeatedly when I first started writing eval rubrics: I'd write good criteria, then anchor them with adjectives, then act surprised when the judge couldn't discriminate. "Numerical accuracy" as a criterion is fine. "0 = poor, 1 = ok, 2 = excellent" is not.

Rewrite the same criterion with behavioral anchors:

- **0** — Contains at least one numeric claim that does not appear in the input, OR restates a number with a different unit than the input specifies.
- **1** — All numeric claims trace back to the input, but at least one is stated with less precision than the input provides (e.g., input says "34.2%", output says "about a third").
- **2** — Every numeric claim in the output appears in the input at the same precision, and units are preserved.

Now the judge has to *look at the numbers* to score. The score becomes reproducible across runs, and disagreements between judges are diagnostic rather than random.

The calibration check at the end of the prompt is the safety net. If the rubric predicts your "strong" example scores 1s across the board, your rubric is either measuring the wrong thing or your intuition is wrong. Either way, you find out before you run the eval, not after.

---

## Example

**Feature**: A pandas + LLM agent that takes funnel event data and produces a written diagnosis of where users drop off. (See `activation-insight-agent` for the real implementation.)

**Failure modes worried about**:
- The LLM invents conversion rates not in the input
- The LLM uses causal language ("mobile UI is broken") when the data only shows correlations
- The LLM buries the biggest finding under generic commentary

**Rubric that Claude drafted** (excerpt, criteria 1 and 3 of 6):

> **Criterion 1: Numerical grounding**
>
> Measures whether every quantitative claim in the diagnosis traces back to the structured findings input.
>
> - **0** — At least one numeric claim in the output does not appear in the input findings JSON, or a rate is stated with a wrong unit (e.g., "26% of users converted" when input says end_to_end_conversion is 0.26, but the diagnosis quotes it as "26 out of every 50").
> - **1** — All numeric claims trace to the input, but at least one is rounded to a coarser precision than the input provides (e.g., input says 34.2%, output says "roughly a third"), OR one comparison is stated in a way that requires an implicit computation (e.g., "twice as high as" when the two numbers are actually 1.8x apart).
> - **2** — Every numeric claim in the diagnosis appears in the input at the same precision. Ratios and comparisons are supported by numbers explicitly in the input.
>
> **Criterion 3: Causal language discipline**
>
> Measures whether the diagnosis uses causal language on observational funnel data (which cannot support causal claims).
>
> - **0** — Uses "caused", "drove", "led to", "because of", "due to", or similar direct-causal verbs to describe why a segment behaves differently, without any hedging language nearby.
> - **1** — Uses hedged causal language ("suggests", "consistent with", "coincides with", "likely reflects"), or mixes causal and correlational framings within the same paragraph.
> - **2** — Consistently uses correlational language. Causal hypotheses are explicitly flagged as hypotheses. No direct-causal verbs applied to observational findings.

**Calibration check**: On my "strong" example, Claude predicted (2, 2, 2, 1, 2, 2) — 11/12. My gut said the same output was a 12/12. The 1 was on criterion 4 (finding prioritization); Claude spotted a weaker headline than I'd noticed. That's the rubric working *as designed* — surfacing something I missed.

**What I did with the rubric**: Ran it in `evals/run_eval.py` against 10 synthetic funnels, structured-findings arm vs. naive-baseline arm. Full write-up in the activation-insight-agent repo. The numerical grounding criterion turned out to be the least discriminating — Sonnet 5 didn't hallucinate numbers on either arm — which was itself a finding worth reporting.

---

## Failure modes of this pattern

**Judges can still cheat if the rubric is too easy.** If your "2" anchor is trivially met by any coherent output, the whole rubric ceilings. Aim for anchors where "2" requires the model to do something a mediocre attempt would miss.

**Judges have their own priors.** Even with good anchors, a judge model prefers verbose outputs, prefers hedged language, prefers structure. Cross-validate with a second judge model (Haiku scoring alongside Sonnet, say) and look at criteria where they diverge — that's where the anchors need more work.

**Anchors that require calculation.** If a criterion says "score 2 if the segment finding is within 3pp of the actual", the judge now has to do arithmetic to score it. Judges are as bad at arithmetic as the model being judged. Move computable checks *outside* the judge — pass them as pre-computed booleans in the input to the judge.

**The rubric gets stale.** If you improve the underlying feature, the "0" anchors stop occurring. Everything scores 2 on that criterion. That's not a good thing — it means the rubric has lost signal. Retire criteria that stop discriminating and add harder ones.

## When to skip

- **You're evaluating a single output.** A rubric is overkill for one-shot analysis; just read it critically.
- **You have ground-truth labels for the outputs.** If you can compare against a gold standard programmatically, skip the LLM judge and just measure agreement with the labels.
- **The failure mode is a hard yes/no** (e.g., "the SQL runs without error"). Assert that in code, don't ask a judge.

## Related patterns

- Pattern 03 (SQL self-review) — the same "second pass with a specific checklist" idea, applied to code instead of eval.
- Pattern 05 (calibrated language) — much of criterion 3 ("causal language discipline") comes straight from calibrated language work.
- Pattern 09 (pre-mortem) — write the rubric *before* running the eval, for the same reason you write a pre-mortem before running the analysis.
