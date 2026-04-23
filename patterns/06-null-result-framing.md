# Pattern 06 — Null result framing

**Problem this solves:** Writing a readout for an experiment that didn't move the primary metric is the hardest writing task in product data science. It requires saying "we learned something valuable" without burying the fact that the hypothesis failed, and without spinning so hard you lose credibility. LLMs are genuinely useful here because they help you surface salvageable learnings without over-selling.

**The pattern:** Give Claude the null result plus any secondary findings, and ask it to draft three alternative framings that surface real value at three different levels of confidence.

---

## The prompt template

```
I ran an experiment. The primary metric did not move. I need to write a
readout that's honest about the null result but also surfaces any genuine
learnings.

PRIMARY RESULT:
{primary metric, CI, p-value}

WHAT I HOPED TO LEARN:
{the hypothesis / decision this was supposed to inform}

SECONDARY OBSERVATIONS (use these ONLY if they're real, not invented):
- {any guardrail movement, positive or negative}
- {any segment heterogeneity}
- {any qualitative signal from the test — user feedback, support tickets, etc.}
- {anything unexpected about the treatment experience itself}

Please draft three versions of the "What we learned" section at different
confidence levels:

VERSION A — Strict null: "We learned that the treatment did not move the
primary metric within the effect size we could detect. Here's what that
implies for the hypothesis."

VERSION B — Null with secondary learnings: above, plus any secondary
findings that are genuinely informative, with clear caveats that these
were not the primary question.

VERSION C — Null as course correction: above, plus an honest discussion of
what this result means for the team's model of the problem, and what to
try next.

Do not invent secondary findings. If I didn't give you any, version B and
C will be short. That's fine.

After the three versions, give me your opinion on which is most appropriate
for a readout going to a PM and design lead who cared about this experiment.
```

## Why three versions

Null results have a framing problem: the right level of narrative weight depends on *who is reading* and *what decision is pending*.

- Version A is right when the team just needs to know the number and move on.
- Version B is right when the secondary data is solid and the team wants to know if there are next steps.
- Version C is right when the null result is itself an update to the team's strategy — the hypothesis was load-bearing for a roadmap decision, and a null needs a real discussion.

Having Claude produce all three lets you pick the right register without having to write each one.

## The anti-pattern this fights

The most common failure mode in null-result readouts is **spinning secondary observations as if they were the primary result**. "The experiment didn't move activation, but users in the treatment group reported higher satisfaction in the follow-up survey (n=47)." This is not a finding, it's a cope.

The explicit "secondary observations" and "do not invent" rules in the prompt force honesty about what the secondary data actually is.

## Example

**Null primary result**: new pricing page copy, no change to trial-to-paid conversion (p = 0.68, CI on relative effect: -2.1% to +3.3%).

**Version A (Claude's draft)**:
> We tested whether rewriting the pricing page copy to emphasize annual savings would increase trial-to-paid conversion. It did not. The 95% confidence interval on the relative effect is -2.1% to +3.3%, which lets us rule out meaningful improvement (>3.3%) but does not rule out small effects in either direction. The hypothesis that copy emphasis is a meaningful driver of trial-to-paid conversion is not supported by this test.

**Version B (Claude's draft)**:
> *[version A, plus:]* Of the three sub-segments we examined, mobile users in Western Europe showed a directional positive effect (+2.8%, CI -1.4% to +7.2%). We did not pre-register this segment, so we are not treating this as a finding. If the team wants to pursue this, it would require a new test powered on that segment.

**Version C (Claude's draft)**:
> *[version B, plus:]* The null primary result updates our view of the copy-testing roadmap. We had prioritized three additional copy experiments behind this one under the implicit assumption that copy is a meaningful lever. This result doesn't rule out that assumption, but it does weaken it. Options: (a) deprioritize the remaining copy tests in favor of structural page changes; (b) run one more copy test with a sharper hypothesis; (c) pursue the mobile-EU directional signal with a properly-powered test. My recommendation is (b) + (c).

**Claude's opinion on which to use**: Version B for the PM/design audience, because they want to know if there's anything to pursue next but the null primary is the real headline. Version C would be appropriate if this were going to the product lead owning the pricing roadmap.

---

## Failure mode

Claude will sometimes sneak secondary observations back into version A ("strict null") even though you asked it not to. Skim and cut if needed.

## When to skip

- Genuinely uninformative nulls: underpowered tests, or tests with execution problems. For these, the right readout is "we can't conclude anything from this" — don't use this pattern to manufacture learnings that aren't there.
- Situations where the null is a straightforward negative and the team just needs to move on. Version A alone might be more than you need.
