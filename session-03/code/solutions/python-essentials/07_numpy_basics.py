"""
Concept 7: NumPy basics

NumPy gives Python a fast, fixed-type array for numbers. It is the base
that most number-crunching libraries are built on.
Everyday example: a list holds a shopping basket of mixed things; a NumPy
array is a neat spreadsheet column of numbers you can do maths on all at once.

Setup (one time, not part of the standard library):
    pip install numpy          (or: pip install -r requirements.txt)

Run:  python 07_numpy_basics.py
"""

import numpy as np  # 'np' is the universal nickname

# ---------------------------------------------------------------
# 1. Why NumPy? Maths on a whole collection at once
# ---------------------------------------------------------------
prices = [100, 250, 80, 400]

# With a plain list, you must loop to add 10% tax.
with_tax_list = [round(p * 1.1, 2) for p in prices]

# With an array, the operation applies to every item at once. No loop.
prices_arr = np.array(prices)
with_tax = prices_arr * 1.1
print("List result :", with_tax_list)
print("Array result:", with_tax)

# Note: list * 2 repeats the list, array * 2 doubles every number.
print("[1, 2] * 2          =", [1, 2] * 2)
print("np.array([1, 2]) * 2 =", np.array([1, 2]) * 2)

# ---------------------------------------------------------------
# 2. Creating arrays
# ---------------------------------------------------------------
marks = np.array([42, 91, 67, 88, 73])
print("\nFrom a list:", marks)
print("Zeros       :", np.zeros(4))
print("Ones        :", np.ones(3))
print("Range       :", np.arange(0, 10, 2))  # start, stop, step
print("Evenly spaced:", np.linspace(0, 1, 5))  # 5 points from 0 to 1

# ---------------------------------------------------------------
# 3. Shape and type
# ---------------------------------------------------------------
# Every array has a single data type and a shape (its size in each direction).
print("\nShape:", marks.shape)  # (5,) means 5 items in one direction
print("Type :", marks.dtype)

# ---------------------------------------------------------------
# 4. Indexing and slicing: same as lists
# ---------------------------------------------------------------
print("\nFirst:", marks[0])
print("Last two:", marks[-2:])

# ---------------------------------------------------------------
# 5. Quick statistics
# ---------------------------------------------------------------
print("\nSum    :", marks.sum())
print("Mean   :", marks.mean())
print("Max    :", marks.max())
print("Min    :", marks.min())
print("Std dev:", round(marks.std(), 2))
print("Position of the max:", marks.argmax())

# ---------------------------------------------------------------
# 6. Filtering with conditions
# ---------------------------------------------------------------
# A comparison gives an array of True/False...
passed = marks >= 50
print("\nPassed mask:", passed)

# ...and using that mask as an index keeps only the True positions.
print("Passing marks:", marks[passed])
print("Count passing:", passed.sum())  # True counts as 1

# ---------------------------------------------------------------
# 7. Two dimensions: rows and columns
# ---------------------------------------------------------------
# A list of lists becomes a 2D array, like a table of numbers.
# Rows = students, columns = subjects.
scores = np.array([
    [90, 80, 70],
    [60, 75, 85],
    [88, 92, 79],
])
print("\nShape (rows, columns):", scores.shape)
print("Second student, third subject:", scores[1, 2])
print("First column (subject 1):", scores[:, 0])  # ':' means all rows

# axis=0 works down the columns, axis=1 works across the rows.
print("Average per subject:", scores.mean(axis=0))
print("Average per student:", scores.mean(axis=1))

# ---------------------------------------------------------------
# 8. Reshaping
# ---------------------------------------------------------------
numbers = np.arange(1, 7)  # [1 2 3 4 5 6]
print("\nOriginal:", numbers)
print("As 2 rows x 3 columns:\n", numbers.reshape(2, 3))

# ---------------------------------------------------------------
# 9. Combining arrays
# ---------------------------------------------------------------
# Arrays of the same shape can be added, multiplied, and so on, item by item.
a = np.array([1, 2, 3])
b = np.array([10, 20, 30])
print("\na + b =", a + b)
print("a * b =", a * b)

# The dot product multiplies item by item, then adds everything up:
# 1*10 + 2*20 + 3*30
print("dot   =", np.dot(a, b))

# Broadcasting: a single number is stretched to fit the array.
print("a + 100 =", a + 100)
