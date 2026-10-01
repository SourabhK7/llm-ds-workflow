# Pattern 03: SQL self-review

SQL written by an LLM fails in a particular way. It's usually valid and close to right, but subtly wrong in ways you only notice after running it on real data, and by then you've already spent a warehouse query. This is a second pass aimed at those specific mistakes.

After Claude writes a query, give it back with a checklist of things LLMs commonly get wrong in SQL, and ask it to review against that list.

## The prompt

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
If a check passes, say so briefly. I want to see you considered it.
```

## Why the checklist

If you just say "review this SQL," you mostly get "looks fine." With the checklist, Claude actually goes through each item, and it often finds something.

The list is about the bugs LLMs make, not the ones people make. People tend to make syntax errors, and the warehouse catches those. LLMs tend to make wrong choices that still run and return numbers that look reasonable.

## The one that matters most

Join fan-out has burned me more than anything else on the list. You join events to a dimension table, some users have several rows in that table (plan history, say), and your event counts are suddenly three times too high. The query runs fine, the numbers look a bit off but not obviously wrong, and the readout goes out.

Asking Claude specifically to trace fan-out catches this about 80% of the time, in my experience.

## Example

The query (shortened): daily active users, joined to a `user_plans` table that has one row per plan change.

Claude's review:

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

The review took 20 seconds. Finding that fan-out bug myself, after noticing the numbers looked high, would have taken half an hour.

## Where it goes wrong

It sometimes flags things that aren't problems. The usual one is warning about NULLs in a filter on a column that can't be NULL. Skim the review and skip suggestions that don't apply to your schema instead of applying all of them.

## When not to bother

- Simple queries: one table, no joins, no window functions.
- When you're still prototyping and will rewrite it five more times. Review the final version.
