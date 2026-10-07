# Step 3 — Make the Sample Data

> Back to index · Previous: Start From the LlamaIndex App · Next: Load Markdown by Heading

## Goal

Create the five documents in `docs/`, and understand what each one is designed to test.

## Why this matters

A multi-format app is only convincing if the documents behave like real ones. These five
are small, synthetic and invented, but each one is built to make a different mistake
visible later:

| File | Format | Built to test |
|---|---|---|
| `employee_handbook.md` | Markdown | A heading-based split. Grades L1 to L5 are explained here |
| `onboarding_checklist.docx` | Word | Headings that live in styles, not in the text, and bullet lists |
| `travel_policy.pdf` | PDF, 3 pages | A document with no headings to split on. Rules such as "more than 25,000 INR" need approval |
| `expense_limits.xlsx` | Excel, 2 sheets | Table rows full of exact codes: "L3", 6000. The PDF points to this file for the money limits |
| `hr_faq.csv` | CSV | Question and answer rows, worded differently from the policies |

Note the link between two of them. The PDF says that hotel limits "depend on grade and are
kept in the Expense Limits workbook". A question such as "I am an L3 and my hotel cost
7,000 INR a night. What happens?" needs the limit from the spreadsheet and the rule from the
PDF. A good multi-format app must be able to use both in one answer.

## 1. Type the Markdown and CSV Files

These two are short and plain text, so type or paste them. The full contents are in the
checkpoint at the end of this step.

Create `docs/employee_handbook.md`, with a title, three labelled lines and six `##`
sections: About This Handbook, Working Hours, Grades and Levels, Performance Reviews, Code of
Conduct, and Resignation and Notice Period.

Create `docs/hr_faq.csv`, with the header `question,answer,category` and twelve rows.

## 2. Copy the Generator for the Other Three

The PDF, Excel and Word files are binary. You cannot type them, so a script writes them.
Copy `make_sample_data.py` from the checkpoint into the project folder. It is about 200
lines of `reportlab`, `openpyxl` and `python-docx`. It is not part of the lesson, so show it
rather than type it.

What is worth pointing out in it:

| Part | What to notice |
|---|---|
| `make_travel_policy_pdf` | Page breaks put three pages of numbered sections in the PDF. Nothing marks a heading except its look |
| `make_expense_limits_xlsx` | Two sheets, with a header row each. Grade is the first column |
| `make_onboarding_docx` | `add_heading` gives real Word heading styles, `style="List Bullet"` gives real bullets |

## Try it

```bash
uv run make_sample_data.py
ls docs
```

```text
Wrote travel_policy.pdf, expense_limits.xlsx and onboarding_checklist.docx to docs/.
employee_handbook.md
expense_limits.xlsx
hr_faq.csv
onboarding_checklist.docx
travel_policy.pdf
```

Peek into the workbook without opening Excel:

```bash
uv run python -c "
from openpyxl import load_workbook
for sheet in load_workbook('docs/expense_limits.xlsx').worksheets:
    print(sheet.title)
    for row in sheet.iter_rows(values_only=True):
        print('  ', row)
"
```

```text
Travel Limits
   ('Grade', 'Hotel Limit Per Night (INR)', 'Meal Allowance Per Day (INR)', 'Local Travel Per Day (INR)', 'Flight Class')
   ('L1', 3500, 800, 600, 'Economy')
   ('L2', 4500, 1000, 800, 'Economy')
   ('L3', 6000, 1500, 1200, 'Economy')
   ('L4', 8000, 2000, 1800, 'Premium Economy')
   ('L5', 12000, 2500, 2500, 'Business')
Leave Entitlement
   ('Grade', 'Paid Leave Days Per Year', 'Sick Leave Days Per Year', 'Casual Leave Days Per Year', 'Max Carry Forward Days')
   ('L1', 12, 8, 5, 6)
   ('L2', 14, 8, 5, 7)
   ('L3', 16, 8, 6, 8)
   ('L4', 18, 10, 6, 10)
   ('L5', 20, 10, 8, 12)
```

Look at that output with the next steps in mind: the header row names every column, and
each later row means nothing without it.

## Checkpoint

<details>
<summary>Full <code>docs/employee_handbook.md</code></summary>

