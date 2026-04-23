# Pattern 07 — Exec TL;DR compression

**Problem this solves:** You have a 3-page analysis doc. An exec needs a 3-bullet summary. Done naively, the summary drops the caveats that make the analysis credible. This pattern produces a TL;DR that is genuinely short *and* preserves the load-bearing uncertainty.

**The pattern:** Give Claude the full analysis and ask for a compressed summary with explicit instructions about which kinds of caveats to preserve vs. drop.

---

## The prompt template

```
Below is an analysis doc. Compress it to a 3-bullet executive TL;DR
following these rules.

ANALYSIS:
{paste the full analysis}

AUDIENCE:
{who is reading this — VP? Director? CEO? — and what decision are they
making from it}

RULES:

Bullet 1: The headline finding. One sentence. Must include the direction
and rough magnitude.

Bullet 2: The single most important caveat. This is the caveat that, if the
exec doesn't hear it, they will make a worse decision. Examples:
- "This is based on 2 weeks of data; we'd want another 2 weeks before
  acting on the full magnitude."
- "The effect is concentrated in enterprise users; SMB saw no change."
- "This was a quasi-experiment, not a randomized test."
Not every caveat in the full doc. The single one that matters most for
the decision at hand.

Bullet 3: What we recommend or what we need to decide.

After the TL;DR, list the caveats you chose NOT to include, and why. I
want to see what you filtered out so I can check your judgment.

Keep bullets to one sentence each. Do not use sub-bullets. Do not hedge
individual words ("potentially", "may suggest") — if something is uncertain,
the single-caveat bullet is where it goes, not sprinkled through the others.
```

## Why "the single most important caveat" is the key move

The default behavior of compression is to drop *all* caveats, because caveats are the longest and most skippable sentences. But the value of DS analysis *is* the caveats. The work of a good DS TL;DR is picking the one caveat that determines whether the decision changes.

Forcing Claude to pick exactly one caveat rather than list "key caveats" is what makes this pattern work. It's also a useful prompt for the DS — if you can't pick which caveat is most important, you probably haven't synthesized the analysis enough.

## Why the "caveats you filtered out" section matters

This is the audit trail. You skim it and occasionally find Claude filtered out something that actually was load-bearing. Then you swap it in. Without the audit list, you'd have to re-read the full doc to check.

## Example

**Full analysis**: a 2-page doc on why pricing page conversion dropped 8% week-over-week.

**Claude's TL;DR**:
> - Conversion dropped 8% WoW on the pricing page, driven almost entirely by a drop in mobile Safari traffic converting at half their usual rate.
> - This coincides with a Safari browser update on April 8 that changed how our cookie consent banner renders; the effect looks like a bug, not a real demand shift.
> - Recommend: pause the week-over-week comparison until Eng confirms whether the banner bug is fixed; treat the drop as measurement artifact unless the pattern persists after fix.

**Caveats filtered out, with reasoning**:
- "Small sample size in iOS Safari segment for the WoW comparison" — filtered because the pattern is consistent across days within the segment, so sample size isn't the main concern.
- "Holiday week may affect baseline" — filtered because we controlled for day-of-week and the drop is specific to a browser/OS cell.
- "Pricing page A/B test launched same week" — filtered because the test was holdout-only and doesn't affect the measurement period.

I skim that list, agree with the filtering, and ship the TL;DR.

---

## Failure modes

- **Claude sometimes compresses away the magnitude**, leaving you with "conversion dropped significantly" instead of "dropped 8%". Numbers matter; check that the headline has them.
- **Claude sometimes softens the recommendation.** "Consider pausing" instead of "pause". If the full analysis supports a clear recommendation, the TL;DR should carry it.

## When to skip

- Analyses where you're the exec and you wrote it; you already know what to emphasize.
- Analyses short enough that there's nothing to compress (< 1 page).
