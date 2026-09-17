# Pattern 14 — Segmentation storytelling

**Problem this solves:** You ran k-means (or hierarchical, or GMM, or whatever) and got 5 clusters that meaningfully separate on the features you care about. The silhouette score is defensible. Now you have to explain this to a PM or growth lead. If you present it as "Cluster 1: high on feature_a, medium on feature_b, low on feature_c", the meeting is over and nothing happens.

**The pattern:** Feed Claude the cluster centroids (or the per-feature distribution per cluster) along with a short description of what each feature means in plain product terms, and ask it to produce (a) a memorable *name* for each cluster grounded in the highest-signal features, (b) a one-paragraph pen portrait of a user in that cluster written in the way a growth marketer thinks about people, and (c) an explicit "what a PM could do with this cluster" line.

The move that makes this work: **name the cluster from its top two or three distinguishing features, not from all of them.** A name that tries to encode every dimension becomes "high-power moderately-engaged mostly-mobile weekend-heavy user" — accurate, useless, unmemorable. A name that captures the top two features ("Weekend warriors: mobile-only, high session count on Sat/Sun, dormant Mon–Fri") is a name the PM can repeat back to you in a meeting three weeks later.

---

## Why this exists

Segmentation is where DS most reliably lose the plot. You did real work — feature engineering, dimensionality reduction, cluster stability checks, silhouette scores — and it gets communicated in a way that lets the PM's brain glaze. The technical quality of the segmentation and the actionability of the writeup have almost nothing to do with each other.

Three anti-patterns I've watched myself and colleagues fall into:

1. **The feature vector**. Presenting clusters as their centroid vectors. Even when you translate the features to prose ("high on session_count, low on days_since_signup"), you're asking the reader to reconstruct a human from a scoresheet. Nobody does that.
2. **The taxonomy dump**. Five clusters, each described as one paragraph of "these users tend to..." bullet lists. Perfectly balanced. Perfectly forgettable. There's no priority signal about which cluster the reader should care about.
3. **The name that's actually a label.** "Segment A / B / C". This is fine for internal DS discussions and terrible for stakeholder work. If the PM has to look up which one "A" is, you've lost.

The Claude-assisted version of this is one of the highest-leverage single prompts in the whole playbook. Naming and portrait-writing are the parts of segmentation work that don't need statistical expertise but strongly benefit from a good writer with product intuition.

---

## The prompt template

```
I've run a clustering analysis and I need to explain the resulting
segments to a PM. Help me produce names, pen portraits, and
actionability lines for each cluster.

CONTEXT:
- Product: {one-line description}
- Population: {who's in the data — e.g., "logged-in users active in
  the last 90 days"}
- What business decision this segmentation is meant to inform:
  {e.g., "which segment to target with a re-engagement campaign",
  "which persona to design the onboarding for", "which cluster is
  most likely to convert to paid"}

FEATURES USED (with plain-product-language descriptions):
- feature_1: {name}. What it means: {"how many days out of the
  last 30 the user opened the app"}.
- feature_2: {name}. Meaning: {...}
- {... etc — 5-10 features is typical}

CLUSTER CENTROIDS (or per-cluster feature medians — pick one; do
not mix):

| Feature       | Cluster 1 | Cluster 2 | Cluster 3 | ... | Overall |
|---------------|-----------|-----------|-----------|-----|---------|
| feature_1     | ...       | ...       | ...       |     | ...     |
| ...           |           |           |           |     |         |

Cluster sizes (as % of population):
- Cluster 1: X%
- Cluster 2: Y%
- ...

For EACH cluster, produce:

1. **Name** — a 2-4 word memorable name. Rules: MUST be grounded in
   the top 2-3 distinguishing features (the ones where this cluster
   is furthest from the overall average). MUST be a name a PM could
   repeat back in a meeting three weeks later. Avoid names that
   describe every dimension. Avoid persona names that project
   demographic attributes not in the data (don't call them "Sarah"
   or "the millennial mom" — you don't know that).

2. **Pen portrait** (2-3 sentences). Describe what a user in this
   cluster actually does in the product, in the language a growth
   marketer would use. Ground every claim in a specific feature
   value; don't invent behavior. If a feature is close to the
   overall average, do not include it — mention only the
   distinguishing ones.

3. **What a PM could do with this segment** — one sentence. A
   specific product or growth action, or the honest answer "this
   cluster is not the one to act on for this decision."

Then produce:

4. **A ranking**: given the business decision named in CONTEXT,
   which cluster should the team focus on FIRST, and why? If
   multiple are tied, say so honestly.

5. **Which cluster you're least confident in** — usually the small
   one, or the one that's close to the overall centroid, or the one
   where the top features are close-run. Flag it. The PM needs to
   know which findings are load-bearing and which are shakier.
```

---

## Why the naming rules matter

I once shipped a segmentation writeup where I named a cluster "The engaged converters" — a two-word name, grounded in the top feature (conversion rate). It was reused verbatim in three follow-on decks by other teams. That's the whole game.

