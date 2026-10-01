# Pattern 14: Explaining segments

You ran k-means (or hierarchical clustering, or a GMM) and got five clusters that separate well on the features you care about. Now you have to explain them to a PM or growth lead. If you present them as "Cluster 1: high on feature_a, medium on feature_b, low on feature_c," the meeting is over and nothing happens.

Give Claude the cluster centroids (or per-cluster feature medians) with a plain-language description of each feature, and ask for three things per cluster: a short name based on its most distinctive features, a two or three sentence description of what someone in that cluster actually does, and one line on what a PM could do with it.

The key rule: name each cluster after its top two or three distinguishing features, not all of them. A name that tries to cover every dimension ("moderately active, price-sensitive, weekend-heavy mobile users") is accurate and impossible to remember. "Weekend warriors: mobile-only, busy Saturday and Sunday, quiet the rest of the week" is a name people can repeat in a meeting weeks later.

## Common problems

Presenting the centroids. Even with the features translated into words, you're asking the reader to reconstruct a person from a score sheet.

Describing every cluster the same way. Five evenly weighted paragraphs, none of which tells the reader which cluster matters for their decision.

Names that are just labels. "Segment A, B, C" is fine inside the DS team. For anyone else, if they have to look up which one A was, you've lost them.

Naming and describing segments doesn't need statistics expertise, but it does need someone who writes well and has a feel for the product, which is where Claude helps.

## The prompt

```
I've run a clustering analysis and need to explain the segments to a
PM. Help me write names, short descriptions, and actions for each.

CONTEXT:
- Product: {one-line description}
- Population: {who's in the data, e.g. "logged-in users active in the
  last 90 days"}
- The decision this segmentation should inform: {e.g., "which segment
  to target with a re-engagement campaign", "which cluster is most
  likely to convert to paid"}

FEATURES (with plain-language meanings):
- feature_1: {name}. Meaning: {"days out of the last 30 the user opened
  the app"}
- feature_2: {name}. Meaning: {...}
- {... usually 5-10 features}

CLUSTER CENTROIDS (or per-cluster medians, pick one, don't mix):

| Feature   | Cluster 1 | Cluster 2 | Cluster 3 | ... | Overall |
|-----------|-----------|-----------|-----------|-----|---------|
| feature_1 | ...       | ...       | ...       |     | ...     |

Cluster sizes (% of population):
- Cluster 1: X%
- Cluster 2: Y%

For EACH cluster:

1. Name: 2-4 words, based on the 2-3 features where this cluster is
   furthest from the overall average. Something a PM could repeat in a
   meeting weeks later. Don't describe every dimension. Don't invent
   demographics that aren't in the data (no "Sarah" or "the millennial
   mom").

2. Description (2-3 sentences): what a user in this cluster actually
   does in the product. Every claim must tie to a specific feature value.
   Leave out features that are close to the overall average.

3. What a PM could do with this segment: one sentence. A specific
   action, or honestly "this isn't the cluster to act on for this
   decision."

Then:

4. Given the decision in CONTEXT, which cluster should the team focus
   on first, and why? Say so if it's a tie.

5. Which cluster are you least confident in? Usually the small one, the
   one close to the overall average, or the one whose top features are
   close calls.
```

## Why the naming rules

A good segment name is two to four words, which is short enough for a Slack message.

It's based on the features where the cluster is furthest from the average, not the ones with the biggest raw values. If everyone has a high session count, a high session count isn't what makes this cluster different.

It doesn't make up demographics. If you didn't have age or gender as features, the cluster doesn't have an age or gender. Calling a cluster "retirees" from behavior alone is inventing a biography.

## Example (illustrative)

Input (shortened): a note-taking app with free and paid tiers. The question is which cluster is most likely to convert to paid, for an in-product upsell. Five clusters over eight features (sessions, notes created, shares, days since signup, mobile only, note length, uses search, uses folders).

The kind of output to aim for, for two of the clusters:

> **Cluster 3: "Power organizers"** (14% of users)
>
> They create three to four times as many notes as the average user (median 47 in 30 days vs. 12 overall), and they all use folders (100% vs. 34% overall) and mostly use search (87% vs. 22%). Their session count is only a little above average. They don't visit more often, they do more per visit. This is the cluster to target for the paid upsell: they're already pushing against the free tier's organization limits, and folders and unlimited notes are two of the main paid features.
>
> *Action:* an in-product upsell tied to folder count and note limits, not a generic "upgrade" prompt.
>
> **Cluster 5: "One-off writers"** (23% of users)
>
> A few long notes (note length four times the overall median, only 3 notes in 30 days), and they rarely come back after the first week (median 2 sessions in 30 days). No sharing, organizing or searching. They seem to be using the product as a one-time document editor, not a note-taking tool.
>
> *Action:* not the cluster for a paid push. It is interesting for a different question, though: is this failed activation, or a use case the product isn't designed for? Worth some user interviews.
>
> **Focus:** Cluster 3 for the paid upsell. Cluster 2 is a distant second.
>
> **Least confident:** Cluster 4 (8% of users, with three of its top features close to the overall average). Rerun with k=4 and see whether it disappears. It may be an artifact of choosing k=5.

## Where it goes wrong

It invents traits. If a feature isn't in your table, Claude may still describe a cluster as "probably younger" or "more mobile-first." Read each description sentence by sentence and delete anything that doesn't tie to a feature value.

It picks catchy names that get the direction wrong, like calling a cluster "lurkers" when it's high on both reading and writing. Check each name against the features it's supposed to reflect.

It skips over how sensitive the clusters are to k. Write-ups almost never say "with k=4 or k=6 the story changes," and the "least confident" question exists to force that. If Claude says every cluster is equally solid, push back.

It forces an action for every cluster. Some clusters are just average users doing average things. Say "no targeted action; this is the baseline" instead of inventing a campaign.

## When not to bother

- Two clusters. You can describe those in one sentence.
- Unstable clusters. If a different random seed reshuffles them, fix the clustering first.
- A technical write-up for other data scientists, where the feature-level description is what people want.

## Related patterns

- Pattern 07 (exec TL;DR): to boil the whole segmentation down to three bullets for an exec deck.
- Pattern 05 (calibrated language): for the action lines, where "target this cluster" and "this cluster is one option worth testing" are different claims.
- Pattern 10 (metric sanity check): run it on your feature definitions before clustering. If `session_count` counts every page load, your "engaged" cluster might just be people on bad wifi.
