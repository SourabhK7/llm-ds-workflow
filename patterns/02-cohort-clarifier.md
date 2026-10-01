# Pattern 02: Cohort definition clarifier

Someone asks for "engaged users who churned" or "power users in the mobile app." It sounds clear in the meeting, but each phrase has at least three reasonable readings, and writing SQL for the wrong one costs you a day. This pattern gets the ambiguity out before you write any code.

Before any SQL, give Claude the request and ask it to list the possible definitions, say which choices would actually change the answer, and suggest a default.

## The prompt

```
A stakeholder asked me to analyze the following cohort:

"{the stakeholder's exact phrasing}"

Context: {product/surface, relevant time period, any known definitions your
team already uses}

Before I write any SQL, I want to pressure-test the definition.

Please:
1. List 3-5 plausible operational definitions of this cohort, with tradeoffs.
2. For each definition, estimate whether it would materially change the
   answer vs. the others (same order of magnitude? flipped direction?).
3. Flag any ambiguities I should clarify with the stakeholder before running
   the analysis.
4. Recommend a default definition and explain your reasoning, but be explicit
   that I should confirm with the stakeholder if the choice is consequential.
```

## Why it works

Claude doesn't know your product. What it's good at is listing cases, and it'll come up with four or five definitions you wouldn't have thought of yourself at 4pm on a Friday. It's a rubber duck that talks back.

The important part is asking whether each definition changes the answer. That separates the pedantic differences, which you can ignore, from the ones you need to take back to the stakeholder.

## Example

Request: "How many engaged mobile users did we lose last quarter?"

Claude's response (shortened):

| Definition of "engaged" | Definition of "lost" | Changes the answer? | Notes |
|---|---|---|---|
| Used app in 3+ of last 4 weeks | Didn't return in following 28 days | Yes | Strictest; gives smallest number |
| Used any core action ≥1 time in quarter | Didn't return in following 28 days | Yes | Much more inclusive; could be 5-10x larger |
| WAU in final week of quarter | Didn't return in following 14 days | Somewhat | Captures recent-cohort attrition |
| Paid plan users only | Subscription ended or downgraded | Yes | Mixes up product churn and billing churn |

Things to ask the stakeholder:
- "Mobile" meaning iOS, Android, or both? (Default: both.)
- "Lost" meaning gone for good (churn) or just hasn't come back yet (dormant)? Exec asks often mix these up.
- Calendar quarter or fiscal quarter?

Suggested default: the first definition, because "engaged" implies repeated use and "lost" implies a real absence. It gives the smallest number, though, so if the exec is expecting a big one they're probably thinking of the second. Worth a two-minute Slack check.

## Where it goes wrong

Claude doesn't know which definitions your team has already standardized. If there's an official "engaged user" definition in your data dictionary, it'll propose reasonable alternatives that conflict with it.

Paste your team's existing definitions into the context. Or ask directly whether any of these conflict with a definition you should know about. Claude will say it doesn't know your internal definitions, which is a good reminder to go check.

## When not to bother

- When the definition really is unambiguous ("how many users signed up in March?").
- When you've analyzed this exact cohort ten times and the definition is second nature.
