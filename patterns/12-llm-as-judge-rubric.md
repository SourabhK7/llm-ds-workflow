# Pattern 12: LLM-as-judge rubrics

You're evaluating something built on an LLM (a summarizer, an agent, a drafting tool) and you want more than eyeballing a few outputs. The usual approach is an LLM judge: a model scores each output against a rubric. The catch is that a vague rubric gives you vague scores. If the levels are "poor / acceptable / excellent," almost everything lands at "good," and you've paid for API calls to learn that the judge is polite.

The fix is to make every score level describe something you can point to in the output, not an adjective. "Excellent" can't be checked. "Every number in the output appears in the input at the same precision" can.

Use Claude to draft the rubric with you, using a few outputs you've already judged yourself.

## The prompt

```
I'm building an LLM-as-judge rubric for {feature description in one sentence}.

The judged output is: {what the LLM being evaluated produces, e.g.
"a written diagnosis of user drop-off in a funnel"}.

Here are 3-4 example outputs, each labeled with my own assessment:

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
- {e.g., "the model invents numbers not in the input"}
- {e.g., "the model uses causal language on observational data"}
- {e.g., "valid prose that misses the biggest finding"}

Produce a rubric with 4-6 criteria. For each criterion:

1. A one-line name.
2. What it measures, in one sentence, grounded in something an
   evaluator can point to in the output.
3. Anchors at scores 0, 1, 2. Each anchor MUST describe an observable
   behavior in the output. Adjectives without behavior ("clear",
   "helpful", "well-written") are not allowed.
4. For each anchor, 1-2 concrete examples of content that would qualify.

Also produce:
- Criteria you considered but rejected, and why.
- A calibration check: for each of my example outputs, the score you'd
  expect the rubric to give on each criterion, so I can see right away
  whether the rubric agrees with my own judgment.
```

## Anchors matter more than criteria

You can have a perfectly good criterion like "numerical accuracy" and still get useless scores if the levels are just "poor, ok, excellent." Here's the version I used in [activation-insight-agent](https://github.com/SourabhK7/activation-insight-agent/blob/main/evals/rubric.md):

- 2: every number in the diagnosis is within 1 percentage point of ground truth, and nothing is made up.
- 1: one number is off by 1 to 3 points, or one made-up number points the right way.
- 0: two or more errors, any error over 3 points, or a made-up number that misstates the size of something.

Now the judge has to actually look at the numbers to score it, so scores repeat across runs, and when two judges disagree it tells you something.

The calibration check at the end of the prompt is your safety net. If the rubric would score your "strong" example as mediocre, either the rubric measures the wrong thing or your own read is off. Better to find out before running the eval.

## A lesson from running one

A rubric is only as good as what the judge checks against. In the activation-insight-agent eval, the judge scored one version's numerical accuracy at 1.33 out of 2. When I recomputed every number it had marked down, they were all correct. The model had reported some rates (by signup week, by country) that weren't in the judge's ground-truth file, and the judge treated "not in my file" as "made up."

If a criterion says "check against ground truth," the ground truth has to cover everything an output might reasonably say. Otherwise the judge reports failures that have nothing to do with correctness. Spot-check the low scores by hand before you believe them.

## Where it goes wrong

The rubric can be too easy. If any coherent output gets a 2, every criterion maxes out. Set the top level so a mediocre attempt would miss it.

Judges have their own tastes. Even with good anchors, a judge model tends to prefer longer, more hedged, more structured answers. If you can, have a second model grade a sample and look at where they disagree. That's where the anchors need work.

Don't make the judge do arithmetic. If a criterion needs a calculation ("within 3 points of the true value"), the judge is as likely to get it wrong as the model being judged. Compute it in code and hand the judge the result.

Rubrics go stale. Once you improve the system, the 0-level failures stop happening and that criterion scores 2 every time. That means it stopped telling you anything. Retire it and add a harder one.

## When not to bother

- You're looking at one output. Just read it carefully.
- You have ground-truth labels. Measure agreement with the labels in code and skip the judge.
- The thing you care about is pass/fail, like "the SQL runs." Check it in code.

## Related patterns

- Pattern 03 (SQL self-review): the same idea of a second pass with a specific checklist, applied to code.
- Pattern 05 (calibrated language): a good source for a "causal language" criterion.
- Pattern 09 (pre-mortem): write the rubric before you run the eval, for the same reason you'd do a pre-mortem before an analysis.
