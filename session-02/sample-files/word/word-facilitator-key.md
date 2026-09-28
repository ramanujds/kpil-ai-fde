# Copilot in Word: Facilitator Key

**AI Developer & FDE Training | Kalpataru Projects, Ahmedabad**
Day 2, Block 2: Word | For the trainer only. Do not share with trainees before the exercise.

> Scope note: this key lists the source facts and planted traps in the three FreshCart Word files, so you can check trainees' Copilot outputs quickly. Copilot output varies between runs; the "watch for" items describe common problems, not guaranteed ones.

---

## Source Facts: Q3 Supplier Performance Update

| Supplier | On-time | Fill rate | Complaints | Price change |
|---|---|---|---|---|
| Green Acre Farms (vegetables) | 94% | 97% | 41 | +3% |
| Coastal Dairy Co. (dairy) | 88% | 93% | 63 | +6% from 1 Oct |
| Sunrise Bakers (bakery) | 96% | 98% | 12 | 0% |
| Harvest Ridge Produce (fruit) | 81% | 89% | 97 | +2% |

| Fact | Value |
|---|---|
| Total supplier-related complaints | 213 |
| Average daily orders | 1,600 in Q2, 1,850 in Q3 |
| Orders in the quarter | About 170,200 over 92 days |
| Customer delivery promise | 90 minutes |
| Cold-chain incident | 14 August, 1,120 units of yoghurt discarded |
| Credit note from Coastal Dairy | Rs 2.4 lakh, received |
| Coastal Dairy cooler repaired | 20 August |
| Harvest Ridge second vehicle | From 1 November |
| Late deliveries at Harvest Ridge | Mostly Monday and Friday mornings |
| Decision needed by | 10 October |
| Improvement plan length for Harvest Ridge | 60 days |
| Sunrise Bakers volume increase recommended | 10% |

Not stated anywhere in the document: an overall on-time percentage, any supplier's revenue, any named delivery driver, the cost of the improvement plan.

## Exercise C: What to Check in Summaries

| Check | Why it matters |
|---|---|
| Does the summary give a single overall on-time figure? | The document does not state one. Any average is Copilot's own calculation and should be labelled that way. |
| Are the four on-time figures and complaint counts exact? | A rounded or swapped figure is the most common slip. |
| Does it say who is responsible for the decision? | The document names Meera Iyer as the audience and 10 October as the deadline. |
| Does it say the second Harvest Ridge vehicle "fixes" the problem? | The document says only that it is committed from 1 November. |

## Exercise D: Planted Traps in the Messy Meeting Notes

| Trap in the notes | What a careless output does | Correct handling |
|---|---|---|
| Number of vehicles with sensors is "18 vans? or 15??" | States one number as fact | Flag as unconfirmed |
| Action 1, "send complaint data - Meera?? or me" | Assigns it to Meera | Owner not stated, or "Meera or Arjun, to be confirmed" |
| Action 5, "someone to look at milk complaints" | Invents an owner | Owner not stated |
| Action 2 has no date, only "after Rohan reverts" | Invents a due date | Date depends on Coastal Dairy's reply |
| Price: "non negotiable" then "maybe 4% if we sign 12 month" | Records only 6% or only 4% | Record both statements and mark as unresolved |
| Temperature logs: "from Oct, not sure about Sept" | Says logs start 1 September or 1 October as fact | Start in October; September not agreed |
| Milk complaints: Priya blames retailers, "we didnt agree on this" | Lists the cause as agreed | Record as a disputed point |
| Finance attendee "didn't catch name" | Invents a name | Attendee name not recorded |
| Next meeting "end of oct?? nothing fixed" | Gives a date | No date fixed |
| Delivery window trial | Records 5 am as agreed | Only a two-week trial was mentioned as workable; the warehouse must check feasibility |

## Exercise E: Problems in the Delay Notice Draft

| Problem | Type |
|---|---|
| "2 hours" delivery promise in paragraph 2, then "90 minutes" near the end | Factual inconsistency; the correct promise is 90 minutes |
| Key message and apology are buried; the notice opens with "It has come to our attention" | Structure |
| Long, passive sentences ("steps are being taken", "it was not able to arrive") | Clarity |
| "Also it rained a lot" is unexplained and sounds like an excuse | Tone |
| Spelling: "inconvinience", "customers who's", "entitled too" | Grammar |
| Lowercase "we advise" starting a sentence | Grammar |
| Support number is not given; the notice says it is "available in the app" | Missing information |
| Discount stated as 10% for delays over 30 minutes, with no expiry or limit | Missing information |
| The notice blames the supplier by role without the impact on the customer | Tone |

## Common Copilot Behaviours to Watch For

- Fills gaps with plausible details instead of writing "not stated", especially in tables with Owner and Date columns
- Rounds or reformats numbers when shortening text
- Softens or strengthens a claim when changing tone
- Ignores "use only this document" when the prompt is long
- Adds a confident closing sentence that promises more than the source supports

## Talking Points When Trainees Find a Mistake

1. Ask how they found it, and reinforce the habit of checking against the source.
2. Contrast Prompt D1 (owner and due date for every action) with Prompt D2 (write "To be confirmed" instead of guessing). D1 pushes Copilot to fill the gaps, so expect invented owners and dates; D2 shows how one instruction changes the result.
3. Compare two trainees' outputs for the same prompt; the differences make the case for human review.

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
