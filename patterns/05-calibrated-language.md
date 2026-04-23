# Pattern 05 — Calibrated language pass

**Problem this solves:** LLM-drafted analysis text consistently over-claims. It reaches for "caused", "drove", "led to" when the data only supports "consistent with" or "associated with". This matters because calibration errors in readouts compound into bad product decisions.

It is also the single pattern with the highest impact-per-effort ratio. Running this 30-second pass on any analysis text removes a subtle failure mode that otherwise propagates into presentations and decision docs.

**The pattern:** Take drafted analysis text and ask Claude to rewrite it with calibrated causal language, specifically addressing the claims that go beyond what a correlational or experimental analysis can support.

---

## The prompt template

```
Below is analysis text I've drafted. Please rewrite it so that the causal
language is calibrated to what the underlying method can actually support.

Context about the method:
- Analysis type: {A/B test | observational / correlational | quasi-experimental | descriptive}
- Key design issues (if any): {peeking, low power, post-hoc segment, etc.}

Rules for the rewrite:
1. "Caused", "drove", "led to", "resulted in" → only keep these if it's
   a properly-run A/B test with a significant primary effect AND no
   major design issues. Otherwise, downgrade to "is associated with",
   "coincided with", or "is consistent with".
2. "Significant" must mean statistically significant. If I'm using it
   loosely ("a significant portion of users"), replace with "a notable
   portion" or a specific percentage.
3. "The data shows" → only if the data really does show that
   unambiguously. Otherwise: "the data is consistent with" or "the data
   suggests".
4. Do NOT go the other direction and make the text mealy-mouthed. A real
   finding should still land as a real finding. Hedging everything is
   just as bad as overclaiming.
5. Preserve the author's voice and sentence structure where possible.
   Change only what needs to change for calibration.

After the rewrite, briefly list the specific changes you made and why.
```

## Why rule #4 matters so much

The most common failure of a naive "make it more calibrated" prompt is that it produces text where every finding is hedged into meaninglessness. A readout that says "we observed a potential directional trend consistent with a possible increase" is *worse* than the over-claim, because it's now impossible to make a decision from.

Explicitly telling Claude not to over-hedge is what keeps this useful.

## Example

**Before** (LLM-drafted readout text):

> The new onboarding flow caused a 3.2% increase in Day 1 activation, showing that simplifying the signup steps drives meaningful engagement. Users in the treatment group were significantly more likely to complete the tutorial, and the data shows this pattern holds across segments.

**After** (calibrated pass):

> The new onboarding flow was associated with a 3.2% relative increase in Day 1 activation (p = 0.02, 95% CI 0.7% to 5.7%). This is consistent with simplified signup steps improving early engagement, though the mechanism is indirect. Users in the treatment group were more likely to complete the tutorial (45% vs 39%, p < 0.01), and the direction of effect was similar across the three segments we examined — though the confidence intervals overlap, so we cannot conclude the effect is uniform.

Changes made:
- "Caused" → "was associated with" (A/B test gives us causal identification, but "caused a 3.2% increase" conflates point estimate with uncertainty; "associated with a 3.2% relative increase" + confidence interval is more honest)
- Added the CI and p-value for the primary result, which the draft implied but didn't state
- "Significantly more likely" kept, but added the numbers and p-value
- "The data shows this pattern holds across segments" → "the direction was similar... though the confidence intervals overlap" (the data does NOT show the pattern holds; it's consistent with the pattern holding)
- Preserved the structure and order of the original; no reorganization

---

## Why this works for product DS specifically

Product orgs reward confident-sounding analysis. PMs prefer "X caused Y" over "X is associated with Y". This creates a gravitational pull toward over-claim that individual DSs have to resist consciously.

Having a machine do the calibration pass removes the social awkwardness of hedging. You're not "being difficult" in a draft review — the LLM already did it, and you're just accepting the output.

## Failure mode

Claude sometimes downgrades language that should stay strong. Example: it'll change "we ran an A/B test and found a 10% lift" to "we observed an effect consistent with a 10% change" — that's over-calibrated. A properly-run, properly-powered A/B test with a significant primary effect *can* make causal claims.

**Mitigation:** the "briefly list the changes" requirement in the prompt. Skim the list and revert any over-hedging.

## When to skip

- Internal scratch notes that no one else will read.
- Text where you've already been rigorous about calibration (rare, but worth noting).
