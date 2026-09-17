# Pattern 13 — Retention curve narrative

**Problem this solves:** You've computed retention curves — D1, D7, D30 by cohort, maybe segmented by acquisition source or plan tier. The numbers are correct. But you need to write them up in a way a PM or growth lead can act on, without them either misreading a survivorship-biased curve as "our engagement is improving" or dismissing the whole thing because they can't parse a log-scale chart.

**The pattern:** Give Claude the retention numbers as structured data (never a chart image, never a paragraph you wrote) and ask for a narrative that (a) leads with the shape, not the number; (b) makes the cohort comparison explicit; and (c) flags survivorship bias inline, in prose, not as a caveat at the end that nobody reads.

The move that separates good retention writing from bad: **describe the curve, then the divergence, then the mechanism you'd need to check to explain the divergence.** In that order. Every other order buries the finding.

---

## Why this exists

Retention is the most-misread metric in product analytics. Three common failure modes in stakeholder writing:

1. **Quoting D30 without D1.** A cohort at 12% D30 sounds fine until you notice D1 is 15%. Retention that flattens fast after a huge day-1 drop is a different story than retention that decays smoothly. Both can end at 12%.
2. **Comparing cohorts of different ages.** "Users from this month have 22% D30 retention" — except the cohort is 25 days old, so anyone who signed up in the last 5 days can't have hit D30 yet. Your D30 is being computed on the older half of the cohort, which is the half that already retained. Survivorship pretending to be a trend.
3. **Flat prose describing a curve.** "Retention decreases over time" is not a finding. Every retention curve decreases over time. The finding is *how it decreases and where*.

Claude produces bad retention writing by default (it defaults to summary statistics and generic prose). Claude produces good retention writing if you force the structure — shape, divergence, mechanism.

---

## The prompt template

```
I have retention data for a cohort or set of cohorts. Write a
stakeholder-ready summary that a PM can act on.

STRUCTURED DATA:

Overall retention curve:
- D0 (baseline): {N users}
- D1: {retained N, rate %}
- D3: {retained N, rate %}
- D7: {retained N, rate %}
- D14: {retained N, rate %}
- D30: {retained N, rate %}

{If multiple cohorts, include a table:}
Cohort breakdown (retention rate at each day):
| Cohort | N | D1 | D3 | D7 | D14 | D30 |
|--------|---|----|----|----|-----|-----|
| ...    |   |    |    |    |     |     |

Cohort age warnings (which cohorts don't have complete data at
each day yet):
- {e.g., "cohort 2026-09 has partial D30 data as of the pull date"}

CONTEXT:
- What product surface: {app / web / feature name}
- What "retention" means here: {"any session", "a specific event",
  "reached activation step X"}
- What changed recently that might explain divergence: {launches,
  onboarding changes, marketing pulses}

Write in this order — do NOT reorder:

1. **The curve shape** (2-3 sentences). Describe how retention
   decays across days: is there a big D1 drop then flattening?
   Steady decay? A knee at a specific day? Use the actual numbers.
   Do NOT lead with the D30 number.

2. **The cohort divergence** (only if multiple cohorts). Name the
   cohorts that diverge from the average, at WHICH day the
   divergence appears, and by how much. Do not compare cohorts at
   days where any of them has incomplete data — call this out
   explicitly instead.

3. **The mechanism to check** (2-4 sentences). Given where the
   divergence appears in the curve, what would you test to explain
   it? Divergence at D1 points at onboarding or activation.
   Divergence appearing only at D14+ points at habit formation or
   engagement loops. Divergence at D7 that closes by D30 points at
   selection (weaker users churned early, survivors are similar).

4. **Survivorship / interpretation caveats** — inline, where
   relevant, not as a trailing list. If cohort A's D30 is computed
   on 60% of its intended users and cohort B's on 100%, say so in
   the sentence that quotes the numbers, not in a footer.

Length: aim for 200-350 words. This is a briefing, not a report.
```

---

## Why the order is non-negotiable

Every retention memo I've received that started with "Our D30 retention is X%" was followed by two paragraphs of context and a chart, and by the time I got to the important part I'd forgotten the number. Every retention memo I've received that started with "The curve has a sharp D1 drop from 100% to 41%, then flattens gradually to 22% by D14 and 18% by D30" gave me a *picture* in the first sentence.

Leading with the shape does two things:

