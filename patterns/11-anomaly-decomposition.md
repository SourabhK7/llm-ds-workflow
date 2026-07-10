# Pattern 11 — Anomaly decomposition

**Problem this solves:** A metric moved. A PM Slacks you at 9am: "Signups dropped 12% yesterday, what happened?" You have maybe 45 minutes before someone senior asks the same question. You don't want to spend 40 of those minutes reading dashboards in the wrong order.

**The pattern:** Before running a single query, describe the anomaly to Claude and ask it to produce a *ranked decomposition tree* — the sequence of splits you should investigate, starting with the ones most likely to explain the movement and cheapest to check. This turns a fuzzy "why did it drop?" into a checklist you can burn through.

The key move is enforcing an ordering discipline that most DS learn painfully over years: **rule out instrumentation before behavior, rule out composition before behavior, and rule out one-day effects before trend changes.** Skipping any of these steps is how DS embarrass themselves with a 200-word Slack thread that gets contradicted by a data engineer an hour later.

---

## The prompt template

```
A metric moved and I need to explain it. Before I start querying,
help me produce a ranked decomposition tree — the sequence of splits
I should investigate, ordered by (a) likelihood of explaining the
movement, and (b) cost to check.

THE MOVEMENT:
- Metric: {name and precise definition}
- Direction and magnitude: {"+12%" or "-3.4pp" — be precise about
  relative vs absolute}
- Time window: {e.g., "yesterday vs the trailing 7-day median" —
  and how confident I am the movement is real, not noise}
- Business surface: {which product, geo, platform, segment}

WHAT I ALREADY KNOW:
- {any relevant context: recent launches, external events, known
  incidents, prior anomalies in this metric}
- {segments I've already looked at, if any}

PRODUCE A DECOMPOSITION TREE, ORDERED:

Level 1 — Instrumentation checks (rule out before anything else):
  - Did the event schema, filter logic, or data pipeline change?
  - Is the data complete for the affected window (late-arriving data,
    partial partitions)?
  - Are we comparing like-for-like across the pre/post window
    (timezone boundaries, DST, weekday alignment)?

Level 2 — Composition shifts (rule out before behavioral explanations):
  - Did the mix of users, geos, platforms, or acquisition sources
    change? A behavior that looks new might just be the same behavior
    from a different-shaped population.

Level 3 — Real behavioral / product changes:
  - Only after 1 and 2 are ruled out, consider actual changes in
    user behavior, feature rollouts, pricing changes, marketing pulses.

Level 4 — External:
  - Holidays, competitor actions, macro events, outages upstream.

For each candidate: give me (a) the specific SQL-shaped question
I should ask, (b) what a "yes, this explains it" answer looks like,
and (c) roughly how expensive the check is (cheap = read a dashboard;
medium = write a 10-line query; expensive = need a new pipeline
or joined dataset).

Rank the checks so I do the cheapest high-likelihood ones first.
```

---

## Why the ordering matters

Every experienced product DS has a story about the time they wrote a beautiful narrative explaining why activation dropped 8%, only for someone to point out that the event pipeline had partial data because a Kafka topic partition was lagging. The narrative was Simpson's paradox-worthy prose about seasonal churn. The actual answer was "logging is broken, wait for the backfill."

Level 1 (instrumentation) catches this in 2 minutes.

Similarly: level 2 (composition) catches the "our Brazilian traffic doubled overnight because of a marketing push, and Brazil has lower activation, so the aggregate rate looks worse but nothing changed for individual users" scenario. This is one of the most common false alarms in product DS, and it's easier to check than most people realize (a simple pre/post user-mix diff).

By the time you're at level 3, you've earned the right to talk about actual behavior. But most people start there, then walk it back embarrassingly.

## Example

**Movement**: US-only signup rate on the marketing site dropped from a trailing-7-day median of 3.4% to 2.9% yesterday. That's a -14.7% relative drop, or -0.5pp absolute.

**What I know**: There was a marketing site redesign shipped two days ago (front-page hero replaced). No known outages. Traffic volume roughly flat.

**Claude's decomposition tree** (abbreviated):

