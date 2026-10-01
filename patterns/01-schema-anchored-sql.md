# Pattern 01: Schema-anchored query drafting

You need SQL against a warehouse Claude has never seen. Left alone, it will confidently use column names that sound right (`user_id`, `event_timestamp`, `session_id`) but don't exist in your schema, and you lose a review cycle every time.

The fix: put the schema at the top of the prompt, tell Claude plainly what it doesn't know, and ask for the query plus a list of the assumptions it made.

## The prompt

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
3. Any columns or tables you wished existed but didn't, so I can check whether
   I forgot to include them in the schema above.

Keep the query readable: use CTEs rather than nested subqueries where it helps.
Always filter on partition_date when querying user_actions.
```

## Why each part is there

"ONLY tables and columns": without it, Claude fills gaps with plausible guesses. With it, the made-up columns mostly go away, at least in my experience.

The value lists on categorical columns (`'web', 'ios', 'android'`) stop it from filtering on `surface = 'mobile'` when that value doesn't exist.

The partition note: forgetting the partition filter is the most common performance mistake I see LLMs make on Databricks and Hive. Put it in the schema comment, not just in the question.

"Columns you wished existed" is the part people skip, and it's the most useful. It shows me gaps in the schema I didn't know about, and it catches the cases where Claude wanted to invent something but I told it not to.

## Example

Question: "How many weekly active users did we have in Q1, broken down by plan tier?"

Claude's response (shortened):

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
- "Weekly active" means any row in `user_actions` that week.
- Weeks start Monday (Databricks default for `DATE_TRUNC('week', ...)`).
- Q1 is Jan 1 to Mar 31.
- Users with no match in `prod_core.users` are still counted, with a NULL plan_tier.

Wished existed: a flag for bot/internal traffic, and a "primary plan tier" for users who changed tiers during the quarter.

## Where it's gone wrong for me

- Week start for date truncation differs by warehouse. Databricks starts weeks on Monday, BigQuery on Sunday by default, and Claude doesn't always get it right for other dialects. Name the dialect in the prompt if it matters.
- MAP and STRUCT access syntax differs too. Claude has used Snowflake syntax (`properties:key::string`) when I asked for Databricks (`properties['key']`). Putting an example access in the schema comments fixes it.
- It defaults to exact `COUNT(DISTINCT)`, which can be slow on big event tables. If that matters, add "use approx_count_distinct for cardinality estimates on user_actions."

## When not to bother

- One-line queries against tables you use every day. Just write them.
- Queries that already exist in your repo. Find and copy them instead of regenerating.
