# Copilot in PowerPoint: Facilitator Key

**AI Developer & FDE Training | Kalpataru Projects, Ahmedabad**
Day 2, Block 4: PowerPoint | For the trainer only. Do not share with trainees before the exercise.

> Scope note: this key lists the planted problems in the draft deck and what to watch for in trainees' Copilot outputs. Copilot output varies between runs; the "watch for" items describe common problems, not guaranteed ones. The draft deck is built from the same synthetic FreshCart facts as the Q3 Supplier Performance Update Word file; see the Word facilitator key for the full source facts.

---

## Planted Problems in FreshCart_Supplier_Review_Draft.pptx

| Slide | Problem | Type |
|---|---|---|
| 1 | Title reads "Supplier Review Q3" with "Draft v3" on the slide | Polish |
| 2 | Recommendations appear before any findings or background | Order |
| 3 | Agenda is slide 3, not slide 2, and does not match the deck: it omits Recommendations and lists sections in a different order | Order and consistency |
| 4 | Title is lowercase, and the slide is one long centred paragraph | Too much text, consistency |
| 5 | Twelve bullets, mixing figures, definitions and a source line; title has two exclamation marks and a larger font size | Too much text, consistency |
| 5 and 7 | Harvest Ridge on-time is 81% on slide 5 and 84% on slide 7 | Factual inconsistency; the correct figure is 81% |
| 5 and 6 | Coastal Dairy complaints are 63 on slide 5 and 36 on slide 6 | Factual inconsistency; the correct figure is 63 |
| 6 | Set in Times New Roman, unlike the other slides | Consistency |
| 6 | "18 vehicles, to be confirmed" for sensors; the meeting notes said 18 or 15 | Unverified detail |
| 7 | Title has a hyphen and "Problems", inconsistent with other titles | Consistency |
| 8 | Title is oversized and red | Consistency |
| 8 | "Rain in July ... could recur" goes beyond the report, which only mentions the July rain in the Green Acre section; "Warehouse staffing at 5 am is not confirmed" comes from the meeting notes, not the report | Content not in the source |
| 9 | "Other observations" includes parking, festival lighting, app rating and new riders: unrelated to the decision | Slides that do not belong |
| 10 | Next steps have no owners or dates; last bullet says "Decision needed soon" instead of 10 October | Missing information |
| 11 | "Questions??" | Polish |
| All | No speaker notes on any slide | Missing information |
| Deck | No executive summary and no statement of the decision needed up front | Missing information |

## Source Facts to Check Against

| Fact | Correct value |
|---|---|
| Harvest Ridge Produce on-time delivery | 81% |
| Coastal Dairy Co. complaints | 63 |
| Total supplier-related complaints | 213 |
| Decision needed by | 10 October |
| Harvest Ridge second vehicle | From 1 November |
| Cold-chain incident | 14 August, 1,120 units of yoghurt |
| Credit note | Rs 2.4 lakh, received |

## Exercise Checks

| Exercise | What good looks like | Watch for |
|---|---|---|
| A. Prompt to deck | Five slides as asked, four bullets or fewer | More slides than requested; invented statistics, dates or stock images; requests that are not in the prompt |
| B. Document to deck | Six slides, decision first, numbers match the report | Padding beyond six slides; a chart with figures not in the document; dropped or altered numbers; owners or dates not in the source |
| C. Executive summary | Decision needed plus three findings, sourced from the deck | Repeating a wrong figure (84% or 36) as fact; stating a decision date that the deck does not give |
| D1. Review | Finds ordering, text volume, style and filler slides | Missing the two number conflicts; reviewing style only |
| D2. Reorder | Logical flow, no facts lost | Dropping slides or bullets while claiming "no facts deleted" |
| D3. Table | Four rows, four measures, definitions moved to notes | Table with numbers that differ from the slide; definitions lost |
| D6. Next steps | "Not stated" for owners and dates | Owners or dates filled in, or a date copied from another slide |
| E. Speaker notes | Short notes that add no new facts | Notes that add claims, statistics or reasons the slides do not contain |

## Talking Points When Trainees Find a Mistake

1. Ask how they spotted it. If they saw two slides disagree, point out that no review of a single slide would have caught it.
2. Show the effect of stating the slide count and the source in the prompt. Compare a prompt that does and one that does not.
3. Contrast Prompt D6 with a version that leaves out "write Not stated". Copilot often fills in plausible owners and dates when nothing tells it not to.
4. Ask trainees whether they would present the deck as it stands. The answer reinforces the closing checklist.

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