```markdown
# Employee Handbook
Department: HR
Version: 2025

## About This Handbook
This handbook describes how people work at Acme, a fictional company used for training. It applies to every employee. Where a separate policy exists, such as the travel policy, that policy decides the details.

## Working Hours
The standard working week is Monday to Friday, 9:30 AM to 6:00 PM, with a 45 minute lunch break. Employees may start between 8:30 AM and 10:30 AM if they complete the same number of hours and are available for the core hours of 11:00 AM to 4:00 PM. Working on a public holiday needs written approval from the department head and earns a compensatory day off.

## Grades and Levels
Acme uses five grades, L1 to L5. L1 is a graduate or trainee role. L2 is an associate. L3 is a senior associate. L4 is a lead or manager. L5 is a director or above. Grade decides travel limits, leave entitlement and approval authority. Promotion from one grade to the next is decided once a year during the April review cycle.

## Performance Reviews
Performance is reviewed twice a year, in October for a mid-year check-in and in April for the annual review. Each review has a self assessment, a manager assessment and a calibration meeting. Ratings are on a scale of 1 to 5. A rating of 4 or above in the annual review makes an employee eligible for promotion and for the annual bonus.

## Code of Conduct
Employees are expected to treat colleagues, vendors and visitors with respect. Harassment of any kind is not tolerated and can be reported to the HR helpdesk or to the internal committee, in confidence. Gifts from vendors worth more than 2,000 INR must be declared to the manager and may need to be returned.

## Resignation and Notice Period
An employee who resigns must give written notice in the HR portal. The notice period is 30 days for L1 and L2, 60 days for L3 and L4, and 90 days for L5. The company can waive part of the notice period. Final settlement is paid within 45 days of the last working day.
```

</details>

<details>
<summary>Full <code>docs/hr_faq.csv</code></summary>

```text
question,answer,category
How do I reset my HR portal password?,Use the Forgot Password link on the HR portal login page. A reset link is sent to your company email and stays valid for 30 minutes.,Portal
Where can I download my payslip?,Payslips are in the HR portal under Payroll > My Payslips. Each payslip is available from the 3rd working day of the following month.,Payroll
When is salary credited?,Salary is credited on the last working day of each month.,Payroll
How do I update my bank account details?,Submit the new details with a cancelled cheque in the HR portal under Payroll > Bank Details. Changes made before the 20th apply to that month's salary.,Payroll
Can I work from another city for a few weeks?,Work from another city for up to 15 working days in a year is allowed with manager approval. Longer stays need the department head's approval and HR must be informed for tax reasons.,Work Arrangement
How do I add a family member to my health insurance?,You can add a spouse and children within 30 days of marriage or birth through the HR portal under Benefits > Insurance. Additions after 30 days wait for the annual enrolment window in April.,Benefits
Who do I contact about a harassment complaint?,Write to the HR helpdesk or to the internal committee. Complaints are handled in confidence and you will get an acknowledgement within 2 working days.,Conduct
Is there a referral bonus?,Yes. An employee whose referred candidate joins and completes 6 months gets a referral bonus of 15000 INR. Referrals for L4 and L5 roles earn 30000 INR.,Benefits
How do I get an experience or relieving letter?,The letter is issued within 10 working days of the final settlement. Request it in the HR portal under Exit > Documents.,Exit
What is the dress code?,Business casual on weekdays. Casual wear is allowed on Fridays unless you are meeting a client.,Conduct
How do I apply for a transfer to another department?,"Discuss it with your manager first. Then raise an internal transfer request in the HR portal. Both department heads must approve, and you must have completed 12 months in your current role.",Career
Can I claim for a training course I paid for myself?,Yes. Courses related to your role are reimbursed up to 25000 INR per year with manager approval before enrolment. Submit the certificate and receipt within 30 days of completion.,Benefits
```

</details>

<details>
<summary>Full <code>make_sample_data.py</code></summary>

