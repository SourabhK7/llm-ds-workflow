# Pattern 08 — Slack-ready explanation

**Problem this solves:** You have a finding that lives in a Confluence doc or notebook. A PM asks for it in Slack. Copy-pasting the doc language into Slack reads as cold and over-long. Rewriting for Slack register takes 5 minutes you don't have. This pattern does the rewrite in 20 seconds.

**The pattern:** Take the formal analysis language and rewrite it for Slack — conversational register, no headings, optimized for "understandable in-channel without clicking through to a doc."

---

## The prompt template

```
Rewrite the analysis below so it reads natively as a Slack message.

SOURCE:
{paste the doc language}

AUDIENCE:
{who you're sending this to — PM, engineer, exec — and their familiarity
with the analysis context}

RULES:
1. One paragraph or at most a short paragraph + 2-3 bullets. No headings.
2. Conversational but not casual — this is work Slack, not text messages.
3. Lead with the finding. No "here's an update on the analysis" preamble.
4. If there's a number, it goes in the first sentence.
5. Preserve the important caveat (the one that changes the decision).
   Other caveats can be dropped or hinted at with "more detail in the doc".
6. End with what I want from the reader: a question, a decision ask, or
   "just FYI, no action needed."

Do not add phrases like "just wanted to share" or "hope this helps."
Do not add emoji unless the source used them.
```

## Why the register matters

Slack is a different medium than a doc. The failure mode of doc-language-in-Slack is that it reads as a wall of text the reader skims and doesn't respond to. The failure mode of casual-language-in-a-doc is that it reads as unserious. Matching register to medium is a real writing skill; the LLM is surprisingly good at it.

## The single most important rule: ending with the ask

Slack messages that don't end with a clear ask get left unread. "Just FYI" is a valid ask. So is "should we escalate this to the pricing team?" What's not valid is ending with a caveat or a hedge and hoping the reader figures out what to do.

## Example

**Source** (doc language):
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

**Claude's Slack rewrite** (audience: PM who ran this with me):

> New onboarding flow lifts Day 1 activation 3.2% overall (p=0.02), but the effect is basically all in free/individual — enterprise is flat. Guardrails clean. My read: ship to free/individual, hold off on enterprise until we run a version tuned for that flow. Full doc linked, happy to walk through if useful — do you want to take this to launch review Thursday or next week?

Compare:
- Leads with the number.
- Drops the confidence interval (available in the doc; not needed for the in-channel read).
- Preserves the important caveat (enterprise is flat) — this is the caveat that changes the recommendation.
- Drops the guardrail detail but signals it's clean.
- Ends with a clear decision ask.

---

## Failure modes

- **Claude sometimes casualizes too much** ("So, TLDR: new onboarding is a win for free users!"). Check tone; the line between "conversational" and "unserious" is narrow.
- **Claude will occasionally add emoji** ("✅ Guardrails clean") even when I tell it not to. Just strip them.
- **For sensitive findings** (something's broken, someone's work didn't pay off), Claude will often soften the ask. If you need the message to actually land, rewrite the last sentence yourself.

## When to skip

- Messages you're sending to a close collaborator who already has full context. A one-liner is fine.
- Asynchronous decision docs where Slack isn't the right medium anyway.