- It forces the writer to actually look at the curve, not just quote endpoints.
- It gives the reader a mental model to hang everything else off. "Sharp D1 drop then flatten" and "smooth exponential decay" are different products, even at the same D30.

The mechanism section is where DS earn their keep. Anyone can read a table. Interpreting where divergence appears is the actual analysis, and it has surprising structure: **divergence early points at activation/onboarding, divergence late points at engagement loops, divergence that opens then closes points at selection**. If your narrative doesn't tell the reader which of these three shapes their divergence is, you've just published a table.

---

## Example

**Input** (abbreviated):

- Overall retention: D1 41%, D3 32%, D7 27%, D14 22%, D30 18% (n = 42,000)
- Cohort 2026-08 (n = 18k, D30 complete): D1 39%, D7 26%, D30 17%
- Cohort 2026-09 (n = 24k, D30 partial — 60% of cohort has full 30-day window): D1 44%, D7 30%, D30 20%
- Context: A new onboarding flow launched at the start of September for 100% of new users.

**Claude's output** (with the prompt):

> **Shape.** The curve has a steep first-week drop — from 100% at signup to 41% at D1 (a 59-point drop in one day), then a shallower decline to 27% by D7. After D7 the decay is gradual: 22% at D14, 18% at D30. Most of the users who churn do so in the first three days; whoever is still active on D7 has about a 67% chance of being active at D30 (18 / 27).
>
> **Cohort divergence.** The September cohort shows a higher D1 rate (44% vs. August's 39%) and a higher D7 rate (30% vs. 26%). The D30 comparison is not clean — only 60% of the September cohort has a full 30-day observation window as of this pull, so the 20% figure is measured on the older half of the cohort. We should not compare D30 across cohorts yet.
>
> **Mechanism to check.** The divergence appears at D1 and holds through D7. That points at the new onboarding flow (launched at the start of September) rather than at engagement loops that would show up later. Two checks to confirm: (a) restrict August and September cohorts to users past D14 only, and compare their D14 rates on the same footing; (b) A/B the old vs. new onboarding on the September cohort specifically, if the launch was randomized. If it wasn't randomized, treat the improvement as an unconfirmed correlation until we can hold something constant.
>
> The size of the gap (~5pp at D1) is meaningful but not dramatic. If the onboarding change is responsible for the full delta, that's a good result; if part of the delta is composition (September's traffic mix is different from August's, e.g., different acquisition channels), the onboarding-only lift is smaller. A per-acquisition-source cohort breakdown would separate these.

Word count: 291. PM can act on this in five minutes.

---

## Failure modes

**Claude will flatten the curve into a summary if you let it.** If you paste retention data as prose ("D1 was 41%, D7 was 27%..."), Claude will summarize back at you. Pass it as a table or a structured object; the shape has to be visible in the input.

**Claude will invent a mechanism.** If you don't provide context on what launched or changed, Claude will still speculate about causes. If nothing changed and the divergence is compositional, say so in the CONTEXT section — otherwise you get plausible but wrong prose about onboarding improvements when the truth is a marketing channel shift.

**Claude sometimes forgets the survivorship warning.** Even with the explicit instruction, if a cohort is partial, Claude may still compare D30 rates. Read the output for the specific claim "D30 for cohort X is Y%" and check whether X had full D30 data. This is the one place I re-read every retention output carefully.

**Watch for the "engagement is improving" over-claim.** A new cohort with a better D1 is either better onboarding, better traffic, or both. Claude will confidently attribute it to the launch even when the CONTEXT section only mentions the launch as one possible factor. Push back in edit.

## When to skip

- **Single cohort, no comparison needed.** If you're describing a curve without any divergence claim, a chart with axis labels is a better artifact than prose.
- **Retention as a chart in a deck.** If the chart is the deliverable and you just need one caption underneath, you don't need this pattern — you need one clear sentence.
- **Preliminary numbers.** Don't write a retention narrative until at least D7 is fully observed for the cohorts you're comparing. Anything earlier is noise-in-a-suit.

## Related patterns

- Pattern 04 (A/B readout skeleton) — the same "structured input + fixed section order" idea, applied to experiment readouts.
- Pattern 05 (calibrated language) — critical for the mechanism section; "consistent with the new onboarding" is different from "the new onboarding improved retention".
- Pattern 10 (metric interpretation sanity check) — run this on the retention definition itself before writing the narrative. Is "retained" defined as "any session"? "Any meaningful action"? The definition changes the numbers materially.
