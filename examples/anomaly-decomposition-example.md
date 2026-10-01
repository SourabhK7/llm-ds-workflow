# Example: anomaly decomposition with pattern 11

A worked example of pattern 11 on a realistic but made-up product anomaly: the prompt input, Claude's ranked list of checks, and the shortened path through it.

## The situation

A data scientist on a B2B activation team. Tuesday morning, 8:47am, a Slack from the PM:

> "Hey, is trial-to-paid conversion actually down? Dashboard says 6.1% last week vs. 7.8% the prior week. Kind of alarming if real. Can you dig in before standup at 10?"

That's 72 minutes. The dashboard does show what the PM quoted, and it's the standard weekly metric.

## Step 1: pin down what moved, before any SQL

Five minutes making sure of what actually changed:

- Metric: 14-day trial-to-paid conversion. Users who started a trial in the week and paid within 14 days of starting, divided by everyone who started a trial that week.
- Movement: 7.8% to 6.1%, about 22% down relative, or 1.7 points absolute.
- Windows: "last week" is Mon 2026-06-02 to Sun 2026-06-08, and "prior week" is Mon 2026-05-26 to Sun 2026-06-01.
- Is it real? 22% is far outside the usual week-to-week noise for this metric (standard deviation around 0.4 points). If it's real, it matters.

Just writing that down catches something. Last week ended Sunday June 8, three days ago, so the 14-day payment window hasn't closed for most of that week's trials. Someone who started a trial on June 8 has until June 22 to pay.

Note it and keep going.

## Step 2: the prompt, with real context

```
A metric moved and I need to explain it. Before I start querying,
help me produce a ranked decomposition tree: the sequence of splits
I should investigate, ordered by (a) likelihood of explaining the
movement, and (b) cost to check.

THE MOVEMENT:
- Metric: 14-day trial-to-paid conversion rate (paid within 14 days
  of trial start / all trial starts, weekly cohort)
- Direction and magnitude: 7.8% → 6.1%, -22% relative, -1.7pp absolute
- Time window: last week (Mon 6/2 to Sun 6/8) vs. prior week (Mon 5/26
  to Sun 6/1). Historical weekly stdev ≈ 0.4pp, so the movement is well
  outside typical noise.
- Business surface: B2B trial funnel, all geos, all plan tiers.

WHAT I ALREADY KNOW:
- The 14-day payment window has NOT fully closed for the reference
  week's cohort. Users who started a trial on 6/8 have until 6/22 to
  pay. This alone could explain a large fraction of the "drop."
- No known product launches in the trial or payment flow in the last
  three weeks.
- Marketing ran a paid pulse mid-May that ended 5/25.
- We had an alerting incident on 6/3 where the paid-conversion webhook
  from Stripe was delayed by ~2 hours (per platform-eng Slack).

Produce the tree.
```

## Step 3: Claude's list of checks

Shortened. Only the checks that got acted on are shown in full.

