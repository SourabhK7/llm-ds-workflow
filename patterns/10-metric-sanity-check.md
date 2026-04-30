# Pattern 10 — Metric interpretation sanity check

**Problem this solves:** You've pulled a number from the warehouse. Before you put it in a readout or share it in Slack, you want a fast check that the number actually means what you think it means — that you haven't made a subtle definitional error that will embarrass you when a stakeholder asks a follow-up question.

**The pattern:** Describe the number you computed, how you computed it, and what decision it's meant to inform. Ask Claude to surface ways the number could be technically correct but misleading — specifically around metric definition, not around the query itself (pattern 03 covers SQL bugs; this covers interpretation bugs).

---

## The prompt template

```
I computed the following metric and I'm about to share it with a stakeholder.
Before I do, I want a fast sanity check on whether the number means what
I think it means.

THE NUMBER:
{metric name}: {value}

HOW I COMPUTED IT:
{describe the numerator and denominator, the time window, the cohort
filter, and any edge cases you handled or ignored}

WHAT DECISION THIS IS MEANT TO INFORM:
{what the stakeholder will do differently based on this number}

Please check for:
1. Numerator/denominator mismatch: is the population in the numerator
   a subset of the population in the denominator? If not, the rate is
   meaningless.
2. Time window asymmetry: if the numerator and denominator are measured
   over different time windows, does that distort the result?
3. Definition drift: does this metric definition match how this metric
   is typically defined in the industry or at most companies? If it
   differs from convention, will the stakeholder assume the conventional
   definition and misread the number?
4. Survivorship / selection: is the population you're measuring a
   survivor cohort that systematically excludes a group relevant to
   the decision?
5. Directionality: is it clear whether higher is better or lower is
   better for this metric? Could the stakeholder read the direction
   wrong?
6. Comparison validity: if this number will be compared to a benchmark
   or a prior period, are the definitions comparable?

For each check: if it passes, say so briefly. If there's an issue,
describe it concretely and suggest how to fix or caveat it.
```

## Why this pattern exists separately from pattern 09 (pre-mortem)

Pattern 09 is for before you run the analysis. This pattern is for after you have a number. The pre-mortem asks "what could go wrong with this analysis approach?" This pattern asks "does this specific number mean what I think it means?"

In practice: pre-mortem for analyses you design from scratch; this pattern for ad-hoc numbers you computed quickly and are about to share.

## The single failure mode this catches most reliably

**Numerator/denominator mismatch** is the metric interpretation error I've seen most in product DS work, and it's the one that's hardest to catch by re-reading your own query.

Classic example: "Day 7 retention is 42%." Sounds clear. But what's the denominator? Users who signed up 7 days ago? Users who signed up 7 days ago AND completed onboarding? Users who were active on Day 1? Each gives a different number, and the denominator choice is often implicit — buried in a WHERE clause that made sense at query-time but that no one will remember when someone asks "42% of what?" at the end of your readout.

Explicitly describing numerator and denominator in the prompt forces you to articulate it, which catches the error before the stakeholder asks.

## Example

**The number:** Day 30 retention, 18.3%.

**How computed:** Users who signed up in January 2026 and had at least one action in the app on Day 30 (±1 day window), divided by all users who signed up in January 2026.

**Decision:** Whether to invest in a retention improvement initiative for new users.

**Claude's check:**

> **1. Numerator/denominator mismatch: ⚠️ Mild issue.**
> The denominator is all January signups. The numerator is users who were active
> on Day 30. But "Day 30 ±1 day" means you're measuring activity on day 29, 30,
> or 31 after signup. For users who signed up January 31, "Day 30" is March 2
> — which is in the future at time of writing. These users will have a 0% Day 30
> retention by construction, which deflates your rate. Either restrict to users
> who signed up on or before February 1 (so all of them have had 30 days pass),
> or note the caveat explicitly.
>
> **2. Time window asymmetry: passes** (same January 2026 cohort for both).
>
> **3. Definition drift: ⚠️ Note.**
> "Day 30 retention" is sometimes defined as "returned at any point in days
> 25–35" and sometimes as "returned on day 30 exactly." Your ±1 day window is
> close to convention but worth flagging in the readout if the stakeholder
> is comparing to industry benchmarks that may use a stricter definition.
>
> **4. Survivorship: passes** for this specific question (all signups included).
>
> **5. Directionality: passes** (higher is clearly better for retention).
>
> **6. Comparison validity: flagged.**
> If you compare this 18.3% to last month's retention or to an industry
> benchmark, confirm the denominator definition matches. Many published
> retention benchmarks use "Day 1 activated users" as the denominator,
> not all signups — which would make their number look higher than yours
> even if the underlying product performance is identical.

This review takes 30 seconds. The January 31 cohort issue would have surfaced as a confusing follow-up question from a PM three days later.

---

## Failure mode

Claude occasionally flags issues that aren't real for your specific context — for instance, it'll often warn about directionality for a metric that's obviously directional (revenue, signups). Skim and apply judgment. The value is in the checks it catches, not in implementing every suggestion.

## When to skip

- Numbers you've computed hundreds of times with the same definition. After 50 DAU queries, you don't need a sanity check.
- Exploratory / for-your-eyes-only pulls where you're still figuring out what to measure.