> **Level 1 — Instrumentation (do these first, ~10 minutes total)**
>
> 1a. **Redesign event schema change** — cheap. When the hero changed, did the click event on the primary CTA change name, DOM selector, or tracking parameters? If yes, the "signup started" event you're counting might be missing a fraction of clicks. *Check*: compare event volume for the CTA event vs. server-side signup form loads. If server-side loads look normal but client-side clicks look low, it's instrumentation.
>
> 1b. **Late-arriving data** — cheap. What was the cutoff time for "yesterday" in your query? If it was midnight UTC but signups have a 3-hour delay pipeline for US traffic, you may be missing the last few hours of US signups. *Check*: rerun the query with the same window but at T+24 hours to see if the number changes.
>
> 1c. **Timezone comparison** — cheap. Is "yesterday" the same weekday-of-month as the days in your trailing-7-day median? If yesterday was a US federal holiday and none of the comparison days were, you're comparing a holiday to non-holidays.
>
> **Level 2 — Composition (~15 minutes)**
>
> 2a. **Traffic source mix** — medium. Did the mix of paid/organic/referral traffic shift? Paid traffic typically has different signup conversion than organic. If paid dropped and organic held, the aggregate rate would fall without any per-source behavior change. *Check*: compute signup rate per source_medium for the two windows. If per-source rates are flat but the mix shifted, it's composition, not behavior.
>
> 2b. **Device / platform mix** — medium. The redesign may have differentially affected mobile vs. desktop. If mobile suddenly dominates traffic and mobile has lower conversion, aggregate drops.
>
> **Level 3 — Behavioral / product (~30+ minutes, only if 1 and 2 clean)**
>
> 3a. **Redesign impact per source** — expensive. If per-source signup rates all dropped after the redesign shipped, that's a real behavioral effect from the redesign. Segment by acquisition source to see if the drop is broad or localized.
>
> 3b. **Funnel step diagnostics** — expensive. Where in the signup funnel do users drop? If they never reach the form (bounce rate up on landing), it's a landing-page problem. If they load the form but don't submit, it's a form problem.
>
> **Level 4 — External**
>
> 4a. **Competitor launch or news event** — cheap-ish. Any large competitor announcement yesterday? Any negative press about your product?

**What I actually found running this**: check 1b caught it. The pipeline had a 4-hour lag on yesterday's data. The corrected number was 3.3%, not 2.9%. The "anomaly" was 40 minutes of a real dip (probably noise) and 3+ hours of missing data.

Total investigation time: 12 minutes. Total time saved vs. the alternative universe where I wrote a redesign-critique memo before checking instrumentation: probably 90 minutes plus embarrassment.

---

## Failure modes

**Claude will suggest more checks than you need.** The value is the *ordering*, not the exhaustive list. Do the cheap high-likelihood ones and stop as soon as you have an explanation that fits the magnitude.

**Claude does not know your specific product's known issues.** If you have a chronically flaky event, Claude won't guess that. Feed known-issues context in the "WHAT I ALREADY KNOW" section — it'll incorporate it into the ranking.

**Watch for the "explanation exhaustion" trap.** After ruling out 4 things, there's a strong temptation to accept the 5th as the explanation just to stop looking. Discipline: does the magnitude of the candidate explanation actually match the magnitude of the anomaly? A composition shift that accounts for 0.05pp doesn't explain a 0.5pp drop.

## When to skip

- Anomalies inside noise. If yesterday's number is within the historical daily variance, don't investigate — you'll manufacture explanations for randomness. Compute a rough control chart before opening this pattern.
- Metrics that move for known reasons (post-launch spikes, planned pulses, expected seasonality).
- When the answer is already obvious. If eng shipped a broken deploy that reverted at 6pm, the tree is not necessary; the incident is the explanation.

## Related patterns

- Pattern 03 (SQL self-review) — apply to each query the tree generates, especially the level-1 instrumentation checks where a subtle join can invert the answer.
- Pattern 10 (metric interpretation) — use *before* declaring an anomaly. Sometimes the "movement" is just a definition mismatch across time.
- Pattern 08 (Slack-ready) — for the summary post you'll send once you find the answer. Format the explanation as: what moved, what caused it, what to do about it.
