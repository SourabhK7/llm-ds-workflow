# Pattern 09 — Pre-mortem for analyses

**Problem this solves:** You're about to run a 4-hour analysis. Halfway through, you realize the query you should have written would answer a different question — or that your cohort definition has a confound you didn't see. This pattern is a pre-flight check that catches these problems before you start.

**The pattern:** Before running anything, describe the analysis you're about to do and have Claude imagine ways the conclusion could be misleading — not wrong (bugs), but correct-but-misleading (confounds, selection effects, Simpson's paradox).

---

## The prompt template

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

## Why this works better than "general rigor"

"Be rigorous" is not actionable. A pre-mortem forces *specific failure scenarios*, and specific failure scenarios are what you can design checks for.

The pattern is also useful for junior DS reports — it's a fast way to stress-test analysis plans without needing a senior DS reviewer. Not a substitute for review, but closes the gap on the obvious problems.

## Example

**Analysis**: "Does offering a 30% discount at trial day 10 improve trial-to-paid conversion?"

**Planned approach**: Compare conversion rate of users who received the discount email vs. users who didn't, among trial users who had been active on day 10.

**Claude's pre-mortem**:

1. **Selection bias in who received the email.** If the discount email was sent to users who had stopped using the product (a retention-oriented trigger), the treatment group is systematically less engaged than the control. The comparison measures engagement, not the discount's effect. **Check**: see who is actually targeted by the email rule; if it's "users who haven't logged in in 3 days", this is not a clean comparison.

2. **Temporal confound from the email itself.** Receiving *any* email at day 10 might reactivate users, independent of the discount offer. The discount's effect is confounded with the existence of the touchpoint. **Check**: is there a group that got a non-discount email at day 10 for comparison? If not, the estimate is "effect of discount + email" not "effect of discount".

3. **Self-selection into discount redemption.** Even within the treatment group, users who redeem the discount are different from users who receive it but don't redeem. If the analysis conditions on redemption, it's measuring the effect of being the kind of user who redeems, not the effect of the discount. **Check**: intent-to-treat analysis (all users who received the email), not per-protocol (only users who redeemed).

4. **Survivorship in the day-10 active population.** Both groups have already survived to day 10; this is fine, but the "trial-to-paid conversion rate" for these users will be higher than the overall rate. The lift estimate applies only to day-10-active users, not to the full trial cohort. **Check**: report the lift as "conversion among day-10-active trial users" explicitly; don't let the PM generalize it to all trial users.

5. **Simpson's paradox across plan tiers.** If the discount is mostly used by users intending to buy individual plans, and individual has lower baseline conversion than team, then an aggregate lift could reverse when split by plan tier. **Check**: segment the result by intended plan tier.

---

## What Claude is good at vs. bad at here

**Good at**: enumerating plausible confounds, because this is a pattern-recognition task and LLMs have seen a lot of analyses in training data.

**Bad at**: knowing whether any specific confound applies in your org. For example, Claude will often suggest "seasonality" as a concern even when the analysis window is 3 days long.

**Mitigation**: treat the output as a checklist of candidates, not a list of definite issues. Your job is to decide which ones are real in your context.

## The meta-benefit

Running this pattern before every non-trivial analysis (even for 2 minutes) changes how you think. You start anticipating the pre-mortem mentally and catching issues at the "scoping the SQL" stage, not the "reviewing the results" stage. The LLM is a scaffold for a habit, not a permanent crutch.

## When to skip

- Truly routine analyses (standard weekly WBR metric check).
- Analyses where the method is bulletproof and the question is unambiguous (rare).
- Time-boxed ad-hoc requests where the cost of running the analysis is lower than the cost of pre-mortem-ing it.
