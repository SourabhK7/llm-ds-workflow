# Pattern 02 — Cohort definition clarifier

**Problem this solves:** A stakeholder asks for "engaged users who churned" or "power users in the mobile app." These phrases feel clear in a meeting but have at least three defensible interpretations each. Writing SQL against the wrong interpretation wastes a day. The goal of this pattern is to surface the ambiguity *before* you write any code.

**The pattern:** Before any SQL, feed the request to Claude and ask it to enumerate possible operational definitions, flag which choices would meaningfully change the result, and recommend a default.

---

## The prompt template

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
4. Recommend a default definition and explain your reasoning — but be explicit
   that I should confirm with the stakeholder if the choice is consequential.
```

## Why this works

This is not about Claude "knowing" your product — it doesn't. It's about Claude being a rubber duck that's better at enumerating cases than you are at 4pm on a Friday. The LLM is genuinely good at producing 4-5 alternative definitions you wouldn't have thought of yourself.

The key move is forcing the "does it change the answer" column. This separates pedantic distinctions (doesn't matter) from consequential ones (go back to the stakeholder).

## Example

Input: "How many engaged mobile users did we lose last quarter?"

Claude's response (abbreviated):

| Definition of "engaged" | Definition of "lost" | Material? | Notes |
|---|---|---|---|
| Used app in 3+ of last 4 weeks | Didn't return in following 28 days | Yes | Strictest; gives smallest number |
| Used any core action ≥1 time in quarter | Didn't return in following 28 days | Yes | Much more inclusive; could be 5-10x larger |
| WAU in final week of quarter | Didn't return in following 14 days | Medium | Captures recent-cohort attrition |
| Paid plan users only | Subscription ended or downgraded | Yes | Conflates product churn with monetization churn |

**Ambiguities worth raising with the stakeholder:**
- "Mobile" — iOS only, Android only, or both? (Default: both.)
- "Lost" — are they asking about churn (gone for good) or dormancy (haven't returned yet)? These are often conflated in exec asks.
- Time boundary: calendar quarter or fiscal quarter?

**Recommended default:** Definition 1, because "engaged" implies repeated use and "lost" implies a meaningful absence. But this gives the smallest possible number, so if the exec expects a big number they may be thinking of definition 2. **Worth a 2-minute Slack check.**

---

## Failure mode

Claude is not great at knowing which definitions your team has *already standardized on*. If your org has a canonical "engaged user" definition in a data dictionary, Claude doesn't know it. It will propose reasonable alternatives that conflict with your internal standard.

**Mitigation:** paste the team's existing definitions into the context block. Or explicitly ask "does any of these conflict with a definition I should be aware of?" — Claude will say "I don't know your internal definitions" which is a useful prompt for you to go check.

## When to skip

- Requests where the definition is genuinely unambiguous ("how many users signed up in March?").
- Requests where you've already analyzed this exact cohort 10 times; the operational definition is reflex at that point.
