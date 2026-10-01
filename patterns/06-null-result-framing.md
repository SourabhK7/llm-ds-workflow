# Pattern 06: Null result framing

Writing up a test that didn't move the primary metric is the hardest writing in product data science. You have to say you learned something useful without hiding that the hypothesis failed, and without spinning it so hard you lose credibility. LLMs help a lot here, because they're good at pulling out what's actually salvageable without overselling it.

Give Claude the null result and any secondary observations, and ask for three versions of the "what we learned" section at three levels of confidence.

## The prompt

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
- {any qualitative signal from the test: user feedback, support tickets, etc.}
- {anything unexpected about the treatment experience itself}

Please draft three versions of the "What we learned" section at different
confidence levels:

VERSION A (strict null): "We learned that the treatment did not move the
primary metric within the effect size we could detect. Here's what that
implies for the hypothesis."

VERSION B (null with secondary learnings): above, plus any secondary
findings that are genuinely informative, with clear caveats that these
were not the primary question.

VERSION C (null as course correction): above, plus an honest discussion of
what this result means for the team's model of the problem, and what to
try next.

Do not invent secondary findings. If I didn't give you any, version B and
C will be short. That's fine.

After the three versions, give me your opinion on which is most appropriate
for a readout going to a PM and design lead who cared about this experiment.
```

## Why three versions

How much weight to give a null result depends on who's reading and what decision is waiting on it.

Version A fits when the team just needs the number so they can move on. Version B fits when the secondary data is solid and people want to know whether there's a next step. Version C fits when the null actually changes the team's plans, because the hypothesis was holding up a roadmap decision and needs a real discussion.

Getting all three means you can pick the right one without writing each yourself.

## The mistake it guards against

The most common problem in null-result readouts is presenting a secondary observation as if it were the result. "The experiment didn't move activation, but users in the treatment group reported higher satisfaction in the follow-up survey (n=47)." That isn't a finding. It's a consolation prize.

The separate secondary-observations block and the "do not invent" rule make you be honest about what that secondary data really is.

## Example

The null: new pricing page copy, no change in trial-to-paid conversion (p = 0.68, CI on the relative effect -2.1% to +3.3%).

Version A, as Claude drafted it:
> We tested whether rewriting the pricing page copy to emphasize annual savings would increase trial-to-paid conversion. It did not. The 95% confidence interval on the relative effect is -2.1% to +3.3%, which lets us rule out meaningful improvement (>3.3%) but does not rule out small effects in either direction. The hypothesis that copy emphasis is a meaningful driver of trial-to-paid conversion is not supported by this test.

Version B:
> *[version A, plus:]* Of the three sub-segments we examined, mobile users in Western Europe showed a directional positive effect (+2.8%, CI -1.4% to +7.2%). We did not pre-register this segment, so we are not treating this as a finding. If the team wants to pursue this, it would require a new test powered on that segment.

Version C:
> *[version B, plus:]* The null primary result updates our view of the copy-testing roadmap. We had prioritized three additional copy experiments behind this one under the implicit assumption that copy is a meaningful lever. This result doesn't rule out that assumption, but it does weaken it. Options: (a) deprioritize the remaining copy tests in favor of structural page changes; (b) run one more copy test with a sharper hypothesis; (c) pursue the mobile-EU directional signal with a properly-powered test. My recommendation is (b) + (c).

Claude's pick: version B for a PM and design audience, since they'll want to know if there's anything to chase next, but the null is still the headline. Version C if it were going to whoever owns the pricing roadmap.

## Where it goes wrong

It sometimes slips secondary observations back into version A even though you asked it not to. Skim it and cut them.

## When not to bother

- Nulls that don't tell you anything, like underpowered tests or tests with execution problems. The right readout there is "we can't conclude anything," and you shouldn't use this to manufacture learnings.
- Plain negative results where the team just needs to move on. Version A alone is probably more than enough.
