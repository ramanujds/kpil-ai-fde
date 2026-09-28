# Copilot in Excel: Facilitator Key

**AI Developer & FDE Training | Kalpataru Projects, Ahmedabad**
Day 2, Block 3: Excel | For the trainer only. Do not share with trainees before the exercise.

> Scope note: this key lists the planted problems in the raw file, the planted patterns in the data and the correct answers to the exercise questions. All figures were calculated from the clean file and are for the synthetic FreshCart data only. Copilot output varies between runs and versions; the "watch for" items describe common problems, not guaranteed ones.

---

## How the Two Files Relate

| File | Content |
|---|---|
| FreshCart_Orders_Raw.xlsx | Sheet "Orders Export": 200 orders with the problems below, plus 2 duplicate rows, blank rows, a total row and a note row |
| FreshCart_Orders_Clean.xlsx | Sheet "Orders": the same 200 orders in an Excel table named OrdersTable (A1:J201), all problems fixed |

Fixes in the clean file compared with the raw file: text dates converted to real dates, "Rs" text values converted to numbers, labels standardised, duplicates removed, the value typo corrected, and title, group-header, blank, total and note rows removed. The 5 missing delivery times were left blank; they were not estimated.

## Planted Problems in the Raw File

| Problem | Where | Count or location |
|---|---|---|
| Title and subtitle rows above the data, merged across A to J | Rows 1 and 2 | 2 merged ranges |
| Group headers merged across columns (Order Details, Product, Basket, Delivery) | Row 4 | 4 merged ranges; the real headers are in row 5 |
| Dates stored as text in mixed formats (14/08/2025, 2025-08-14, Aug 14, 2025) | Order Date column | 52 of 200 orders; the rest are real dates |
| Order values stored as text, such as "Rs 1,250" | Order Value column | 42 orders |
| Category labels inconsistent (dairy, DAIRY, "Dairy " with a trailing space, Fruits, Vegetable, bakery) | Category column | 32 orders |
| Supplier names inconsistent (Coastal Dairy, Harvest Ridge) | Supplier column | 10 orders |
| On Time recorded as Y, N, yes as well as Yes and No | On Time column | 29 orders |
| Duplicate order rows | FC-10041 (rows 46 and 47) and FC-10121 (rows 128 and 129) | 2 duplicates |
| Blank rows inside the data | Rows 68 and 140 | 2 rows; row 210 is also blank, above the total |
| Value typo: FC-10066 has 53,000 instead of 530 | Row 73, West zone bakery order, 6 August | 1 order |
| Missing delivery time and On Time | FC-10002, FC-10061, FC-10086, FC-10151, FC-10164 | 5 orders |
| Typed total that includes duplicates and the typo | Row 211, Order Value column: 155,350 | Text values are not included in it, so it is wrong in two ways |
| Note row under the total | Row 212 | 1 row |

## Planted Patterns in the Data

| Pattern | Evidence in the clean file |
|---|---|
| Fruit orders are late on Mondays and Fridays | Fruit on-time is 50.0% on Monday and Friday (14 orders with a recorded time) versus 92.6% on other days (27 orders); this mirrors the single-vehicle problem in the Q3 report |
| Dairy complaints spike after the 14 August cold-chain incident | 13 to 17 August: 10 dairy orders, 6 with complaints. Other dairy orders: 46, with 2 complaints (4.3%) |
| West zone is slower | Average delivery time in West is 79.4 minutes; the other zones range from 68.6 to 74.2 |
| Order volume rises across the quarter | 55 orders in July, 72 in August, 73 in September; average orders per day about 1.8, 2.3 and 2.4 |

## Correct Answers (Clean File)

| Question | Answer |
|---|---|
| Number of orders | 200 |
| Total order value | Rs 129,910 |
| Overall on-time rate | 86.2% (168 of 195 orders with a delivery time). If the 5 blanks are counted as not on time, 84.0% (168 of 200) |
| Late orders | 27 of 195 with a delivery time |
| Complaints, total | 16 |
| Average order value | Rs 649.6 |

| Category | Orders | On-time rate | Complaints | Average delivery minutes |
|---|---|---|---|---|
| Bakery | 47 | 91.3% | 2 | 68.9 |
| Dairy | 56 | 81.5% | 8 | 75.5 |
| Fruit | 42 | 78.0% | 2 | 77.6 |
| Vegetables | 55 | 92.6% | 4 | 70.5 |

| Zone | Average delivery minutes |
|---|---|
| Central | 71.6 |
| East | 74.2 |
| North | 73.1 |
| South | 68.6 |
| West | 79.4 |

Late deliveries by weekday: Monday 6, Tuesday 4, Wednesday 4, Thursday 4, Friday 5, Saturday 2, Sunday 2.

## What to Watch For

| Exercise | Good result | Watch for |
|---|---|---|
| A1: question on raw data | Copilot asks for a table, refuses or gives an unreliable answer | An answer that looks confident but ignores text values or merged headers; trainees accepting it |
| A2: problem review | Finds merged cells, mixed date formats, text numbers, label variants, duplicates, blanks | Missing the value typo (53,000) or the mixed date formats; not being able to see rows beyond the visible window |
| A4: helper columns | New columns with visible formulas; original data untouched | Overwriting original columns; misreading dd/mm/yyyy text dates as mm/dd (3 July read as 7 March) |
| B1 to B4 | Figures match the tables above | Averages that include or exclude blanks without saying so; on-time rate of 84.0% or 86.2% depending on treatment |
| B5 | Says 5 orders lack a delivery time and states how it treated them | A confident rate with no mention of the blanks |
| C1: trends | Identifies Fruit on Monday and Friday, the mid-August dairy complaints, West zone and rising volume | Generic statements with no numbers; confusing counts with rates |
| C2 | Fruit late deliveries cluster on Monday and Friday | Weekday derived incorrectly |
| C3 | Dairy, 13 to 17 August | Reporting category totals only, not the dates |
| C5 | Reasons clearly labelled as guesses | Stating causes as facts, such as "the supplier had a cooling failure", which the data does not show |
| D1 to D4 | Working formulas the trainee can read | Formulas that return errors on blank delivery times; explanations that do not match the formula |
| E1 to E3 | Correct charts with titles and labels | Charts that use a truncated axis; a chart based on the wrong column; too many series |

## Talking Points When Trainees Compare Answers

1. Ask two trainees who got different on-time rates how they each handled the blanks. Neither is wrong; the choice must be stated.
2. Point out that the raw data would have given a wrong answer with total confidence. Ask what the cost would be if that number went into a report.
3. Contrast C1 with C5: what the data shows against what someone guesses. Ask what evidence would confirm the dairy incident as the cause.
4. Ask trainees which of Copilot's answers they would still want to verify with a filter or COUNTIF before sharing it.

---

*Prepared for Kalpataru Projects | AIM ADaSci | Confidential*
