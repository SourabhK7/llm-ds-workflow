# Pattern 15 — Exec Q&A prep

**Problem this solves:** You're about to share an analysis with an exec (a VP, a director, sometimes a founder). You've done the work. The readout is tight. What you don't have is a good sense of the 5-8 hardest questions that will land in the meeting, and you don't have prepared answers to them. Most DS wing this and it shows: the answer is either "I'd have to look into that" (which erodes trust) or a confident wrong answer (which erodes trust worse).

**The pattern:** Give Claude your readout (or the key findings) plus a one-line description of the exec's job function, and ask it to produce a ranked list of the questions this specific reader is likely to ask — plus a calibrated draft answer for each. Then edit the answers hard, because Claude's default answers are polished but often not honest enough.

The move that makes this work: **ask Claude to categorize each anticipated question by what it's really about** (methodology, business implication, scope, feasibility, follow-up work, or challenge to a claim). The question "how confident are you in this?" from a Head of Product means something different than the same words from a Head of Data. Categorization is what forces prep that isn't generic.

---

## Why this exists

The failure mode in a lot of DS-to-exec meetings isn't the analysis. It's that the analysis is 40 minutes of prepared thinking followed by 15 minutes of unprepared thinking under time pressure, and the second half is where the exec's memory of you is formed.

Two common shapes of this failure:

- **The methodology deep-dive.** Exec asks "did you control for X?" You say "we did, in the segmentation step". Exec asks "what happens if we don't control for X?". You don't know. You've spent 20 hours on the analysis and now 90 seconds of not-knowing is the takeaway.
- **The business implication punt.** Exec asks "so, ballpark, how much revenue is this worth?" You say "it depends on how many users we'd target and the assumed conversion lift". This is technically correct and functionally useless. The prepared version has three scenarios ready with the assumptions listed.

You don't need to have perfect answers to hard questions. You need to have *prepared* answers to hard questions. The gap between "I hadn't thought about that" and "here's the tradeoff, here's my read, here's what I'd want to test" is not intelligence — it's whether you did the prep work.

---

## The prompt template

```
I'm about to present the following analysis to {exec title} — {one
line on what this person does and what they care about}.

Meeting context: {e.g., "20-minute slot in a monthly business
review, decision I want out of it is X"}.

Here's the readout / findings:
{paste the full readout or a tight summary — headline, key
findings, recommendation}

Produce 6-8 questions this specific exec is likely to ask,
ranked from most to least likely. For each:

1. **The question**, in the exec's likely phrasing (not the
   sanitized academic version).

2. **What the question is really about** — pick one:
   - METHODOLOGY (did you compute this right?)
   - BUSINESS IMPLICATION (what does this mean for revenue /
     users / roadmap?)
   - SCOPE (is this the whole story or a slice?)
   - FEASIBILITY (can we act on this?)
   - FOLLOW-UP (what else should we investigate?)
   - CHALLENGE (I don't buy this — convince me)

3. **A calibrated draft answer** in 2-4 sentences. Rules for the
   draft:
   - If the honest answer is "I don't know", say so and then say
     what you'd need to check. Do not fabricate.
   - If the answer requires a number that isn't in the readout,
     flag it explicitly — that's a gap to close before the meeting.
   - Do not hedge every sentence. Hedging on the wrong things
     signals lack of confidence overall. Hedge specifically where
     the data is genuinely weak.
   - Do not oversell. If a finding has real limitations, name them
     in the answer, not as a footnote.

4. **The one-line follow-up you'd offer** if the exec presses (a
   commitment: "I'll come back with X by Y"). Only include this
   for questions where a follow-up is realistic.

At the end, produce a "**wildcard**" — one question that isn't in
the top 8 but that this specific exec is known to ask ("what does
finance think?" from a growth-oriented VP; "how does this compare
to what Amazon does?" from a competitive-obsessed founder). Even if
you're wrong about this one, thinking through it forces a broader
view.

Then produce a "**questions I hope they DON'T ask, and why**"
section. Two or three, honestly listed. These are the ones you
should actually prep hardest for — the fact that you hope they
skip them is a signal.
```

---

## Why the categorization step matters

Without the "what the question is really about" tagging, Claude will produce plausible-sounding answers that miss the actual concern. A METHODOLOGY question wants precision; a BUSINESS IMPLICATION question wants numbers and confidence; a CHALLENGE question wants you to hold your ground with evidence, not fold.

The category shapes the answer:

- **Methodology → be specific about the assumption or method, name the alternative, say why you picked yours.** "We used a 7-day attribution window. Alternatives are 1-day or 30-day. 7-day is standard for us because it matches marketing's reporting."
- **Business implication → give a range, name the key sensitivity, don't punt.** "Ballpark $200K-$400K in ARR. The main sensitivity is whether the conversion lift holds beyond the test population; the range covers a 50% attenuation to no attenuation."
- **Scope → say what's in and what's out, and offer to expand.** "This is US-only, web-only. Mobile is next. I did not include APAC because their funnel shape is different enough that pooling would obscure the story."
- **Feasibility → be blunt about engineering cost, dependencies, and the go/no-go signal.** "Yes, if we can get a data-eng half-week to build the pipeline. Without that, no."
- **Follow-up → commit to something specific and small.** "I'll run the same analysis on the mobile cohort by end of week and share a one-pager."
- **Challenge → do not fold. Restate the evidence, name the alternative interpretation, say why you find yours more likely.** "I understand the concern. The reason I think this isn't {alternative} is {specific piece of evidence}. That said, {the honest limit of my case}."

