# Pattern 13: Retention curve write-ups

You've computed retention curves (D1, D7, D30 by cohort, maybe split by acquisition source or plan). The numbers are right. Now you need to write them up so a PM or growth lead can act on them, without anyone reading a too-young cohort as "engagement is improving," and without losing people who can't read a retention chart.

Give Claude the retention numbers as a table (not a chart image, not your own summary) and ask for a write-up in a fixed order: the shape of the curve, then where cohorts differ, then what you'd check to explain it. Ask it to flag incomplete cohorts in the same sentence as the number, not in a footnote.

## Common problems with retention write-ups

Quoting D30 without D1. A cohort at 12% on D30 sounds fine until you see D1 was 15%. Retention that drops hard on day one and then flattens is a different product from retention that decays slowly, even if both end at 12%.

Comparing cohorts of different ages. "This month's users have 22% D30 retention," but the cohort is only 25 days old, so anyone who joined in the last 5 days can't have a D30 yet. The number is computed on the older half of the cohort, the half that already stuck around.

Describing the curve without saying anything. "Retention decreases over time" is true of every curve. The useful part is how it decreases, and where.

Left alone, Claude tends to write summary statistics in generic prose. Fixing the order is what gets you something useful.

## The prompt

```
I have retention data for a cohort or set of cohorts. Write a
summary a PM can act on.

Overall retention curve:
- D0 (baseline): {N users}
- D1: {retained N, rate %}
- D3: {retained N, rate %}
- D7: {retained N, rate %}
- D14: {retained N, rate %}
- D30: {retained N, rate %}

{If multiple cohorts:}
| Cohort | N | D1 | D3 | D7 | D14 | D30 |
|--------|---|----|----|----|-----|-----|
| ...    |   |    |    |    |     |     |

Cohorts without complete data at each day yet:
- {e.g., "cohort 2026-09 has partial D30 data as of the pull date"}

CONTEXT:
- Product surface: {app / web / feature name}
- What "retained" means here: {"any session", "a specific event",
  "reached activation step X"}
- Anything that changed recently: {launches, onboarding changes,
  marketing pushes}

Write it in this order:

1. The shape of the curve (2-3 sentences). How retention decays: a big
   D1 drop then flattening? Steady decay? A bend at a particular day?
   Use the actual numbers. Do not lead with D30.

2. Where cohorts differ (only if there are several). Which cohorts
   differ from the rest, at which day the difference shows up, and by
   how much. Don't compare cohorts at a day where any of them is
   incomplete. Say so instead.

3. What to check (2-4 sentences). A difference that shows up at D1
   points at onboarding or activation. One that only appears at D14+
   points at habits and engagement loops. One that opens at D7 and
   closes by D30 points at selection (weaker users left early). Say
   which this looks like.

4. Caveats inline, where they apply. If one cohort's D30 is based on
   60% of its users and another's on 100%, say it in the sentence
   that gives those numbers.

Aim for 200-350 words.
```

## Why this order

Starting with the shape gives the reader a picture right away, and it makes the writer actually look at the curve instead of quoting the endpoints. "Sharp drop on day one, then it flattens" and "steady decay" are different situations even at the same D30.

The "what to check" step is where the real analysis is. Anyone can read a table. Where the difference appears tells you a lot: early differences point at onboarding, late ones at engagement, and ones that open and then close point at selection. If the write-up doesn't say which of those it looks like, it's just a table in sentences.

## Example (illustrative)

Input (shortened):
- Overall: D1 41%, D3 32%, D7 27%, D14 22%, D30 18% (n = 42,000)
- Cohort 2026-08 (n = 18k, D30 complete): D1 39%, D7 26%, D30 17%
- Cohort 2026-09 (n = 24k, D30 partial; 60% of the cohort has a full 30-day window): D1 44%, D7 30%, D30 20%
- Context: a new onboarding flow launched to all new users at the start of September.

The kind of write-up this prompt is aiming for:

> **Shape.** The curve has a steep first-week drop: from 100% at signup to 41% at D1, then a shallower decline to 27% by D7. After D7 the decay is gradual: 22% at D14, 18% at D30. Most of the users who churn do so in the first three days; whoever is still active on D7 has about a 67% chance of being active at D30 (18 / 27).
>
> **Cohort divergence.** The September cohort shows a higher D1 rate (44% vs. August's 39%) and a higher D7 rate (30% vs. 26%). The D30 comparison is not clean. Only 60% of the September cohort has a full 30-day observation window as of this pull, so the 20% figure is measured on the older half of the cohort. We should not compare D30 across cohorts yet.
>
> **Mechanism to check.** The divergence appears at D1 and holds through D7. That points at the new onboarding flow (launched at the start of September) rather than at engagement loops that would show up later. Two checks to confirm: (a) restrict August and September cohorts to users past D14 only, and compare their D14 rates on the same footing; (b) if the launch was randomized, compare old vs. new onboarding within September directly. If it wasn't, treat the improvement as an unconfirmed correlation.
>
> The gap (~5pp at D1) is meaningful but not dramatic. Part of it could be composition if September's traffic came from different channels than August's. A per-source breakdown would separate the two.

## Where it goes wrong

If you paste the numbers as prose, Claude summarizes them back to you. Give it a table so the shape is visible.

It will come up with a cause on its own. If you don't say what changed, it'll still guess, usually something about onboarding. If nothing changed and the difference is just traffic mix, say that in the context.

It sometimes forgets the incomplete-cohort warning even when told. Check any sentence of the form "D30 for cohort X is Y%" and confirm X actually had complete D30 data.

## When not to bother

- One cohort, nothing to compare. A labeled chart beats prose.
- A chart in a deck that just needs a one-line caption.
- Early numbers. Don't write this up until at least D7 is complete for the cohorts you're comparing.

## Related patterns

- Pattern 04 (A/B readout skeleton): the same idea of structured input and a fixed section order.
- Pattern 05 (calibrated language): for the "what to check" section, where "consistent with the new onboarding" and "the new onboarding improved retention" are very different claims.
- Pattern 10 (metric sanity check): run it on the definition of "retained" first. "Any session" and "a meaningful action" can give very different curves.
