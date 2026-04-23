# Pattern 03 — SQL self-review

**Problem this solves:** LLM-generated SQL has a specific failure profile. It's usually syntactically fine and semantically close, but subtly wrong in ways you catch only by running it against real data — by which point you've already wasted a warehouse query. This pattern is a second-pass prompt that catches the specific errors LLMs make.

**The pattern:** After Claude writes a query, hand it back to Claude with a targeted checklist of "things LLMs get wrong in SQL" and ask for a review.

---

## The prompt template

```
Here is a SQL query I'm about to run on a production warehouse:

{paste query}

Context about the data:
- {table names and rough row counts}
- {anything unusual: partitioning, skew, known NULLs, duplicate events, etc.}

Please review this query specifically for these failure modes, which are
common in LLM-written SQL:

1. JOIN fan-out: does any join duplicate rows in a way that would inflate
   counts or sums?
2. Window function partitioning: if there are window functions, is the
   PARTITION BY clause complete? Common bug: forgetting to partition by
   user_id on user-level rankings.
3. Time window off-by-one: are BETWEEN clauses inclusive on both ends
   when you want them to be? Are you using [closed, open) consistently?
4. NULL handling in filters: does `WHERE col != 'x'` do what you intend
   when col can be NULL?
5. COUNT vs COUNT(DISTINCT): is the cardinality what I actually want?
6. Aggregation level: are you grouping at the right level? Common bug:
   summing a pre-aggregated metric across multiple rows.
7. Partition filter on event tables: is it there and correct?
8. Deduplication: if the source table has duplicate events (same user,
   same action, same timestamp), how are those being handled?

For each issue you find, describe it concretely and suggest a fix.
If a check passes, say so briefly — I want to see you considered it.
```

## Why the explicit checklist matters

Without the checklist, "review this SQL" gets you a generic "looks fine" from Claude, which is not useful. With the checklist, Claude actually applies each check and often catches things.

The checklist is specifically **the bugs LLMs produce**, not the bugs humans produce. Humans tend to make syntax errors (caught by the warehouse). LLMs tend to make subtly-wrong semantic choices that run fine and return plausible-looking numbers.

## The single highest-value item on the checklist

**Join fan-out.** This is the one I've been burned by the most. A query joins events to a dimension table, a user has multiple rows in the dim table (e.g., plan history), and suddenly your event counts are inflated 3x. The query runs. The numbers look wrong but not obviously wrong. You ship the readout.

Explicitly asking Claude to trace join fan-out catches this ~80% of the time in my experience.

## Example

Input query (abbreviated): a query counting daily active users joined to a `user_plans` table that has one row per plan change.

Claude's review response:

> **1. JOIN fan-out: ⚠️ Issue found.**
> The `LEFT JOIN` to `user_plans` on `user_id` will duplicate each DAU row
> once per plan change that user has ever had. If a user has 3 historical
> plan records, they'll be counted 3 times in the daily active count.
>
> Fix: join to a subquery that selects one plan per user, e.g., the plan
> active on the event date, using a range join or a LATERAL correlated
> subquery.
>
> **2. Window function partitioning: passes (no window functions present).**
>
> **3. Time window: passes (single-sided `>=` filter, no off-by-one risk).**
>
> **4. NULL handling: ⚠️ Minor.**
> `WHERE plan_tier != 'enterprise'` will exclude users whose plan_tier is
> NULL. If unmatched users should be included, use
> `WHERE plan_tier IS DISTINCT FROM 'enterprise'`.
> [...]

This review took 20 seconds. The join fan-out bug would have taken me 30 minutes to diagnose after I noticed the numbers looked inflated.

---

## Failure mode

Claude will occasionally flag a non-issue as an issue (false positive). Most common: it'll warn about NULL handling in a filter where NULLs are impossible (e.g., the column is NOT NULL). **Mitigation:** skim the review, don't blindly apply every suggestion. Ignore the ones that don't apply to your schema.

## When to skip

- Simple queries (single table, no joins, no windows). The checklist is overkill.
- Queries where you're prototyping and planning to iterate 5 times anyway — save the review for the final version.
