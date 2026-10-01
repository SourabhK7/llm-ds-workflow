# Pattern 04: Experiment readout skeleton

Writing an A/B test readout from scratch takes 60 to 90 minutes, and most of that goes into structure and transitions. The actual thinking is maybe 15 minutes. This gets the structure drafted in under a minute so the time goes into interpretation.

Give Claude the experiment details and top-line numbers, have it fill in a structure you've already decided on, and then write the interpretation yourself.

## The prompt

```
Draft an A/B test readout using the structure below. Write in paragraphs,
not bullets. Be calibrated: do not claim causality beyond what the data
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

## Why this order

Each section is there because people reading readouts look for it.

The TL;DR goes first because most exec readers stop there, so the decision should be at the top. "What we tested" comes before "what we found" so the result has context, which matters for anyone who missed the original plan.

Guardrails get their own section rather than a footnote. A secondary metric moving the wrong way is often the most interesting thing in the whole test.

Segments get their own section because an average effect can hide a lot. Looking at where the effect actually landed is what separates an okay readout from a good one.

Caveats get their own section too. Scattered through the results, people skip them. Grouped together, the writer has to actually own the limitations.

The recommendation goes last, as the conclusion the rest leads to.

## What Claude does well here

- Clean prose for sections 2, 3 and 6, which are mostly restating and framing.
- Noticing contradictions, like a TL;DR that says ship while the caveats say the test was underpowered.
- Suggesting caveats you forgot (section 7).

## What it doesn't do well

- Deciding whether to ship. It leans toward "ship" if anything is positive, or hedges forever if the results are mixed. You make the call, and it writes around your decision.
- Weighing a guardrail hit against a lift on the primary metric. That's judgment.
- Knowing your org's bar. Some teams ship anything that isn't negative, others want a clear lift and no guardrail damage.

## Example

There's a full input and output in [examples/ab-readout-example.md](../examples/ab-readout-example.md).

## Where it goes wrong

Give it marginal or null results and it reaches for language that suggests more signal than there is ("suggests a potential trend toward..."). Pattern 05 is a second prompt for stripping that out. For any test where the main result isn't significant or is close to zero, I run 04 and then 05.

## When not to bother

- Tests with an obvious result (say p < 0.001, a 10% lift on the primary metric, no guardrail problems). Those take 15 minutes to write without help.
- Exploratory analyses that aren't real A/B tests. They need a different structure.
