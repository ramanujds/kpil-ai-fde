"""
Concept 8: pandas basics

pandas gives Python a DataFrame: a table with named columns, like an
Excel sheet you can control with code. It is built on NumPy.
Everyday example: a class register with one row per student and one
column per detail.

Setup (one time, not part of the standard library):
    pip install pandas         (or: pip install -r requirements.txt)

Run:  python 08_pandas_basics.py
"""

from io import StringIO  # lets us treat a string like a file, no real file needed

import pandas as pd  # 'pd' is the universal nickname

# ---------------------------------------------------------------
# 1. Creating a DataFrame
# ---------------------------------------------------------------
# From a list of dicts (Concept 3): one dict per row, keys become columns.
df = pd.DataFrame([
    {"name": "Asha", "city": "Ahmedabad", "marks": 91},
    {"name": "Ravi", "city": "Surat", "marks": 67},
    {"name": "Meera", "city": "Ahmedabad", "marks": 88},
    {"name": "Kabir", "city": "Surat", "marks": 54},
    {"name": "Divya", "city": "Vadodara", "marks": 73},
])
print(df)

# ---------------------------------------------------------------
# 2. Looking at the data
# ---------------------------------------------------------------
print("\nShape (rows, columns):", df.shape)
print("Columns:", list(df.columns))
print("\nFirst 2 rows:\n", df.head(2))
print("\nQuick statistics:\n", df.describe())

# ---------------------------------------------------------------
# 3. Selecting columns
# ---------------------------------------------------------------
# One column gives a Series (a single labelled column).
print("\nMarks column:\n", df["marks"])

# A list of names gives a smaller DataFrame.
print("\nName and marks:\n", df[["name", "marks"]])

# A Series knows the same statistics tricks as NumPy.
print("\nAverage marks:", df["marks"].mean())
print("Highest marks:", df["marks"].max())

# ---------------------------------------------------------------
# 4. Filtering rows
# ---------------------------------------------------------------
# Same idea as a NumPy mask: a condition picks the rows to keep.
toppers = df[df["marks"] >= 80]
print("\nMarks 80 or more:\n", toppers)

# Combine conditions with & (and) or | (or), each in brackets.
surat_passed = df[(df["city"] == "Surat") & (df["marks"] >= 60)]
print("\nSurat and passing:\n", surat_passed)

# ---------------------------------------------------------------
# 5. Adding a column
# ---------------------------------------------------------------
# Maths on a column applies to every row, no loop needed.
df["marks_plus_5"] = df["marks"] + 5  # e.g. a grace-marks column
df["result"] = df["marks"].apply(lambda m: "Pass" if m >= 60 else "Fail")
print("\nWith new columns:\n", df)

# ---------------------------------------------------------------
# 6. Sorting
# ---------------------------------------------------------------
ranked = df.sort_values("marks", ascending=False)
print("\nRanked:\n", ranked[["name", "marks"]])

# ---------------------------------------------------------------
# 7. Grouping and counting
# ---------------------------------------------------------------
# groupby splits rows into groups, then summarises each group.
print("\nAverage marks per city:\n", df.groupby("city")["marks"].mean())
print("\nStudents per city:\n", df["city"].value_counts())

# ---------------------------------------------------------------
# 8. Missing values
# ---------------------------------------------------------------
# Real data has gaps. pandas marks them as NaN ("not a number").
gappy = pd.DataFrame({"name": ["Asha", "Ravi", "Meera"], "marks": [91, None, 88]})
print("\nWith a gap:\n", gappy)
print("Missing per column:\n", gappy.isna().sum())

print("\nFilled with 0:\n", gappy.fillna(0))
print("\nRows with gaps dropped:\n", gappy.dropna())

# ---------------------------------------------------------------
# 9. Reading and writing CSV
# ---------------------------------------------------------------
# CSV is the most common way tables are shared.
# Here a string stands in for a file so the example needs no extra files.
csv_text = """name,marks
Asha,91
Ravi,67
"""
from_csv = pd.read_csv(StringIO(csv_text))
print("\nRead from CSV:\n", from_csv)

# With a real file you would write: pd.read_csv("students.csv")
# and save with:                    df.to_csv("out.csv", index=False)
print("\nAs CSV text:\n", from_csv.to_csv(index=False))

# ---------------------------------------------------------------
# 10. Back to plain Python
# ---------------------------------------------------------------
# Convert rows back into a list of dicts (Concept 3) whenever you need to.
records = df[["name", "marks"]].to_dict(orient="records")
print("As list of dicts:", records[:2])
