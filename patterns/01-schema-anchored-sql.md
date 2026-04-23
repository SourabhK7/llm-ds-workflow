# Pattern 01 — Schema-anchored query drafting

**Problem this solves:** You need to write SQL against a warehouse Claude has never seen. Left to its own devices, it will confidently invent column names that sound right (`user_id`, `event_timestamp`, `session_id`) but don't exist in your schema. This wastes a review cycle every time.

**The pattern:** Pin the schema as structured context at the top of the prompt, explicitly tell Claude what it does *not* know, and ask for a query *plus* a list of assumptions it made.

---

## The prompt template

```
You are writing SQL for a Databricks warehouse. Here are the ONLY tables and
columns you can reference. Do not assume any other columns exist.

TABLE: prod_events.user_actions
  user_id           STRING
  action_name       STRING
  action_timestamp  TIMESTAMP
  surface           STRING       -- values: 'web', 'ios', 'android'
  properties        MAP<STRING, STRING>
  partition_date    DATE         -- partitioned; always filter on this

TABLE: prod_core.users
  user_id           STRING
  signup_date       DATE
  plan_tier         STRING       -- 'free', 'individual', 'team', 'enterprise'
  country_code      STRING

[...additional tables...]

QUESTION: {natural language question here}

Please produce:
1. A SQL query that answers the question.
2. A short list of assumptions you had to make (e.g., how you defined "active
   user", which time window you used, what you assumed about NULLs).
3. Any columns or tables you wished existed but didn't — so I can check whether
   I forgot to include them in the schema above.

Keep the query readable: use CTEs rather than nested subqueries where it helps.
Always filter on partition_date when querying user_actions.
```

## Why each piece matters

- **"ONLY tables and columns"** — without this, Claude will fill in gaps with plausible guesses. With it, hallucination rate drops sharply in my experience.
- **Value lists for categorical columns** (`'web', 'ios', 'android'`) — prevents Claude from filtering on `surface = 'mobile'` when that's not a real value.
- **Partition hint** — the #1 performance mistake LLMs make on Databricks/Hive is forgetting partition filters. Put it in the schema comment, not just in the natural language question.
- **"Columns you wished existed"** — this is the most underrated part of the prompt. It surfaces schema gaps I didn't know I had, and catches cases where Claude *wanted* to hallucinate but I told it not to.

## Example output

Input question: "How many weekly active users did we have in Q1, broken down by plan tier?"

Claude's response (abbreviated):

```sql
WITH weekly_active AS (
  SELECT
    DATE_TRUNC('week', action_timestamp) AS week_start,
    user_id
  FROM prod_events.user_actions
  WHERE partition_date BETWEEN '2025-01-01' AND '2025-03-31'
  GROUP BY 1, 2
)
SELECT
  wa.week_start,
  u.plan_tier,
  COUNT(DISTINCT wa.user_id) AS wau
FROM weekly_active wa
LEFT JOIN prod_core.users u ON wa.user_id = u.user_id
GROUP BY 1, 2
ORDER BY 1, 2;
```

Assumptions:
- "Weekly active" defined as any row in `user_actions` in a given week.
- Week starts Monday (Databricks default for `DATE_TRUNC('week', ...)`).
- Q1 = Jan 1 to Mar 31.
- Users with no match in `prod_core.users` are counted but have NULL plan_tier.

Wished existed: a flag for bot/internal traffic; a "primary plan tier" for users who changed tiers mid-quarter.

---

## Failure modes I've hit

- **Date-truncation week start** varies by warehouse. Databricks uses Monday; BigQuery default is Sunday. Claude doesn't always get this right for non-Databricks dialects. **Mitigation:** specify the dialect in the prompt if it matters.
- **MAP/STRUCT column access syntax** differs across warehouses. Claude sometimes uses Snowflake syntax (`properties:key::string`) when I asked for Databricks (`properties['key']`). **Mitigation:** include an example access in the schema comments.
- **COUNT(DISTINCT) vs approx** — Claude defaults to exact counts, which can be slow on large event tables. **Mitigation:** add "use approx_count_distinct for cardinality estimates on user_actions" to the prompt if relevant.

## When to skip this pattern

- One-liner queries against tables you use every day. Just write them.
- Highly-templated queries that already exist in your repo; fuzzy-find and copy, don't re-generate.
