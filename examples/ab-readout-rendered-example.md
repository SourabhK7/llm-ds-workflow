Draft an A/B test readout using the structure below. Write in paragraphs, not
bullets. Be calibrated — do not claim causality beyond what the data supports.
Where the data is ambiguous, say so explicitly rather than smoothing it over.

EXPERIMENT METADATA:
- Name: onboarding_save_prompt_v2
- Hypothesis: Adding an optional 'save your progress' modal at step 3 of onboarding reduces abandonment and increases Day 1 activation.
- Audience: New web signups in US/CA/UK/AU, 50/50 split, ~24,800 users total
- Duration: 2026-06-02 to 2026-06-16 (14 days)
- Primary metric: Day 1 activation rate — fraction of new signups who complete a first meaningful in-app action within 24h of signup
- Guardrail metrics: Day 7 retention, support contact rate (first 7 days)
- Randomization unit: user_id (at signup)

RESULTS:
Primary metric:
- Control: 38.1% control (N=12,450) · 40.9% treatment (N=12,388), 95% CI on relative lift [2.4%, 12.3%]
- Treatment: 38.1% control (N=12,450) · 40.9% treatment (N=12,388), 95% CI on relative lift [2.4%, 12.3%]
- Relative lift: +7.3% relative
- p-value: 0.004
- Practical significance threshold: MDE = 3% relative lift

Guardrails:
- Day 7 retention: 24.1% control vs 24.8% treatment, p=0.31 (not significant): {result, direction, significance}
- Support contact rate: 4.2% control vs 4.5% treatment, p=0.48 (not significant): {result, direction, significance}

Segment breakdowns (if any):
- US +8.1% (p=0.008), UK +7.8% (p=0.03), CA +6.9% (p=0.19, underpowered), AU +4.2% (p=0.41, underpowered) — effect directionally positive in all four: see segment breakdown above

STRUCTURE:
1. TL;DR (2-3 sentences): the decision you're recommending and why.
2. What we tested and why: the hypothesis in plain language.
3. What we found: primary metric result, in calibrated language.
4. Guardrails: did anything move that shouldn't have?
5. Segments / heterogeneity: was the effect uniform or concentrated?
6. What this means: the business interpretation.
7. Caveats: what this readout cannot tell us. Be specific.
8. Recommendation: ship / don't ship / iterate, with reasoning.

Do not invent numbers. If a section has no data provided, write
"[placeholder: need to fill in]" rather than guessing.
