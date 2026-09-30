# Copilot for Teams Tasks: Exercise Handout

**AI Developer & FDE Training | Kalpataru Projects, Ahmedabad**
Day 2, Block 6: Teams | 30 minutes

In this exercise you will turn a meeting into a summary, decisions and action items, and practise catching up on something you missed. If you can run a live Teams call, you will do this with a real recording and transcript. If not, you will use a ready-made transcript that stands in for one. Either way, you will work with a script about FreshCart, a made-up grocery delivery business. The business, people and events are all fictional.

By the end you will be able to:

1. Turn a meeting recording or transcript into a short summary
2. Pull out decisions and action items, with owners and dates
3. Spot when a recap states something as fact that was only spoken as a guess or left unclear
4. Use Copilot to catch up on something you missed
5. Check a recap against the transcript before you rely on it

---

## Before You Start

Choose one of two paths, depending on what is available to your group.

**Path 1: Live meeting (if you can).** Form a group of three. Use the mock-meeting script. Start a Teams "Meet now" call or a scheduled meeting, turn on transcription or recording, and have the three volunteers read their parts naturally. End the call, then open the Recap.

**Path 2: Ready-made transcript (if Teams access, transcription or three volunteers are not available).** Open the pre-written transcript file directly and paste it into Copilot Chat or Copilot in Word. Every prompt below still works; wherever a step says "open the Recap tab", instead paste the transcript and ask the same question.

- Use only the sample files. Do not use a real work meeting or paste real transcripts into Copilot during this exercise.
- Read the transcript once yourself, in either path, before checking Copilot's answers against it.
- Copilot gives a different answer each time, and Path 1 groups will each get a slightly different recording. That is expected.
- If you are in a group of three for Path 1, decide who plays which role before you start.

## The Sample Files

| File | What it is | Used in |
|---|---|---|
| FreshCart_Harvest_Ridge_Meeting_Script.docx | A script for three volunteers to read aloud | Path 1 |
| FreshCart_Harvest_Ridge_Meeting_Transcript.docx | The same conversation, already written out as a transcript | Path 2, and for checking Path 1's real transcript afterwards |

The meeting is a short supplier check-in: FreshCart's operations manager and procurement lead speak with the owner of Harvest Ridge Produce, a fruit supplier, about an improvement plan raised in an earlier report.

## How to Write a Good Prompt

Use the same four parts as in the earlier exercises.

| Part | Question it answers | Example |
|---|---|---|
| Goal | What do I want? | "List the action items" |
| Context | Who is it for, and why? | "For someone who missed the meeting" |
| Source | What should Copilot use? | "Use only this meeting" |
| Expectations | What shape do I want back? | "A table with owner and due date" |

## Suggested Timing

| Step | Minutes |
|---|---|
| Trainer demonstration or screen guide recap | 3 |
| Set-up: record the meeting, or open the transcript | 6 |
| A. Summarise the meeting | 5 |
| B. Decisions and action items | 6 |
| C. Fact versus guess | 5 |
| D. Catching up | 3 |
| E. Check before you rely on it | 2 |

---

## Exercise A: Summarise the Meeting

**If Path 1:** open the Recap tab and select Open Copilot, or ask in the meeting chat.
**If Path 2:** paste the transcript into Copilot Chat or Word first.

**Prompt A1**

> Summarise this meeting in five bullet points, for someone who was not there.

**Prompt A2**

> What was the main topic of this meeting, and what update was given on it?

**Prompt A3**

> Did anyone raise a concern or a risk during this meeting? What was it?

**Think about it:** Read the transcript once yourself. Did the summary include the most important update, or did it bury it under smaller points?

---

## Exercise B: Decisions and Action Items

**Prompt B1**

> List the action items from this meeting. For each one, give the owner and the due date, using only what was actually said. Where the meeting does not name an owner or a date, write "Not stated".

**Prompt B2: Check the date logic**

> The meeting mentions a follow-up timeframe more than once. What exactly was said about when the next check-in will happen? Quote the relevant lines.

**Prompt B3: A second pass without the guardrail**

> Now list the action items again, but this time make sure every action has an owner and a due date.

**Think about it:** Compare B1 and B3. Did B3 invent an owner or a date that B1 correctly left as "Not stated"? What instruction caused the difference?

---

## Exercise C: Fact Versus Guess

**Prompt C1**

> What date was given in this meeting for the second delivery vehicle to be in service?

**Prompt C2: A harder question**

> Is the date given in this meeting for the second vehicle the same as, earlier than, or later than any date you may already know from other FreshCart documents about Harvest Ridge Produce? Say clearly if you are not certain, rather than guessing.

**Prompt C3**

> Summarise the meeting again, but this time mark every point with either [Said in the meeting] or [My own inference], so I can tell the two apart.

**Think about it:** What date was actually spoken in the meeting? If you have seen the FreshCart Q3 Supplier Performance Update from the Word exercise, does it match? What should you do with a mismatch like this in real work?

---

## Exercise D: Catching Up

**Prompt D1**

> I missed the first half of this meeting. What did I miss?

**Prompt D2**

> Give me a two-sentence version of this meeting I could read out loud to a colleague who has thirty seconds.

**Think about it:** Is the two-sentence version in D2 still accurate, or did shortening it drop something that matters, such as the changed vehicle date?

---

## Exercise E: Check Before You Rely on It

Use this checklist on every recap or summary from Exercises A to D.

| Check | Done |
|---|---|
| Every date and figure matches what was actually said, not what I assumed | |
| Owners and due dates are only stated where the meeting actually gave them | |
| Anything unclear or unresolved is flagged, not smoothed over | |
| I have read or listened to the source myself, not just the recap | |
| I know whether this recap came from a real recording or the written transcript | |

If you cannot tick a box, check the transcript, correct the recap, or ask Copilot to redo it with clearer instructions.

---

## Your Notes

Write down what you found. Your trainer will ask a few of you to share.

| Question | My answer |
|---|---|
| What date was given for the second vehicle, and did it match what you expected? | |
| Which action item was hardest to pin an owner or date to? | |
| What changed between Prompt B1 and B3? | |
| One meeting from my own work I could try this on | |

## Stretch Prompts

If you finish early, try these on the transcript.

> If you were writing the minutes of this meeting for a file, what would you title it, and what three headings would you use?

> What follow-up question would you want to ask Deepak Verma before your next check-in, based on this meeting?

> Rewrite the action items as a message you could post directly into a Teams chat.

## Remember

- No transcript, no recap. Copilot can only work from what was actually recorded or written down.
- A recap can sound complete while quietly filling a gap the meeting left open. Ask it to say "Not stated" instead of guessing.
- A date spoken in a meeting can differ from a date written in an older document. Notice the mismatch rather than picking one silently.
- You are responsible for what you send on from a recap. Check it against the source first.

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
