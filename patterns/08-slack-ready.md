# Pattern 08: Slack-ready explanation

The finding lives in a doc or a notebook, and a PM asks for it in Slack. Pasting the doc language reads stiff and too long, and rewriting it properly takes five minutes you don't have. This does the rewrite in about 20 seconds.

Take the doc language and have Claude rewrite it as a Slack message: conversational, no headings, and understandable without clicking through to anything.

## The prompt

```
Rewrite the analysis below so it reads natively as a Slack message.

SOURCE:
{paste the doc language}

AUDIENCE:
{who you're sending this to (PM, engineer, exec) and their familiarity
with the analysis context}

RULES:
1. One paragraph or at most a short paragraph + 2-3 bullets. No headings.
2. Conversational but not casual. This is work Slack, not text messages.
3. Lead with the finding. No "here's an update on the analysis" preamble.
4. If there's a number, it goes in the first sentence.
5. Preserve the important caveat (the one that changes the decision).
   Other caveats can be dropped or hinted at with "more detail in the doc".
6. End with what I want from the reader: a question, a decision ask, or
   "just FYI, no action needed."

Do not add phrases like "just wanted to share" or "hope this helps."
Do not add emoji unless the source used them.
```

## Why the tone matters

Slack isn't a doc. Paste doc language into a channel and it becomes a wall of text people skim and never reply to. Put chatty language in a doc and it looks unserious. Matching the writing to where it's going is a real skill, and the model turns out to be pretty good at it.

## End with the ask

This is the rule that matters most. A Slack message without a clear ask at the end tends to get ignored. "Just FYI" counts as an ask. So does "should we escalate this to the pricing team?" Ending on a caveat and hoping the reader works out what to do doesn't.

## Example

The doc language:
> **Summary of findings**
>
> Analysis of the new onboarding flow's performance indicates that the treatment
> group exhibited a statistically significant increase in Day 1 activation of
> 3.2% (p = 0.02, 95% CI 0.7% to 5.7%) relative to control. However, this
> effect was not uniformly distributed across segments. Specifically, the
> enterprise segment showed no significant lift (0.4%, p = 0.91), while the
> individual/free segment drove nearly all of the observed effect (5.1%,
> p < 0.01). Guardrail metrics including 7-day retention and customer
> support contact rate did not show adverse movement.

Claude's Slack version, for the PM who ran the test with me:

> New onboarding flow lifts Day 1 activation 3.2% overall (p=0.02), but the effect is basically all in free/individual. Enterprise is flat. Guardrails clean. My read: ship to free/individual, hold off on enterprise until we run a version tuned for that flow. Full doc linked, happy to walk through if useful. Do you want to take this to launch review Thursday or next week?

What it did:
- Put the number first.
- Dropped the confidence interval, which is in the doc and not needed in the channel.
- Kept the caveat that changes the recommendation: enterprise is flat.
- Dropped the guardrail details but said they're clean.
- Ended with a clear question.

## Where it goes wrong

- It can get too casual ("So, TLDR: new onboarding is a win for free users!"). The line between conversational and unserious is thin, so check the tone.
- It sometimes adds emoji ("✅ Guardrails clean") even when told not to. Delete them.
- With sensitive findings, like something being broken or someone's project not paying off, it tends to soften the ask. If the message needs to land, rewrite the last sentence yourself.

## When not to bother

- Messages to a close collaborator who already has the context. One line is enough.
- Decisions that should happen in a doc, where Slack is the wrong place anyway.
