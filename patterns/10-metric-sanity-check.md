# Pattern 10: Metric sanity check

You've pulled a number from the warehouse. Before it goes in a readout or a Slack thread, you want a quick check that it means what you think, and that there isn't a definition mistake waiting to embarrass you when someone asks a follow-up question.

Describe the number, how you computed it, and what decision it feeds. Ask Claude for ways it could be technically right but misleading. This is about what the metric means, not the query. Pattern 03 covers SQL bugs; this covers interpretation bugs.

## The prompt

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

## How this differs from pattern 09

Pattern 09 is for before you run an analysis: what could go wrong with this approach? This one is for after you have a number: does this specific number mean what I think? I use the pre-mortem for analyses I design from scratch, and this for quick numbers I'm about to share.

## The mistake it catches most

A numerator that doesn't match the denominator is the interpretation error I see most in product DS work, and it's the hardest to spot rereading your own query.

Take "Day 7 retention is 42%." Sounds clear, but 42% of what? Users who signed up 7 days ago? Those who signed up 7 days ago and finished onboarding? Those active on Day 1? Each gives a different number, and the choice is usually buried in a WHERE clause that made sense when you wrote it and that nobody remembers when someone asks "42% of what?" at the end of the readout.

Writing out the numerator and denominator in the prompt forces you to say it plainly, which catches it before the stakeholder does.

## Example

The number: Day 30 retention, 18.3%.

How it was computed: users who signed up in January 2026 and did at least one thing in the app on Day 30 (±1 day), divided by all January 2026 signups.

The decision: whether to fund a retention push for new users.

Claude's check:

> **1. Numerator/denominator mismatch: ⚠️ Mild issue.**
> The denominator is all January signups. The numerator is users who were active
> on Day 30. But "Day 30 ±1 day" means you're measuring activity on day 29, 30,
> or 31 after signup. For users who signed up January 31, "Day 30" is March 2,
> which is in the future at time of writing. These users will have a 0% Day 30
> retention by construction, which deflates your rate. Either restrict to users
> who signed up on or before February 1 (so all of them have had 30 days pass),
> or note the caveat explicitly.
>
> **2. Time window asymmetry: passes** (same January 2026 cohort for both).
>
> **3. Definition drift: ⚠️ Note.**
> "Day 30 retention" is sometimes defined as "returned at any point in days
> 25 to 35" and sometimes as "returned on day 30 exactly." Your ±1 day window is
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
> not all signups, which would make their number look higher than yours
> even if the underlying product performance is identical.

That took 30 seconds. The January 31 problem would otherwise have shown up three days later as a confusing question from a PM.

## Where it goes wrong

It sometimes flags things that don't apply, like warning about direction on a metric where it's obvious (revenue, signups). Skim and use judgment. The value is in what it catches, not in acting on every line.

## When not to bother

- Numbers you've computed hundreds of times the same way. After the fiftieth DAU query you don't need this.
- Exploratory pulls just for you, while you're still working out what to measure.
