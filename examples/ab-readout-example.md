# Example: A/B readout using patterns 04 + 05

A full worked example of drafting an experiment readout with the skeleton pattern (04) followed by the calibrated language pass (05).

---

## The situation

Imagine a product DS on a growth team. The team ran an experiment testing whether adding a "Save your progress" prompt during onboarding improves activation. The numbers are realistic but the details are fabricated — no real Adobe or other company data.

### Raw inputs to the prompt

```
EXPERIMENT METADATA:
- Name: onboarding_save_prompt_v1
- Hypothesis: Adding an optional "save your progress" modal at step 3 of
  onboarding will reduce the number of users who abandon setup and
  increase Day 1 activation (defined as completing a first meaningful
  action after sign-up).
- Audience: New web signups in US/CA/UK/AU. 50/50 split.
- Duration: March 3 to March 17, 2026 (14 days)
- Primary metric: Day 1 activation rate
- Guardrail metrics: Day 7 retention, support contact rate (first 7 days)
- Randomization unit: user_id (at signup)

RESULTS:
Primary metric (Day 1 activation):
- Control: 38.1%, N = 12,450
- Treatment: 40.9%, N = 12,388
- Relative lift: +7.3%
- p-value: 0.004
- 95% CI on relative lift: [2.4%, 12.3%]

Guardrails:
- Day 7 retention: 24.1% control vs 24.8% treatment, p = 0.31 (not significant)
- Support contact rate: 4.2% control vs 4.5% treatment, p = 0.48 (not significant)

Segments:
- US: +8.1% lift, p = 0.008
- CA: +6.9% lift, p = 0.19 (underpowered)
- UK: +7.8% lift, p = 0.03
- AU: +4.2% lift, p = 0.41 (underpowered)
```

---

## Step 1: Apply pattern 04 (skeleton)

**Claude's first draft** (abbreviated — showing the full structure):

### TL;DR
The "save your progress" onboarding prompt increased Day 1 activation by 7.3% (38.1% → 40.9%, p=0.004). Guardrails were clean. We recommend shipping to 100% of new web signups in the tested geographies.

### What we tested
Users in the treatment group saw a new modal at step 3 of signup offering to save their work-in-progress before continuing. Control users saw the existing flow. The hypothesis was that reducing perceived risk of losing setup work would push more users through to a first meaningful action.

### What we found
Day 1 activation improved from 38.1% in control to 40.9% in treatment — a relative lift of 7.3% (95% CI: 2.4% to 12.3%, p=0.004). This is consistent with a meaningful positive effect; the confidence interval rules out no-effect and very-large-effect alternatives.

### Guardrails
Neither guardrail moved significantly. Day 7 retention was slightly higher in treatment (24.8% vs 24.1%, p=0.31) but not enough to conclude a real effect. Support contact rate was similar across groups (4.5% vs 4.2%, p=0.48). We did not observe any early indicators that the modal is creating downstream friction or confusion.

### Segments / heterogeneity
The effect direction was positive in all four geographies. US and UK were individually significant (+8.1%, p=0.008; +7.8%, p=0.03). Canada and Australia were directionally positive but underpowered (+6.9%, p=0.19; +4.2%, p=0.41). The confidence intervals overlap considerably across geographies, so we cannot conclude the effect varies by geography.

### What this means
Signup friction is a real lever for activation. A simple modal — implemented in a sprint — produced a 7.3% relative lift on the primary activation metric. This is consistent with our team's broader thesis that early-funnel work-preservation signals reduce abandonment.

### Caveats
1. The test ran for 14 days, which captures a full weekly cycle but not monthly seasonality. If users behave differently on first-of-month cohorts, we haven't measured it.
2. Day 1 activation is a leading indicator. We do not yet have sufficient follow-up data to conclude this translates to longer-term engagement or monetization.
3. The modal is novel to users. Novelty effects sometimes decay. We recommend a follow-up measurement at 30 and 60 days post-launch to check for decay.
4. The treatment was tested in English-language geographies only. We should not assume the lift will hold in non-English markets without re-testing.

### Recommendation
**Ship** to 100% of new web signups in US/CA/UK/AU. Plan a 30-day and 60-day follow-up measurement to check for novelty effect decay. Before expanding to non-English markets, re-test with localized copy.

---

## Step 2: Apply pattern 05 (calibrated language pass)

Claude's calibration review identified three phrases to adjust:

1. **"increased Day 1 activation by 7.3%"** in the TL;DR — this is technically OK because it's a properly-run A/B test, but "associated with a 7.3% increase" is slightly more honest about the fact that the point estimate has uncertainty around it. The CI is already reported elsewhere, so either phrasing works. Kept the original; this is a well-powered experiment.

2. **"Signup friction is a real lever for activation"** in "What this means" — this is an overclaim. One experiment on one lever does not establish that friction broadly is a lever. Changed to: "This experiment is consistent with signup friction being a meaningful driver of activation, at least for the modal form of intervention we tested."

3. **"consistent with our team's broader thesis"** — retained, because "consistent with" is already calibrated language.

The final doc ships with those two changes. Total time: ~4 minutes for the first draft from Claude, ~2 minutes for the calibration pass, ~10 minutes for my own review and small edits. vs. ~75 minutes to write from scratch.

---

## What I edited in my own review (not done by Claude)

- Added a section at the bottom titled "Who was involved" crediting the eng team and the designer, which is org-specific social hygiene an LLM can't do for you.
- Changed the recommendation line to name the specific launch meeting (internal context).
- Added one sentence about what the team learned about the *process* of running this experiment (we scoped it too narrowly; the eng cost to expand was small).

These are the kinds of edits that stay human. The LLM handles the structure and language; the DS handles the judgment calls and the org-specific context.
