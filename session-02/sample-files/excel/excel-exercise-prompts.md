# Copilot in Excel: Exercise Handout

**AI Developer & FDE Training | Kalpataru Projects, Ahmedabad**
Day 2, Block 3: Excel | 35 minutes

In this exercise you will prepare a messy data export so Copilot can work with it, then use Copilot in Excel to ask questions, spot trends, add formulas, highlight rows and build charts. You will work with two sample files about FreshCart, a made-up grocery delivery business. The business, orders and numbers are all fictional.

By the end you will be able to:

1. Recognise what makes a spreadsheet hard for Copilot to use, and fix it
2. Ask questions of your data in plain language
3. Ask Copilot to explain trends and patterns, and tell facts apart from guesses
4. Get help with formulas, highlighting and charts
5. Check a Copilot answer against the data before you rely on it

---

## Before You Start

- Sign in to Excel with your work account and confirm you can see the Copilot button on the Home tab.
- Open the sample files from the folder your trainer shares with you.
- Copilot in Excel works best when your data is an Excel table and the file is saved in OneDrive or SharePoint with AutoSave switched on. If Copilot cannot see your data, check these two things first.
- Before you change anything, use "Save As" to keep a copy of the original file.
- Use only these sample files. Do not paste real company data into Copilot during this exercise.
- Your screen may look slightly different from a colleague's. Button names change between versions, so look for the Copilot icon rather than an exact menu path.
- Copilot gives a different answer each time, and it cannot always do what you ask. When it cannot, note what it said; that is a useful result.
- Work in pairs if you can: one person types the prompts, the other checks every answer. Swap halfway.

## The Sample Files

| File | What it is | Used in |
|---|---|---|
| FreshCart_Orders_Raw.xlsx | A sample of 200 orders, exported from an operations system as it came | Exercise A |
| FreshCart_Orders_Clean.xlsx | The same 200 orders, already prepared as an Excel table | Exercises B to E |

If you run short of time in Exercise A, move on and use the clean file for the rest.

## About the Data

Each row is one customer order for one main product category. The columns are:

| Column | Meaning |
|---|---|
| Order ID | Unique order number |
| Order Date | Date the order was placed, 1 July to 30 September |
| Zone | Delivery zone: Central, North, South, East or West |
| Category | Main product category: Vegetables, Dairy, Bakery or Fruit |
| Supplier | The supplier that provided the category |
| Items | Number of items in the basket |
| Order Value (Rs) | Order value in rupees |
| Delivery Minutes | Minutes from order to delivery |
| On Time | Yes if delivered within 90 minutes, otherwise No |
| Complaint | Yes if the customer complained about the order |

## How to Write a Good Prompt

Use the same four parts as in the Word and PowerPoint exercises.

| Part | Question it answers | Example |
|---|---|---|
| Goal | What do I want? | "Show the on-time rate for each category" |
| Context | What is this data, and why do I ask? | "This is a sample of delivery orders; I want to find weak spots" |
| Source | What should Copilot use? | "Use only the OrdersTable" |
| Expectations | What shape do I want back? | "A table, sorted lowest to highest, with percentages to one decimal place" |

For data questions, name the columns you mean and say how you want the answer shown.

## Suggested Timing

| Step | Minutes |
|---|---|
| Trainer demonstration | 3 |
| A. Prepare the data | 9 |
| B. Ask questions of your data | 5 |
| C. Explain trends and patterns | 6 |
| D. Formulas and highlighting | 4 |
| E. Charts | 4 |
| F. Check before you rely on it | 4 |

---

## Exercise A: Prepare the Data

Open FreshCart_Orders_Raw.xlsx.

**Step 1: See what happens**

Ask Copilot a simple question before you touch the data.

> What is the average delivery time for each category?

Note what Copilot says. Does it give an answer? Does it ask you to do something first?

**Step 2: Find the problems**

> Review this sheet and list anything that would make analysis unreliable. Group the problems under these headings: Layout and Headers, Dates, Numbers Stored as Text, Inconsistent Labels, Duplicates, Blanks, and Unusual Values. Do not change anything.

Then look through the sheet yourself. Scroll to the top, the bottom and the middle. Did Copilot find everything you found?

**Step 3: Fix the layout first**

Copilot works with tables, so the sheet must have one row of headers followed by clean rows of data. Use this guide.

| Type of problem | How to spot it | Ways to fix it |
|---|---|---|
| Titles and merged cells above the data | Text above the column headers; cells that span several columns | Unmerge the cells, delete rows so the headers are the first row |
| Blank rows and totals inside the data | Gaps in the list; a total or note under the data | Delete them; totals can be recalculated later |
| Not an Excel table | No filter buttons on the header row | Click inside the data and press Ctrl+T, tick "My table has headers" |

**Step 4: Fix the data with Copilot's help**

Try these prompts on your new table. Copilot usually adds a new helper column instead of changing your original, which is safer.

> Add a column that converts the Order Date values into real Excel dates. Keep the original column.