The failure case: I've also shipped writeups where I named a cluster something like "Moderately active, price-sensitive, weekend-heavy, mobile-preferring users." Nobody used the name. In the next meeting the cluster was referred to as "the third one, you know, the one that was mostly on the weekends?" That's not a name; that's a query.

Good cluster names have three properties:

- **Two to four words.** Long enough to be specific, short enough to be a slack message.
- **Grounded in the top features by distance from overall.** Not the top features by absolute value. A cluster that's high on session_count only matters if session_count is where it *differs* — if everyone is high on session_count, that's not the story.
- **No projected demographics.** If you didn't feature-engineer "age" or "gender", the cluster doesn't have those. Naming a cluster "The retiree" from behavioral features alone is confidently making up biography.

---

## Example

**Input** (heavily abbreviated):

- Product: a note-taking app with free and paid tiers
- Business question: which cluster is most likely to convert to paid, so we can target them in an in-product upsell
- 5 clusters over 8 features (session_count_30d, notes_created_30d, share_actions_30d, days_since_signup, mobile_only, avg_note_length, uses_search, uses_folders)

**Claude output (excerpt for two clusters)**:

> **Cluster 3 — "Power organizers"** (14% of users)
>
> Users in this cluster create 3-4x more notes than the average user (notes_created_30d median 47 vs. overall 12) and are heavy users of folder structure (uses_folders 100% vs. overall 34%) and search (uses_search 87% vs. overall 22%). Their session counts are only slightly above average — they don't visit more, they do more per visit. This cluster is the one to focus on for the paid upsell: they're already stressing the free-tier feature set on organization, and folders + unlimited notes are two of the paid-tier headline features.
>
> *Action*: target this cluster with an in-product upsell tied specifically to folder count and note limits. Do not use a generic "upgrade" prompt; anchor on what they're already doing.
>
> **Cluster 5 — "One-off writers"** (23% of users)
>
> This cluster creates a small number of long notes (avg_note_length 4x overall median; notes_created_30d only 3) and rarely returns after the first week (session_count_30d median is 2). They are not sharing, not organizing, not searching. This looks like people using the product as a one-off document editor rather than an ongoing note-taking tool.
>
> *Action*: this cluster is not the one to target for paid conversion — the behavior doesn't suggest sustained value. But it's the interesting cluster for a different question: is this a failed activation (people who wanted a note tool and bounced) or a valid use case we're not designing for? Worth a qualitative follow-up, not a paid-tier push.
>
> **Focus recommendation**: for the "who converts to paid" question, Cluster 3 (Power organizers) is the clear focus — they combine high engagement with product-usage patterns aligned to the paid-tier value prop. Cluster 2 ("Weekend note-jotters") is a distant second.
>
> **Lowest confidence**: Cluster 4 (small cluster, 8% of population, three of its top features are close to the overall mean). I'd re-run the clustering with k=4 and see if Cluster 4 dissolves — it might be an artifact of the k choice rather than a real segment.

---

## Failure modes

**Claude will invent traits the data doesn't support.** If a feature isn't in the centroid table, Claude may still confidently describe users in that cluster as "probably younger" or "more mobile-first" (without mobile_only in your features). Read the pen portraits sentence-by-sentence and delete anything that doesn't trace to a specific feature value.

**Claude picks memorable names that are wrong.** Occasionally Claude will pick a name that's punchy but misinterprets the direction of a feature (e.g., naming a cluster "The lurkers" when the cluster is actually *high* on read-only actions and *also* high on write actions — they're just doing everything). Cross-check each name against the top-3 features it's meant to encode.

**Cluster-count sensitivity gets buried.** Segmentation writeups almost never say "if we'd picked k=4 or k=6 instead of k=5, the story would be different." The prompt's "lowest confidence" section is meant to force this. If Claude confidently ranks all clusters as equally solid, push back — there's almost always one that's on the edge.

**The "act on nothing" cluster.** Some clusters are honestly "no action needed" — average users doing average things. Claude will often force an action recommendation anyway. Edit those to say "no targeted action; this is the baseline population." Not every cluster deserves a campaign.

## When to skip

- **You have 2 clusters.** Two clusters is a segmentation you can describe in a sentence: "Group A does X, Group B does Y." A structured pen-portrait exercise is overkill.
- **The clusters aren't stable.** If you re-run the clustering with a different seed and the clusters shuffle, don't write pen portraits — the whole thing is noise. Fix the clustering first.
- **You need the technical writeup, not the PM writeup.** For a paper or internal DS review, the feature-vector description is what people want. Skip the storytelling; save it for the stakeholder version.

## Related patterns

- Pattern 07 (Exec TL;DR) — after this pattern produces cluster portraits, use pattern 07 to compress the whole segmentation into three bullets for an exec deck.
- Pattern 05 (calibrated language) — critical when Claude drafts the "what to do about it" line. "Target this cluster" is different from "consider targeting this cluster as one option among several."
- Pattern 10 (metric sanity check) — apply to your feature definitions before clustering. If `session_count` counts every page load, your "engaged" cluster might just be users on flaky wifi that reloads a lot.
