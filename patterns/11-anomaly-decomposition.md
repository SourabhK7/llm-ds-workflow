# Pattern 11: Anomaly decomposition

A metric moved. A PM messages you at 9am: "Signups dropped 12% yesterday, what happened?" You have maybe 45 minutes before someone more senior asks the same thing, and you don't want to spend 40 of them clicking through dashboards in the wrong order.

Before running any query, describe the movement to Claude and ask for a ranked list of things to check, starting with the ones most likely to explain it and cheapest to look at. That turns a vague "why did it drop?" into a checklist.

The main thing it enforces is an order most data scientists learn the hard way: rule out instrumentation before behavior, rule out changes in the mix of users before behavior, and rule out one-day blips before calling it a trend. Skip a step and you end up writing a long Slack thread that a data engineer contradicts an hour later.

## The prompt

```
A metric moved and I need to explain it. Before I start querying,
help me produce a ranked decomposition tree: the sequence of splits
I should investigate, ordered by (a) likelihood of explaining the
movement, and (b) cost to check.

THE MOVEMENT:
- Metric: {name and precise definition}
- Direction and magnitude: {"+12%" or "-3.4pp", and be precise about
  relative vs absolute}
- Time window: {e.g., "yesterday vs the trailing 7-day median", and
  how confident I am the movement is real, not noise}
- Business surface: {which product, geo, platform, segment}

WHAT I ALREADY KNOW:
- {any relevant context: recent launches, external events, known
  incidents, prior anomalies in this metric}
- {segments I've already looked at, if any}

PRODUCE A DECOMPOSITION TREE, ORDERED:

Level 1, instrumentation checks (rule out before anything else):
  - Did the event schema, filter logic, or data pipeline change?
  - Is the data complete for the affected window (late-arriving data,
    partial partitions)?
  - Are we comparing like-for-like across the pre/post window
    (timezone boundaries, DST, weekday alignment)?

Level 2, composition shifts (rule out before behavioral explanations):
  - Did the mix of users, geos, platforms, or acquisition sources
    change? A behavior that looks new might just be the same behavior
    from a different-shaped population.

Level 3, real behavioral / product changes:
  - Only after 1 and 2 are ruled out, consider actual changes in
    user behavior, feature rollouts, pricing changes, marketing pulses.

Level 4, external:
  - Holidays, competitor actions, macro events, outages upstream.

For each candidate: give me (a) the specific SQL-shaped question
I should ask, (b) what a "yes, this explains it" answer looks like,
and (c) roughly how expensive the check is (cheap = read a dashboard;
medium = write a 10-line query; expensive = need a new pipeline
or joined dataset).

Rank the checks so I do the cheapest high-likelihood ones first.
```

## Why the order matters

A lot of data scientists have a story about writing a careful explanation for why activation dropped 8%, only to have someone point out that the event pipeline was missing data because one Kafka partition was lagging. The explanation was a thoughtful theory about seasonal churn. The real answer was "logging is broken, wait for the backfill." The level 1 checks catch that in two minutes.

Level 2 catches the "our Brazil traffic doubled overnight from a marketing push, Brazil converts lower, so the overall rate fell even though nothing changed for any individual user" situation. It's one of the most common false alarms in product analytics, and it's easier to check than people think: just compare the user mix before and after.

Once you're at level 3, you've earned the right to talk about behavior. Most people start there and then have to walk it back.

## Example

The movement: US signup rate on the marketing site went from a trailing 7-day median of 3.4% to 2.9% yesterday. That's -14.7% relative, or -0.5pp absolute.

What I know: the marketing site was redesigned two days ago (new front-page hero). No known outages. Traffic is roughly flat.

Claude's tree (shortened):

> **Level 1: Instrumentation (do these first, ~10 minutes total)**
>
> 1a. **Redesign event schema change** (cheap). When the hero changed, did the click event on the primary CTA change name, DOM selector, or tracking parameters? If yes, the "signup started" event you're counting might be missing a fraction of clicks. *Check*: compare event volume for the CTA event vs. server-side signup form loads. If server-side loads look normal but client-side clicks look low, it's instrumentation.
>
> 1b. **Late-arriving data** (cheap). What was the cutoff time for "yesterday" in your query? If it was midnight UTC but signups have a 3-hour delay pipeline for US traffic, you may be missing the last few hours of US signups. *Check*: rerun the query with the same window but at T+24 hours to see if the number changes.
>
> 1c. **Timezone comparison** (cheap). Is "yesterday" the same weekday-of-month as the days in your trailing-7-day median? If yesterday was a US federal holiday and none of the comparison days were, you're comparing a holiday to non-holidays.
>
> **Level 2: Composition (~15 minutes)**
>
> 2a. **Traffic source mix** (medium). Did the mix of paid/organic/referral traffic shift? Paid traffic typically has different signup conversion than organic. If paid dropped and organic held, the aggregate rate would fall without any per-source behavior change. *Check*: compute signup rate per source_medium for the two windows. If per-source rates are flat but the mix shifted, it's composition, not behavior.
>
> 2b. **Device / platform mix** (medium). The redesign may have affected mobile and desktop differently. If mobile suddenly dominates traffic and mobile has lower conversion, the aggregate drops.
>
> **Level 3: Behavioral / product (~30+ minutes, only if 1 and 2 are clean)**
>
> 3a. **Redesign impact per source** (expensive). If per-source signup rates all dropped after the redesign shipped, that's a real behavioral effect from the redesign. Segment by acquisition source to see if the drop is broad or localized.
>
> 3b. **Funnel step diagnostics** (expensive). Where in the signup funnel do users drop? If they never reach the form (bounce rate up on landing), it's a landing-page problem. If they load the form but don't submit, it's a form problem.
>
> **Level 4: External**
>
> 4a. **Competitor launch or news event** (fairly cheap). Any large competitor announcement yesterday? Any negative press about your product?

What it turned out to be: check 1b. The pipeline had a 4-hour lag on yesterday's data, and the corrected number was 3.3%, not 2.9%. The "anomaly" was about 40 minutes of a real dip, probably noise, plus three-plus hours of missing data.

That took 12 minutes. The alternative, writing up a critique of the redesign before checking the pipeline, would have taken an hour and a half and ended badly.

## Where it goes wrong

It suggests more checks than you need. The value is the order, not the full list. Do the cheap, likely ones and stop once you have an explanation that fits the size of the movement.

It doesn't know your product's known problems. If you have an event that breaks regularly, Claude can't guess that. Put it in the "what I already know" section and it'll factor it into the ranking.

Watch out for accepting the fifth explanation just because you're tired of ruling things out. Check whether the explanation is big enough. A mix shift worth 0.05pp doesn't explain a 0.5pp drop.

## When not to bother

- Movements within normal noise. If yesterday is inside the usual day-to-day range, don't investigate, or you'll invent explanations for randomness. Put together a rough control chart before you reach for this.
- Movements with known causes: post-launch spikes, planned campaigns, expected seasonality.
- When the answer is already obvious. If engineering shipped a broken deploy and rolled it back at 6pm, that's your explanation.

## Related patterns

- Pattern 03 (SQL self-review): use it on each query the tree suggests, especially the level 1 checks, where one bad join can flip the answer.
- Pattern 10 (metric sanity check): use it before calling something an anomaly. Sometimes the "movement" is just a definition that changed over time.
- Pattern 08 (Slack-ready): for the message you send once you know the answer. Say what moved, why, and what to do about it.
