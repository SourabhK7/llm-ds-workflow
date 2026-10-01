# Pattern 07: Exec TL;DR

You have a three-page analysis and an exec who needs three bullets. Shorten it the obvious way and the caveats that make the analysis believable are the first thing to go. This gets you a TL;DR that's actually short and still keeps the uncertainty that matters.

Give Claude the full analysis and tell it exactly which kind of caveat to keep.

## The prompt

```
Below is an analysis doc. Compress it to a 3-bullet executive TL;DR
following these rules.

ANALYSIS:
{paste the full analysis}

AUDIENCE:
{who is reading this (VP? Director? CEO?) and what decision are they
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
individual words ("potentially", "may suggest"). If something is uncertain,
the single-caveat bullet is where it goes, not sprinkled through the others.
```

## Why exactly one caveat

When you compress, caveats go first, because they're the longest sentences and the easiest to skip. But in DS work the caveats are often the whole point. A good TL;DR picks the one caveat that would change the decision.

Making Claude choose a single caveat, instead of listing "key caveats," is what makes this work. It's a useful test for you too. If you can't say which caveat matters most, you probably haven't finished thinking through the analysis.

## Why ask what it left out

That list is how you check its judgment. You skim it, and every so often it dropped something that actually mattered, so you swap it in. Without the list you'd have to reread the whole doc to check.

## Example

The analysis: a two-page doc on why pricing page conversion dropped 8% week over week.

Claude's TL;DR:
> - Conversion dropped 8% WoW on the pricing page, driven almost entirely by a drop in mobile Safari traffic converting at half their usual rate.
> - This coincides with a Safari browser update on April 8 that changed how our cookie consent banner renders; the effect looks like a bug, not a real demand shift.
> - Recommend: pause the week-over-week comparison until Eng confirms whether the banner bug is fixed; treat the drop as measurement artifact unless the pattern persists after fix.

What it left out, and why:
- "Small sample size in iOS Safari segment for the WoW comparison": left out because the pattern holds day by day within the segment, so sample size isn't the main worry.
- "Holiday week may affect baseline": left out because day of week was controlled for and the drop is specific to one browser and OS.
- "Pricing page A/B test launched same week": left out because the test was holdout-only and doesn't touch the measurement period.

I skimmed that, agreed with it, and sent the TL;DR.

## Where it goes wrong

- It sometimes drops the number, leaving "conversion dropped significantly" instead of "dropped 8%." Check that the headline has the magnitude.
- It sometimes softens the recommendation to "consider pausing" when the analysis supports "pause." If the doc backs a clear call, the TL;DR should make it.

## When not to bother

- You're the exec and you wrote it, so you already know what to emphasize.
- The analysis is under a page and there's nothing to compress.
