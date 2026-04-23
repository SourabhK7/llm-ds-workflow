# Example: Exec TL;DR using pattern 07

A 2-page analysis doc compressed into a 3-bullet exec summary. Shows what the pattern drops and preserves.

---

## The source analysis (abbreviated)

A DS investigation into why churn in the mid-market (team plan) segment spiked in February. The full doc is ~2 pages; here's the substance:

> Mid-market churn rose from a 12-month baseline of 3.8% monthly to 5.1% in February 2026, a 34% relative increase.
>
> Decomposition by cohort shows the spike is concentrated in customers who onboarded in Q3 2024 (18 months prior). This cohort was acquired during an aggressive paid-search campaign that emphasized a specific use case (annual report automation) which was subsequently de-emphasized in product roadmap.
>
> Within the Q3 2024 cohort, churn reasons from exit surveys (n=47) cluster around "product no longer fits our workflow" (62% of responses). Among customers who did not churn, NPS in this cohort dropped from 42 to 31 over the same 6-month window.
>
> Other cohorts (Q4 2024, Q1 2025, Q2 2025) saw no statistically significant churn change in February, and their NPS is stable.
>
> A regression controlling for plan tier, firmographics, and usage intensity suggests the Q3 2024 cohort effect persists after controls (p < 0.01).
>
> The February spike is consistent with a delayed product-market-fit breakdown for a specific acquisition campaign, not a broad product issue. However, we flag two alternative hypotheses that we cannot rule out:
>
> 1. Competitor X launched a feature directly targeting the annual-report-automation use case in late January. We do not have competitive intelligence on adoption.
>
> 2. A pricing change announced February 1 could be a proximate trigger. However, the Q3 2024 cohort did not receive different pricing treatment than other cohorts, so this does not explain why they specifically churned.
>
> Recommendation: the 2024-Q3 cohort was acquired against a use case we no longer prioritize. Option (a): re-engage the cohort with messaging aligned to current product strengths. Option (b): accept the churn and focus retention resources on cohorts with better fit. We recommend (b), framed as accepting the cost of a strategic product shift — but (a) is defensible if we have bandwidth.

---

## Claude's compressed TL;DR

> - February mid-market churn rose to 5.1% (from a 3.8% baseline), and the spike is almost entirely driven by customers we acquired in Q3 2024 against a use case we've since deprioritized in the product.
> - The single most important caveat: a competitor launched a feature directly targeting the affected use case in late January, which we cannot rule out as a contributing cause and do not have competitive-intelligence data to assess.
> - Recommendation: accept the Q3 2024 cohort churn as the cost of our product strategy shift, and focus retention resources on better-fit cohorts. Would like a 15-minute decision meeting this week to confirm before we stand down retention outreach on this segment.

## Caveats Claude filtered out

1. **Pricing change as alternative hypothesis** — filtered because the analysis already rules it out (Q3 cohort had no differential pricing exposure). Not load-bearing for the decision.

2. **Small-N on exit surveys (47 responses)** — filtered because the quantitative churn decomposition does not depend on the surveys; they are confirmatory color.

3. **Option (a): re-engagement campaign** — filtered because the recommendation is (b); if the exec disagrees and wants to pursue (a), they'll ask.

4. **Regression controls** — filtered because execs don't read regression caveats and the headline finding does not turn on the specific model choice.

5. **NPS decline from 42 to 31** — filtered because it's supporting evidence for the headline, not a separate finding the exec needs to act on.

---

## My review

I agreed with all filter choices except one: I added back a phrase about the regression ("the effect holds after controlling for plan tier and usage intensity") because I know this specific exec will ask "did you control for company size" and having it in the TL;DR heads off the question.

This is the kind of edit the LLM cannot make for you — it requires knowing the reader. The pattern saves you the 25 minutes of drafting; you still spend 5 minutes on audience-specific polish.

Total time: ~2 minutes for Claude's draft + ~5 minutes for my review = 7 minutes for a deliverable that would otherwise take 25-30.
