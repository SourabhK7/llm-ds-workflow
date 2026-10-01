# Pattern 09: Pre-mortem for analyses

You're about to spend four hours on an analysis. Halfway through you realize the query you should have written answers a different question, or the cohort definition has a confound you didn't see. This is a quick check before you start that catches those problems early.

Before running anything, describe the analysis and have Claude imagine how the conclusion could mislead. Not wrong because of a bug, but correct and still misleading: confounds, selection effects, Simpson's paradox.

## The prompt

```
I'm about to run the following analysis. Before I start, please do a
pre-mortem: imagine the analysis has been completed, the number came out
exactly as I expected, I presented it to stakeholders, and they made a
decision based on it. Then imagine that six months later, the decision
turned out to be wrong.

What went wrong?

Be specific about failure modes involving:
- Confounds or selection effects that would bias the result
- Simpson's paradox (the aggregate answer conflicts with segment-level answers)
- Survivorship bias in the data
- Temporal confounds (seasonality, product launches, external events)
- Measurement issues (event logging gaps, definition changes, clock skew)
- The question being answered not matching the question being asked

THE ANALYSIS:
- Question being asked: {plain-English question from the stakeholder}
- Data I'll use: {tables, time period, filters}
- Method: {SQL aggregation? regression? matching? experiment analysis?}
- Expected outcome: {roughly what I think I'll find}

Give me 3-5 scenarios where this analysis produces a number that is
technically correct but misleads the decision. For each, suggest what
additional check or analysis would catch it.
```

## Why this beats "be rigorous"

"Be rigorous" isn't something you can act on. A pre-mortem gives you specific ways things could go wrong, and those you can actually write checks for.

It's also handy for junior folks on a team, as a fast way to stress-test a plan without waiting for a senior review. It doesn't replace the review, but it catches the obvious problems first.

## Example

The question: "Does offering a 30% discount at trial day 10 improve trial-to-paid conversion?"

The plan: compare conversion for users who got the discount email against users who didn't, among trial users who were active on day 10.

Claude's pre-mortem:

1. Selection bias in who got the email. If the email went to users who had stopped using the product (a retention trigger), the treatment group is less engaged to begin with, and you're measuring engagement, not the discount. Check: look at the email's targeting rule. If it's "hasn't logged in for 3 days," this isn't a clean comparison.

2. The email itself. Getting any email on day 10 might bring people back, discount or not, so the discount's effect is mixed up with the touchpoint. Check: is there a group that got a non-discount email on day 10? If not, you're measuring discount plus email, not the discount.

3. Who redeems. Even within the treatment group, people who redeem differ from people who get the email and ignore it. If the analysis only looks at redeemers, it measures being the kind of user who redeems. Check: use everyone who received the email (intent to treat), not only those who redeemed.

4. Survivorship in the day-10 population. Both groups already made it to day 10, which is fine, but their conversion rate will be higher than the full trial cohort's. The lift only applies to day-10-active users. Check: label it that way explicitly so nobody generalizes it to all trials.

5. Simpson's paradox across plan tiers. If the discount mostly gets used by people heading for individual plans, and individual converts lower than team, the overall lift could flip when you split by tier. Check: segment the result by intended plan tier.

## What it's good and bad at here

It's good at listing plausible confounds. That's pattern recognition, and it has seen a lot of analyses.

It's bad at knowing whether a given confound applies to you. It will bring up seasonality even when your window is three days long. Treat the list as candidates, not confirmed problems, and decide which ones are real in your situation.

## The side effect

Doing this before every non-trivial analysis, even for two minutes, changes how you think. You start running the pre-mortem in your head and catching things while you scope the SQL instead of while you review results. The prompt helps build the habit; you don't need it forever.

## When not to bother

- Routine checks, like a standard weekly metric review.
- When the method is airtight and the question is unambiguous (rare).
- Quick ad-hoc requests where running the analysis costs less than pre-morteming it.
