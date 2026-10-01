# Pattern 05: Calibrated language pass

Analysis text drafted by an LLM almost always claims too much. It says "caused," "drove" or "led to" when the data only supports "consistent with" or "associated with." That matters, because overstated readouts turn into bad product decisions.

It's also the best return on effort of anything in this repo. Thirty seconds on any analysis text removes a quiet problem that would otherwise carry into decks and decision docs.

Take the drafted text and have Claude rewrite the causal language to match what the method can actually support.

## The prompt

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

## Rule 4 is the important one

A plain "make this more careful" prompt tends to hedge every finding until it means nothing. "We observed a potential directional trend consistent with a possible increase" is worse than the overclaim, because nobody can make a decision from it. Telling Claude not to over-hedge is what keeps the pass useful.

## Example

Before (LLM-drafted readout text):

> The new onboarding flow caused a 3.2% increase in Day 1 activation, showing that simplifying the signup steps drives meaningful engagement. Users in the treatment group were significantly more likely to complete the tutorial, and the data shows this pattern holds across segments.

After the pass:

> The new onboarding flow was associated with a 3.2% relative increase in Day 1 activation (p = 0.02, 95% CI 0.7% to 5.7%). This is consistent with simplified signup steps improving early engagement, though the mechanism is indirect. Users in the treatment group were more likely to complete the tutorial (45% vs 39%, p < 0.01), and the direction of effect was similar across the three segments we examined, though the confidence intervals overlap, so we cannot conclude the effect is uniform.

What changed:
- "Caused" became "was associated with." An A/B test does support a causal reading, but "caused a 3.2% increase" treats the point estimate as certain. Giving the relative increase with its confidence interval is more accurate.
- Added the CI and p-value for the main result, which the draft implied but didn't state.
- Kept "more likely" for the tutorial, with the numbers and p-value added.
- "The data shows this pattern holds across segments" became "the direction was similar, though the confidence intervals overlap." The data is consistent with the pattern holding. It doesn't show it.
- Kept the original structure and order.

## Why this matters in product DS

Product orgs reward analysis that sounds confident. A PM would rather hear "X caused Y" than "X is associated with Y," so there's a constant pull toward overclaiming that you have to push back on deliberately.

Having the model do the pass also takes the awkwardness out of it. You're not being difficult in the doc review. The draft just comes back calibrated.

## Where it goes wrong

Sometimes it weakens language that should stay strong. It'll turn "we ran an A/B test and found a 10% lift" into "we observed an effect consistent with a 10% change," which is too cautious. A well-run, well-powered A/B test with a significant primary effect can make a causal claim.

That's why the prompt asks for a list of changes. Skim it and undo any over-hedging.

## When not to bother

- Scratch notes nobody else will read.
- Text you've already been careful with (rare, but it happens).
