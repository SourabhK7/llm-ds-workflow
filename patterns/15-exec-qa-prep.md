# Pattern 15: Exec Q&A prep

You're about to present an analysis to a VP, a director, or a founder. The readout is solid. What you don't have is a list of the six to eight hardest questions they'll ask, and answers ready for them. If you wing it, the answer tends to be either "I'd have to look into that," which costs you some trust, or a confident answer that turns out wrong, which costs you more.

Give Claude the readout and a one-line description of what the exec does, and ask for the questions they're most likely to ask, each with a draft answer. Then edit the answers hard, because the drafts tend to be polished but not quite honest enough.

The part that makes this work is having Claude tag what each question is really about. "How confident are you?" from a head of product means something different than the same words from a head of data.

## Why bother

The analysis is usually forty minutes of prepared thinking, followed by fifteen minutes of unprepared thinking under time pressure. The second part is often what people remember.

Two ways that goes badly:

The methodology question. "Did you control for X?" "Yes, in the segmentation." "What happens if you don't?" Silence. Twenty hours of work, and the takeaway is the ninety seconds where you didn't know.

The business question you punt. "Roughly how much revenue is this worth?" "It depends on how many users we target and what lift we assume." True, and no help to anyone. The prepared version has three scenarios with their assumptions written down.

You don't need perfect answers. You need prepared ones. The difference between "I hadn't thought about that" and "here's the tradeoff, here's my read, here's what I'd test" mostly comes down to prep.

## The prompt

```
I'm about to present the following analysis to {exec title}, {one line
on what this person does and what they care about}.

Meeting context: {e.g., "20-minute slot in a monthly business review;
the decision I want out of it is X"}.

The readout:
{paste the full readout or a tight summary: headline, key findings,
recommendation}

Give me the 6-8 questions this exec is most likely to ask, most likely
first. For each:

1. The question, the way this exec would actually phrase it.

2. What it's really about, one of:
   - METHODOLOGY (did you compute this right?)
   - BUSINESS IMPLICATION (what does this mean for revenue / users /
     roadmap?)
   - SCOPE (is this the whole story or a slice?)
   - FEASIBILITY (can we act on this?)
   - FOLLOW-UP (what else should we look at?)
   - CHALLENGE (I don't buy this, convince me)

3. A draft answer in 2-4 sentences:
   - If the honest answer is "I don't know," say so and what you'd
     need to check. Don't make things up.
   - If the answer needs a number that isn't in the readout, flag it.
     That's a gap to fill before the meeting.
   - Don't hedge every sentence. Hedge where the data is actually weak.
   - Don't oversell. Put real limitations in the answer, not in a
     footnote.

4. If the exec pushes, a one-line follow-up commitment ("I'll come back
   with X by Y"), only where that's realistic.

Then one "wildcard": a question outside the top 8 that this particular
exec might ask, given what they care about.

Then "questions I hope they don't ask, and why": two or three, honestly.
Those are the ones to prepare hardest for.
```

## Why the tags matter

Without the tag, Claude writes answers that sound fine and miss the actual concern. Each kind of question wants a different kind of answer:

- Methodology: name the specific assumption or method, the alternative, and why you picked yours. "We used a 7-day attribution window. 1-day and 30-day are the alternatives. We use 7 because it matches how marketing reports."
- Business implication: give a range, name the main sensitivity, and don't dodge. "Roughly $200K to $400K in ARR. The big unknown is whether the lift holds outside the test population. The range covers it holding at half strength through full strength."
- Scope: say what's in and what's out, and offer to extend it. "US web only. Mobile is next. I left out APAC because its funnel is different enough that combining them would muddy the result."
- Feasibility: be direct about cost and dependencies. "Yes, if we get half a week of data engineering time. Without that, no."
- Follow-up: commit to something small and specific. "I'll run the same cut for mobile by Friday and send a one-pager."
- Challenge: don't fold. Restate the evidence, name the other explanation, and say why you find yours more likely. "I get the concern. The reason I don't think it's {alternative} is {specific evidence}. The weak spot in my case is {honest limit}."

Untagged, the answers drift toward a mix of methodology and vague follow-up, which comes across as noncommittal in an exec meeting.

## Example (illustrative)

The meeting: a 20-minute readout to a VP of Product. The finding: mobile users convert 15 points lower than desktop, and the gap is concentrated at the payment step.

The kind of output to aim for, top three of eight:

> **Q1 (very likely): "How much is this worth to fix?"**
> Category: BUSINESS IMPLICATION
> Draft: If we closed half the mobile vs. desktop gap at payment, mobile checkout completion would go up about 4 points. At current mobile checkout volume (~120K a month) that's ~4,800 more completed purchases a month, and at a mobile AOV of $52, roughly $250K a month or $3M a year. The big assumption is "half the gap." The real number depends on which friction we find and fix.
> Follow-up: "I'll rerun it with 25% and 75% closure and send it tomorrow."
> Gap to close before the meeting: confirm the $52 AOV is current (it's from Q2).
>
> **Q2 (very likely): "Is it the payment method or the payment form?"**
> Category: METHODOLOGY / SCOPE
> Draft: This analysis can't tell. What I know is that the drop happens between "payment_info_entered" and "purchase_complete," which is after the user has picked a method and tapped submit, so the submit step is more likely than the method picker. I haven't instrumented the steps inside payment yet.
> Follow-up: "I can add sub-step tracking and rerun in about a week."
>
> **Q3 (likely): "How sure are you this isn't just a mix difference?"**
> Category: CHALLENGE
> Draft: Fairly sure. The mobile vs. desktop gap holds within each country and each acquisition source, so it isn't cheaper mobile traffic from one market pulling the average down. I can't rule out a difference on a dimension I didn't have, since I only had four. If you have one in mind, like app vs. mobile web, I can check it.
>
> **Wildcard:** "What does finance think of the $3M?" (if this VP has been asking how DS numbers line up with finance's forecast). Prepared answer: it's a directional estimate for prioritizing, not booked revenue, and I'm happy to bring finance in before we scope the work.
>
> **Questions I hope they don't ask:** "Why is it 15 points worse? I'd expect worse, but not that much." (I know where it happens, not why.) "How does this compare to competitors?" (No benchmarks. I'd have to say so.)

## Where it goes wrong

The draft answers are too polished. They read like a consultant wrote them: grammatical, careful, and a bit empty. Edit them into what you'd actually say. "Fairly sure" works better than "highly confident, based on multi-dimensional segmentation analysis" in most rooms.

Don't skip the wildcard. Spending ninety seconds on "what would the CFO think of this?" often turns up a real gap.

The questions you hope they don't ask can change the analysis. The point isn't to rehearse a deflection. If you're hoping nobody asks about the counterfactual, you probably need one before the meeting.

Take the category tags out of anything you print. They're for shaping your answer, not for the exec.

The exec description matters. Claude gives different questions for a head of growth, a head of product, and a CFO, and the differences are large. "Senior stakeholder" gets you generic prep.

## When not to bother

- Team or peer meetings. Five minutes of thinking is enough.
- A three-slide check-in. Eight questions is too much.
- Meetings where the exec already read the pre-read. Their questions will be more specific, so respond to those directly.

## Related patterns

- Pattern 04 (A/B readout skeleton) and pattern 07 (exec TL;DR): the readout you feed into this should already have been through one of those.
- Pattern 05 (calibrated language): run it on your draft answers before the meeting.
- Pattern 09 (pre-mortem): the "questions I hope they don't ask" section is a pre-mortem for the meeting instead of the analysis.