> Add a column that cleans the Category values: remove extra spaces and make the capitalisation consistent. Treat "Fruits" as "Fruit" and "Vegetable" as "Vegetables".

> Add a column that turns Order Value into a number, removing "Rs" and commas where they appear.

> Highlight any duplicate Order IDs.

> Which order values look unusually high or low compared with the rest? List them.

You do not need to fix everything in the time available. Fix the layout and two or three data problems, then note what is left and switch to the clean file for the rest of the exercise.

**Think about it:** Which problems did Copilot spot quickly, and which did it miss? What would have happened if you had asked your question about the raw data and believed the answer?

---

## Exercise B: Ask Questions of Your Data

Open FreshCart_Orders_Clean.xlsx.

**Prompt B1**

> How many orders are there, and what is their total order value in rupees?

**Prompt B2**

> What is the on-time delivery rate for each category? Show a table sorted from lowest to highest, with percentages to one decimal place.

**Prompt B3**

> Which zone has the longest average delivery time? Show all five zones.

**Prompt B4**

> How many complaints were there in each category?

**Prompt B5**

> How many orders have no delivery time recorded, and how did you handle them when you worked out the on-time rate?

**Think about it:** Copilot must make choices, such as what to do with blank cells. Does it tell you what it chose? Would a different choice change the answer?

---

## Exercise C: Explain Trends and Patterns

Stay in FreshCart_Orders_Clean.xlsx.

**Prompt C1**

> Describe the main trends in this data in five bullet points. Give the numbers behind each one.

**Prompt C2**

> Is there a pattern in late deliveries by day of the week for Fruit orders? Show the numbers.

**Prompt C3**

> Were there any unusual spikes in complaints? Tell me which category and which dates.

**Prompt C4**

> Are orders increasing, decreasing or staying flat over the quarter? Show the number of orders per month.

**Prompt C5**

> Suggest three possible reasons for what you found. Label each one clearly as a guess, not a fact.

**Think about it:** Which of Copilot's statements come directly from the numbers, and which are interpretation? What extra information would you need to confirm the reasons?

---

## Exercise D: Formulas and Highlighting

Stay in FreshCart_Orders_Clean.xlsx.

**Prompt D1**

> Add a column called Weekday that shows the day name for each Order Date.

**Prompt D2**

> Add a column called Late Minutes that shows how many minutes over 90 the delivery took, or 0 if it was on time or has no delivery time.

**Prompt D3**

> Highlight in red every row where On Time is No and Complaint is Yes.

**Prompt D4**

> Explain in plain English how the formula in the Late Minutes column works.

**Think about it:** Click a cell in each new column and read the formula. Could you have written it yourself? Would you know what to do if it gave the wrong answer?

---

## Exercise E: Charts

Stay in FreshCart_Orders_Clean.xlsx.

**Prompt E1**

> Create a column chart of the average delivery time in minutes for each category. Add a clear title and axis labels.

**Prompt E2**

> Create a line chart of the number of orders per week. Add a title and label the axes.

**Prompt E3**

> Create a chart that compares the on-time rate for Fruit orders on each day of the week.

**Think about it:** Look at each chart against the numbers you found earlier. Does the chart start its axis at zero? Would a busy manager read the right message from it?

---

## Exercise F: Check Before You Rely on It

Use this checklist on every Copilot answer you plan to use. It is the same habit you will use for real work data.

| Check | Done |
|---|---|
| I checked at least one number myself, for example with a filter or a simple COUNTIF | |
| I know how Copilot treated blank cells and unusual values | |
| The category and column names used in the answer match my data | |
| I can read and explain each formula Copilot added | |
| My original data is unchanged and I have a saved copy | |
| Each chart matches the numbers, with a clear title and honest axes | |
| I have separated what the numbers show from what someone guesses | |
| I have looked at the whole result myself | |

If you cannot tick a box, check the data, correct the result or ask Copilot to explain, then check again.

---

## Your Notes

Write down what you found. Your trainer will ask a few of you to share.

| Question | My answer |
|---|---|
| Which problem in the raw data would have caused the biggest mistake? | |
| Which question gave the most useful answer? | |
| Where did Copilot make a choice or an assumption I would want to know about? | |
| One spreadsheet from my own work I could try this on | |

## Stretch Prompts

If you finish early, try these on FreshCart_Orders_Clean.xlsx.

- "Create a summary table with one row per supplier showing orders, on-time rate, complaints and average order value."
- "Which combination of category and zone has the lowest on-time rate? Show the top three."
- "Suggest three questions I should ask about this data next, and explain why."
- "Add a slicer or filter so I can look at one zone at a time."

## Remember

- Copilot works only as well as the table you give it. Prepare the data first.
- It sounds sure of itself even when it has made a choice you did not intend. Ask what it did with blanks, duplicates and unusual values.
- Numbers explain what happened; they do not explain why. Keep facts and guesses separate.
- You are responsible for the numbers you share. Check them first.

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
