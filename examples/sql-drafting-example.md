# Example: SQL drafting with patterns 01 + 03

Worked example of using the schema-anchored pattern to draft a query, then running the self-review pattern to catch issues before executing.

---

## The task

A PM asks: "How many of our new signups from the last month became weekly active users in their second week? Break it down by acquisition source."

A realistic ad-hoc request. Needs a new-cohort definition, a WAU definition, and a join to acquisition data.

---

## Step 1: Draft with pattern 01

Schema provided to Claude:

```
TABLE: prod_core.users
  user_id         STRING
  signup_date     DATE
  signup_source   STRING      -- values: 'organic', 'paid_search', 'paid_social',
                              --         'referral', 'direct', 'partnership'
  country_code    STRING

TABLE: prod_events.user_actions
  user_id           STRING
  action_name       STRING
  action_timestamp  TIMESTAMP
  partition_date    DATE        -- partitioned; always filter on this
```

Question: "Of users who signed up between 2026-03-01 and 2026-03-31, what fraction had at least one action during their second week (days 8–14 after signup), broken down by signup_source?"

Claude's draft:

```sql
WITH new_signups AS (
  SELECT
    user_id,
    signup_date,
    signup_source
  FROM prod_core.users
  WHERE signup_date BETWEEN '2026-03-01' AND '2026-03-31'
),
week2_actions AS (
  SELECT DISTINCT
    ua.user_id
  FROM prod_events.user_actions ua
  INNER JOIN new_signups ns
    ON ua.user_id = ns.user_id
  WHERE ua.partition_date BETWEEN DATE_ADD(ns.signup_date, 7)
                              AND DATE_ADD(ns.signup_date, 13)
    AND ua.action_timestamp >= ns.signup_date + INTERVAL 7 DAY
    AND ua.action_timestamp <  ns.signup_date + INTERVAL 14 DAY
)
SELECT
  ns.signup_source,
  COUNT(DISTINCT ns.user_id) AS new_signups,
  COUNT(DISTINCT w2.user_id) AS week2_active,
  COUNT(DISTINCT w2.user_id) * 1.0 / COUNT(DISTINCT ns.user_id) AS week2_activation_rate
FROM new_signups ns
LEFT JOIN week2_actions w2
  ON ns.user_id = w2.user_id
GROUP BY ns.signup_source
ORDER BY new_signups DESC;
```

Assumptions:
- "Second week" interpreted as days 8 through 14 after signup (signup_date + 7 through signup_date + 13, inclusive).
- A user counts as "week 2 active" if they have any row in `user_actions` in that window.
- Signups from March 2026 means signup_date between March 1 and March 31 inclusive.
- signup_source is populated for all users (no handling for NULL in the grouping).

Wished existed:
- A `is_internal_user` or bot flag to exclude test accounts.
- An `acquisition_campaign` granularity beyond source.

---

## Step 2: Self-review with pattern 03

Fed the draft back to Claude with the checklist prompt.

Claude's review:

> **1. JOIN fan-out: passes.**
> The `week2_actions` CTE uses `SELECT DISTINCT user_id`, so the LEFT JOIN at
> the end cannot fan out. The inner join within the CTE could produce multiple
> rows per user if a user has multiple actions in week 2, but the `DISTINCT`
> collapses them. Safe.
>
> **2. Window function partitioning: N/A.** No window functions.
>
> **3. Time window off-by-one: ⚠️ Issue found.**
> The original question asks for days 8 through 14 after signup (inclusive on
> both ends, per the prompt). The query uses
> `DATE_ADD(signup_date, 7)` through `DATE_ADD(signup_date, 13)` — which is
> day 8 (since day 1 = signup_date) through day 14 if we count signup_date
> as day 1. But `ua.action_timestamp < signup_date + INTERVAL 14 DAY` excludes
> actions on day 14 itself (the 14th day after signup).
>
> The behavior depends on whether "day 8–14" means:
> - Calendar-day based (day 1 = signup, day 8 = 7 calendar days later): the
>   current SQL is correct for this interpretation.
> - Hours-based (day 14 = up to signup_timestamp + 14 days): you're losing
>   actions in the final day.
>
> Likely fine — but flag for the person asking to confirm their definition.
>
> **4. NULL handling in filters: passes.** No non-equality filters on NULL-able columns.
>
> **5. COUNT vs COUNT(DISTINCT): passes.** Both sides use COUNT(DISTINCT user_id) which is correct for the rate calculation.
>
> **6. Aggregation level: passes.** Grouping by signup_source, counting users within group.
>
> **7. Partition filter on event tables: passes.** `partition_date` is filtered.
>
> **8. Deduplication: ⚠️ Noted but likely fine.**
> If `user_actions` has multiple rows per user per day (which it does), the
> `DISTINCT user_id` in `week2_actions` correctly collapses them. No issue.
>
> **Additional flag:** The query assumes `signup_date` is a pure DATE type.
> If it's actually a TIMESTAMP cast in schema, `signup_date + INTERVAL 7 DAY`
> behaves differently — it would give a timestamp exactly 7×24 hours later,
> which may not align with midnight on day 8. Worth confirming.

I confirmed with the PM that calendar-day interpretation was fine, and with the data catalog that `signup_date` is stored as DATE. Query shipped.

---

## What this saved

- Without the self-review, I probably would have caught the `< signup_date + 14 DAY` issue when I noticed the activation rate was slightly lower than expected — cost: one re-run + 20 minutes of head-scratching.
- The timestamp vs. date ambiguity I probably would have missed and shipped.

Total time: ~3 minutes for draft, ~90 seconds for review, ~2 minutes to verify the flagged concerns. ~7 minutes end-to-end for a query that would otherwise take 20.

The win isn't speed alone; it's also *caught errors I wouldn't have caught unprompted*.