```python
"""Writes the PDF, Excel and Word sample files into docs/. Everything in them is made up.

Run it only if you want to regenerate those files: uv run make_sample_data.py
"""
from pathlib import Path

from docx import Document
from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

DOCS = Path("docs")
DOCS.mkdir(exist_ok=True)


# ---- PDF: a travel policy, three pages, no markdown headings to split on ----

def make_travel_policy_pdf():
    styles = getSampleStyleSheet()
    story = []

    def heading(text):
        story.append(Paragraph(text, styles["Heading2"]))

    def para(text):
        story.append(Paragraph(text, styles["BodyText"]))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Acme Business Travel Policy", styles["Title"]))
    para("Department: Finance and Admin. Version 2025. Effective 1 April 2025.")

    heading("1. Purpose and Scope")
    para(
        "This policy explains how employees book, approve and claim for business travel. "
        "It applies to all grades, L1 to L5, for travel inside India and abroad. Travel that is "
        "paid for by a client is outside this policy unless the client contract says otherwise. "
        "The money limits that depend on grade, such as the hotel limit per night and the daily "
        "meal allowance, are kept in the Expense Limits workbook and not repeated here."
    )
    heading("2. Booking Flights and Trains")
    para(
        "All tickets must be booked through the company travel desk in the Admin portal. Tickets "
        "booked directly by the employee are reimbursed only if the travel desk could not offer "
        "the same journey, and a screenshot of the desk's reply must be attached to the claim. "
        "Book at least 7 days before the travel date, because fares rise sharply close to departure."
    )
    para(
        "Trains are the default choice for journeys under 6 hours, for example Ahmedabad to Mumbai. "
        "Air travel is allowed for longer journeys or when a train is not available on the required "
        "day. The class of travel depends on grade and is listed in the Expense Limits workbook. "
        "Business class is only available to L5, or to anyone on a flight longer than 6 hours when "
        "the department head has approved it in advance."
    )
    story.append(PageBreak())

    heading("3. Pre-Approval of Trips")
    para(
        "Every trip needs the reporting manager's approval in the Admin portal before booking. "
        "A trip needs the additional approval of the department head if it is longer than 3 nights "
        "or if the estimated cost is more than 25,000 INR. Pre-approval requests for these trips "
        "must be raised at least 5 working days before departure."
    )
    para(
        "International travel always needs the approval of the department head and the finance "
        "controller, whatever the cost. The traveller must also carry a valid passport and visa and "
        "register the trip with the Admin desk so that travel insurance can be arranged. Approval "
        "is not needed again for a change of dates, but a change of destination needs a new request."
    )
    heading("4. Hotels and Local Travel")
    para(
        "Hotels must be booked through the travel desk. The maximum rate per night depends on grade "
        "and is listed in the Expense Limits workbook. A stay above the limit needs the department "
        "head's approval before booking, and the extra amount is otherwise recovered from the "
        "employee. In cities where a company guest house is available, employees are expected to use "
        "it instead of a hotel."
    )
    para(
        "For local travel, employees can claim metro, bus, auto-rickshaw and app-cab fares up to the "
        "daily local travel limit for their grade. Car rental for a whole day needs the manager's "
        "approval. Personal vehicle use is reimbursed at 9 INR per kilometre for a car and 4 INR per "
        "kilometre for a two-wheeler, with a trip log attached."
    )
    story.append(PageBreak())

    heading("5. Claiming Travel Expenses")
    para(
        "A travel claim must be submitted in the Finance portal within 10 working days of returning "
        "from the trip. Claims submitted later are paid only with the approval of the finance "
        "controller. Every claim needs the original ticket or boarding pass, the hotel invoice, and "
        "receipts for any single expense above 500 INR. Meals are paid as a fixed daily allowance and "
        "need no receipts."
    )
    para(
        "Advance payments are available for trips longer than 3 nights. The advance can be up to 70 "
        "percent of the estimated cost and must be settled within 10 working days of the trip. An "
        "unsettled advance is deducted from the next month's salary."
    )
    heading("6. Non-Reimbursable Items")
    para(
        "The company does not reimburse minibar and alcohol charges, laundry for trips shorter than "
        "5 nights, personal entertainment, traffic fines, or the cost of upgrading a ticket or room "
        "above the entitlement of the employee's grade, unless the upgrade was approved in advance."
    )
    heading("7. Exceptions")
    para(
        "Exceptions to this policy can be approved by the finance controller in writing. The employee "
        "should explain why the policy could not be followed and attach any supporting email. An "
        "exception approved once does not set a precedent for later trips."
    )

    SimpleDocTemplate(str(DOCS / "travel_policy.pdf"), pagesize=A4, title="Acme Business Travel Policy").build(story)


# ---- Excel: two sheets of limits and entitlements by grade ----

def make_expense_limits_xlsx():
    wb = Workbook()

    travel = wb.active
    travel.title = "Travel Limits"
    travel.append(["Grade", "Hotel Limit Per Night (INR)", "Meal Allowance Per Day (INR)",
                   "Local Travel Per Day (INR)", "Flight Class"])
    for row in [
        ("L1", 3500, 800, 600, "Economy"),
        ("L2", 4500, 1000, 800, "Economy"),
        ("L3", 6000, 1500, 1200, "Economy"),
        ("L4", 8000, 2000, 1800, "Premium Economy"),
        ("L5", 12000, 2500, 2500, "Business"),
    ]:
        travel.append(row)

    leave = wb.create_sheet("Leave Entitlement")
    leave.append(["Grade", "Paid Leave Days Per Year", "Sick Leave Days Per Year",
                  "Casual Leave Days Per Year", "Max Carry Forward Days"])
    for row in [
        ("L1", 12, 8, 5, 6),
        ("L2", 14, 8, 5, 7),
        ("L3", 16, 8, 6, 8),
        ("L4", 18, 10, 6, 10),
        ("L5", 20, 10, 8, 12),
    ]:
        leave.append(row)

    for sheet in (travel, leave):
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        for column in "ABCDE":
            sheet.column_dimensions[column].width = 30

    wb.save(DOCS / "expense_limits.xlsx")


# ---- Word: an onboarding checklist with real heading styles ----

def make_onboarding_docx():
    doc = Document()
    doc.add_heading("New Joiner Onboarding Checklist", level=1)
    doc.add_paragraph("Department: HR. This checklist is shared with every new joiner and their manager.")

    doc.add_heading("Before Day One", level=2)
    for item in [
        "HR sends the offer documents and a list of papers to bring: ID proof, address proof, and the relieving letter from the previous employer.",
        "IT prepares a laptop and a company email account. The laptop is collected from the IT desk on the first morning.",
        "The manager nominates a buddy from the same team.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("Day One", level=2)
    for item in [
        "Report to reception by 9:30 AM and collect the access card.",
        "Complete the HR induction, which covers the employee handbook, the code of conduct and the leave policy.",
        "Set up the laptop with the IT desk, including multi-factor authentication and the VPN.",
        "Have lunch with the buddy and the team.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("First Week", level=2)
    for item in [
        "Finish the mandatory online courses on information security and prevention of harassment within 5 working days.",
        "Meet the manager to agree the goals for the first 90 days.",
        "Submit bank details and nominee details in the HR portal so that the first salary is not delayed.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("First Month", level=2)
    for item in [
        "Add family members to the health insurance within 30 days of joining.",
        "Attend the monthly new joiner session with the HR head.",
        "Complete the probation goal-setting form. Probation lasts 6 months and is reviewed at 3 and 6 months.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("Who to Contact", level=2)
    doc.add_paragraph(
        "For HR questions, write to the HR helpdesk. For laptop, email or access problems, raise a "
        "ticket with the IT desk. For travel and expense questions, contact Finance and Admin."
    )

    doc.save(DOCS / "onboarding_checklist.docx")


if __name__ == "__main__":
    make_travel_policy_pdf()
    make_expense_limits_xlsx()
    make_onboarding_docx()
    print("Wrote travel_policy.pdf, expense_limits.xlsx and onboarding_checklist.docx to docs/.")
```

</details>

These match the reference project's files exactly. The generated PDF, Excel and Word files
carry timestamps, so their bytes can differ from the reference while their content is the
same.

## Common Mistakes

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'reportlab'` | The `dev` group was not installed | Run `uv sync` without `--no-dev` |
| One FAQ answer is cut short in Step 7, and its category looks like a sentence | An answer that contains a comma was not wrapped in double quotes, so the CSV reader split it into an extra column | Put double quotes around any answer that contains a comma, as the transfer question's answer does in the checkpoint |
| `docs/` has the old Markdown policies | The `docs/*` removal in Step 2 was skipped | Delete them, so the app does not mix the two sets |
| The PDF has one page | The two `PageBreak` lines were left out when copying | Copy the generator again from the checkpoint |

Next: **Step 4 — Load Markdown by Heading**.