> **Level 1 — Instrumentation (do these first)**
>
> **1a. Right-censoring of the reference-week cohort.** The 14-day payment window is not closed for trials started on days 6/2 through 6/8. Users who started a trial on 6/8 have 14 days to pay, ending 6/22 — that's *12 days from now*. The reference-week numerator systematically excludes payments that haven't happened yet. This is the single largest candidate explanation and it's structural, not behavioral. *Check*: for each cohort day in both windows, restrict to trials whose full 14-day payment window has already closed. If both windows are limited to "trials that started at least 14 days ago", does the drop still exist? Cost: cheap, one query with a HAVING clause.
>
> **1b. Stripe webhook incident on 6/3.** A 2-hour webhook delay could cause paid conversions from 6/3 to be attributed to the wrong day, OR could cause some paid events to be dropped entirely if there was a retry failure. *Check*: verify Stripe payments for 6/3 in the source-of-truth Stripe dashboard match the count in the warehouse for that date. Cost: cheap, 5 minutes.
>
> **1c. Timezone / day boundary alignment.** Both windows are full calendar weeks so this is unlikely to be an issue, but confirm the cohort assignment logic uses the same timezone as prior weeks. *Check*: compare distinct trial_start_date values in both windows — if the counts per day look normal and symmetric, this is fine.
>
> **Level 2 — Composition shifts**
>
> **2a. Trial source mix.** The marketing pulse ended 5/25, so the prior week (5/26-6/1) may have a higher fraction of paid-acquired users still in the trial funnel from the tail of the pulse, while the reference week (6/2-6/8) is more organic-heavy. Paid trial converts differently than organic. *Check*: compute conversion rate per acquisition source for both windows. If per-source rates are stable but the mix shifted, this explains at least part of the drop.
>
> **2b. Plan tier mix.** If enterprise trials (higher conversion) became a smaller share of the reference week for some reason, the aggregate would drop even if per-tier rates held. Check the plan-tier distribution.
>
> **Level 3 — Behavioral / product**
>
> **3a. Real conversion behavior per source and tier.** Only after 1a-c and 2a-b are ruled out or accounted for. If per-source, per-tier conversion rates are actually lower in the reference week, then something real is happening.
>
> **Level 4 — External**
>
> **4a. Broader macro — end-of-quarter B2B budget dynamics.** June is end of Q2 for many B2B buyers, which can create both push (spend before quarter closes) and pull (delay to Q3). Directionally, this can go either way for trial-to-paid conversion. Low prior, hard to check.

## Step 4: what actually got checked

Following that order, three queries in the next 25 minutes.

First, check 1a, the payment window. Restricting both weeks to trials that started at least 14 days ago, so every payment window is closed:

- Prior week (5/26 to 6/1), fully closed: 7.9%. The original said 7.8%; the small change is late-arriving data, which is expected.
- Last week (6/2 to 6/8): only 6/2 has a closed window. 6/3 to 6/8 are still open.

So that restriction alone can't compare the two, since last week has almost no closed days. Instead, compare both weeks at the same age: what share had converted by day 5 after starting the trial?

- Prior week at day 5: 4.1%
- Last week at day 5: 4.0%

At the same age they're basically identical. Most of the "drop" is last week's trials not having had time to convert yet.

You could stop there, but the marketing tail was worth confirming.

Second, check 1b, the Stripe incident. Stripe shows 174 payments on 6/3, and the warehouse has 174. Fine.

Third, check 2a, the source mix. Paid-acquired share of trial starts was 34% the prior week and 21% last week. The tail of the mid-May campaign had been inflating the share of paid trials the week before. That mix change explains a small leftover part of the drop even after adjusting for trial age, and it's a return to normal, not a decline.

## Step 5: the reply

Posted at 9:33am, 46 minutes after the PM's message:

> Short answer: the drop isn't real. It's mostly last week's trials being too new, plus traffic mix going back to normal.
>
> The 14-day payment window hasn't closed for most of last week's trials. Comparing both weeks at the same age (day 5 after trial start), conversion is basically the same, 4.1% vs 4.0%.
>
> The rest is the mid-May paid campaign winding down. Paid trials went from 34% to 21% of starts week over week. Conversion within each source is stable.
>
> Stripe and the warehouse match for 6/3, so the webhook alert didn't lose anything.
>
> I wouldn't act on the raw weekly number. I'd like to add a closed-window version of this metric to the dashboard so maturity stops setting off false alarms, and I can build it this sprint. I'll reshare the 6/2 to 6/8 number in about 10 days once the window closes.

Total time: 46 minutes, about half of it framing and reading and about 20 minutes of SQL.

## What the pattern saved

The obvious path, "conversion is down, let me look at the funnel steps," would have burned an hour on behavioral analysis before anyone noticed the trial-age problem. That's exactly what pattern 11 is for: checking the structure before talking about behavior.

The prompt doesn't do the analysis. It just keeps the order straight. On a quiet afternoon you might remember to check trial age first anyway. At 8:47am with a PM waiting, having the order written down helps a lot.