Without the tag, Claude's default is to answer everything as a mix of methodology and follow-up — which reads as vague and non-committal in an exec setting.

---

## Example

**Meeting**: 20-minute readout to the VP of Product on a piece of work showing that mobile users convert 15pp lower than desktop, concentrated at the payment step.

**Claude output (excerpt, top 3 of 8 questions)**:

> **Q1 (very likely) — "How much is this worth to fix?"**
> Category: BUSINESS IMPLICATION
> Draft answer: If we closed half the mobile-vs-desktop gap at the payment step, we'd add roughly 4pp to overall mobile checkout completion. On current mobile checkout volume (~120K/month), that's ~4,800 additional completed purchases per month. At the current mobile AOV of $52, that's ~$250K/month or ~$3M/year in incremental revenue. The main sensitivity is the assumption of "half the gap" — the real number depends on which specific friction we find and fix.
> Follow-up: "I'll rerun the sensitivity with 25% and 75% closure assumptions and send tomorrow."
> ⚠️ Gap to close before meeting: I need to verify the current mobile AOV number is fresh (the 52 figure is from Q2; check Q3 pull).
>
> **Q2 (very likely) — "Is it the payment method or the payment form?"**
> Category: METHODOLOGY / SCOPE
> Draft answer: The analysis doesn't distinguish those. What I know: the drop-off happens between "payment_info_entered" and "purchase_complete". That's after the user has picked a payment method and tapped through to submit, so it's more likely to be the submission step than the method-picker. But I haven't instrumented the sub-steps within payment_info yet — this would need a separate analysis to say definitively.
> Follow-up: "I can add sub-step instrumentation and rerun the analysis in ~1 week."
>
> **Q3 (likely) — "How confident are you that this isn't a mix issue?"**
> Category: CHALLENGE
> Draft answer: Pretty confident. I checked per-country and per-acquisition-source rates and the mobile-vs-desktop gap holds within each of those. So the 15pp isn't being driven by, e.g., cheaper mobile traffic from a specific market dragging the average down. What I can't rule out is a mix shift on some dimension I didn't segment on — I only had four attributes to work with. If you have a specific hypothesis (e.g., "is it the app vs. mweb split?"), I can check that specifically.
> Follow-up: none proactively; offer to check specific dimensions if the exec names one.
>
> [... Q4-Q8 omitted ...]
>
> **Wildcard**: "What does finance say about the projected $3M number?" This VP has been asking a lot about how DS numbers reconcile with finance's forecast recently. Prepared answer: I haven't run this by finance because the projection is a directional estimate for prioritization, not a booked-revenue commitment. Happy to loop them in before we scope the work.
>
> **Questions I hope they don't ask**:
> - "Why is the payment step 15pp worse on mobile? I'd expect it to be worse but not that much." (Because I don't have a good root cause, only the location of the drop-off. I'd need to answer this by pointing to next steps.)
> - "How does this compare to competitors?" (I don't have benchmarks. If pressed, I'll have to say so.)

---

## Failure modes

**Claude's draft answers are too polished.** Default Claude output reads like a management-consultant response — grammatical, calibrated, and slightly vacant. The prep is only useful if you edit the answers into something you'd actually say. "Pretty confident" beats "Highly confident, based on multi-dimensional segmentation analysis" in most rooms.

**The wildcard is often the most useful question.** Take it seriously. Reviewing your notes and thinking "what does the CFO think about this?" for 90 seconds routinely surfaces a real gap in the analysis.

**Prep for questions you don't want changes your work.** The most productive use of the "questions I hope they don't ask" section is not to memorize deflections. It's to notice that if you're hoping the exec doesn't ask "what's the counterfactual?", you should probably have a counterfactual before the meeting. Prep sometimes makes you redo the work — that's a feature, not a bug.

**Category tags leak in.** Delete "Category: BUSINESS IMPLICATION" from your printed prep. It's for framing your answer, not for the exec to see. This sounds obvious; DS have accidentally left it in.

**Wrong exec calibration.** Claude will produce different questions if you describe the exec as "Head of Growth" vs. "Head of Product" vs. "CFO" — and the questions differ a lot. If your one-line exec description is generic ("senior stakeholder"), the prep is generic. Give Claude something to work with.

## When to skip

- **Peer or team meetings.** Overkill; five minutes of thinking beats this workflow.
- **Rehearsal loops where you have a slide count constraint.** If you're prepping a 3-slide deck for a 5-minute check-in, the "8 questions" scaffold is too much.
- **Meetings where the exec has already seen the pre-read.** Different mode; the questions will be much more specific and less predictable. Handle those with the async response, not with prep.

## Related patterns

- Pattern 04 (A/B readout skeleton) — the readout you feed *into* this prep should be one you already ran through pattern 04 or 07.
- Pattern 05 (calibrated language) — apply to the draft answers before the meeting. Pattern 15 gives you the answers; pattern 5 tunes the confidence level.
- Pattern 09 (pre-mortem) — the "questions I hope they don't ask" section is a specific application of the pre-mortem idea, focused on the meeting rather than the analysis.
