# Example: anomaly decomposition using pattern 11

A worked example of using pattern 11 on a realistic (but fabricated) product anomaly. Shows the full raw prompt input, Claude's ranked decomposition tree, and the abbreviated real-work path taken through it.

---

## The situation

A product DS on a B2B activation team. It's Tuesday morning. Slack from the PM at 8:47am:

> "Hey — is trial-to-paid conversion actually down? Dashboard says 6.1% last week vs. 7.8% the prior week. Kind of alarming if real. Can you dig in before standup at 10?"

72 minutes to answer. The dashboard shows the number the PM quoted. The metric is the standard weekly one.

---

## Step 1: Frame the movement precisely (before touching SQL)

Before running pattern 11, the DS spends 5 minutes making sure they understand what moved:

- **Metric**: 14-day trial-to-paid conversion rate, defined as: users who started a trial in the reference week AND paid within 14 days of trial start / all users who started a trial in the reference week.
- **Movement**: 7.8% → 6.1%, a relative drop of ~22%, or -1.7pp absolute.
- **Windows**: "Last week" = Mon 2026-06-02 through Sun 2026-06-08. "Prior week" = Mon 2026-05-26 through Sun 2026-06-01.
- **Confidence it's real**: 22% is well outside typical weekly variance for this metric (historical stdev ≈ ±0.4pp week-over-week). If real, the effect is meaningful, not noise.

This framing itself catches one thing: the reference week ended Sunday 2026-06-08 — which was **3 days ago**. The 14-day payment window hasn't fully closed for most of that cohort's users. Users who started a trial on Sunday June 8 have until June 22 to pay.

Flag this and continue.

---

## Step 2: Feed pattern 11 with real context

Raw prompt input to Claude:

```
A metric moved and I need to explain it. Before I start querying,
help me produce a ranked decomposition tree — the sequence of splits
I should investigate, ordered by (a) likelihood of explaining the
movement, and (b) cost to check.

THE MOVEMENT:
- Metric: 14-day trial-to-paid conversion rate (paid within 14 days
  of trial start / all trial starts, weekly cohort)
- Direction and magnitude: 7.8% → 6.1%, -22% relative, -1.7pp absolute
- Time window: last week (Mon 6/2 to Sun 6/8) vs. prior week (Mon 5/26
  to Sun 6/1). Historical weekly stdev ≈ 0.4pp — the movement is well
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

---

## Step 3: Claude's decomposition tree

Abbreviated. Only the checks the DS actually acted on are shown in full.

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

---

## Step 4: What the DS actually did

Following the ordering, the DS ran three queries in the next 25 minutes:

**Query 1 (check 1a) — right-censoring.**

Restricted both windows to only trials that started ≥14 days before today, so all payment windows are closed.

Result:
- Prior week (5/26 to 6/1), fully closed: **7.9%** (was 7.8% in the original — small revision from late-arriving data, expected).
- Reference week (6/2 to 6/8), only 6/2 has a fully closed window; 6/3-6/8 are partially open.

Cannot directly compare on this restriction alone — the reference-week cohort has almost no closed sub-cohorts. Instead: build a "days-since-trial-start" cumulative conversion curve. At day 5 post-trial-start, what fraction has converted?

- Prior week at day-5-since-trial: 4.1%
- Reference week at day-5-since-trial: 4.0%

**Essentially identical at the same maturity.** The apparent drop is dominated by the reference-week cohort being newer and not having had time to convert yet.

At this point the DS could stop, but continues one more check because the marketing-pulse effect is worth confirming for completeness.

**Query 2 (check 1b) — Stripe webhook incident.**

Payment counts from Stripe source-of-truth on 6/3 = 174. Warehouse count = 174. Fine.

**Query 3 (check 2a) — source mix.**

Paid-acquired share of trial starts:
- Prior week: 34%
- Reference week: 21%

Confirms the tail of the mid-May marketing pulse was inflating paid-acquired trial share the week before. The mix shift explains a small residual portion of the drop even after adjusting for maturity — but the mix shift is a *return to normal*, not a degradation.

---

## Step 5: The Slack reply

Post to the PM at 9:33am, 46 minutes after the original message:

> Short answer: **the drop is not real. It's mostly cohort maturity plus a return-to-normal in traffic mix.**
>
> Details:
>
> 1. **Cohort maturity dominates the apparent drop.** The 14-day payment window hasn't closed for most of last week's trials. When we compare cohorts at the same days-since-trial-start (e.g., day 5), conversion is essentially identical (4.1% vs. 4.0%).
>
> 2. **Marketing tail explains a small residual.** Paid-acquired share of trial starts fell from 34% to 21% week-over-week as the mid-May pulse fully wound down. This mix shift accounts for a small portion of the aggregate change. Per-source conversion rates are stable.
>
> 3. **Stripe/warehouse reconciliation is clean** for the 6/3 window despite the earlier webhook alert.
>
> Recommendation: don't act on the raw weekly number. Add a "closed-window only" version of this metric to the dashboard so we stop getting false alarms from cohort maturity. Happy to build it this sprint.
>
> Will reshare the 6/2-6/8 conversion number in ~10 days when the window closes.

Total time: 46 minutes. Half of it framing and reading. About 20 minutes of actual SQL.

---

## What this pattern saved

The naive path here — start with "conversion is down, let me look at funnel steps" — would have burned an hour on level-3 behavioral analysis before catching the level-1 cohort-maturity issue. That's exactly the failure mode pattern 11 exists to prevent: talking about behavior before ruling out structure.

The prompt itself doesn't do the analysis. It enforces the ordering discipline. In a low-adrenaline moment you might remember to check maturity first; at 8:47am with a PM waiting, the discipline is a lifesaver.
