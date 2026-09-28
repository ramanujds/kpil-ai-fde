"""
Concept 1: Lists

A list is an ordered, changeable collection of items.
Everyday examples: a shopping list, a playlist, a queue of tasks,
the marks of a class.

Run:  python 01_lists.py
"""

# ---------------------------------------------------------------
# 1. Creating a list
# ---------------------------------------------------------------
# Square brackets, items separated by commas. Items can be any type.
fruits = ["apple", "banana", "mango"]
print("Fruits:", fruits)

# A list can be empty and filled later.
todo = []
print("Empty todo:", todo)

# ---------------------------------------------------------------
# 2. Indexing: picking one item
# ---------------------------------------------------------------
# Counting starts at 0. Negative numbers count from the end.
print("\nFirst fruit:", fruits[0])
print("Last fruit :", fruits[-1])

# ---------------------------------------------------------------
# 3. Slicing: picking a range
# ---------------------------------------------------------------
# list[start:stop] -> includes start, excludes stop.
print("\nFirst two:", fruits[0:2])

# fruits[-N:] means "the last N items".
print("Last two :", fruits[-2:])

# ---------------------------------------------------------------
# 4. Changing a list
# ---------------------------------------------------------------
# append -> add ONE item at the end
fruits.append("orange")

# extend -> add MANY items at the end
fruits.extend(["grapes", "papaya"])

# insert -> add at a given position (0 = the very front)
fruits.insert(0, "guava")

print("\nAfter changes:", fruits)
print("Number of items:", len(fruits))  # len = count

# pop -> remove and return an item (default: the last one)
removed = fruits.pop()
print("Removed:", removed)

# remove -> delete the first item that matches a value
fruits.remove("banana")
print("After removing banana:", fruits)

# ---------------------------------------------------------------
# 5. Looping over a list
# ---------------------------------------------------------------
print("\nAll fruits:")
for fruit in fruits:
    print("  -", fruit)

# enumerate gives you the position too. start=1 for human-friendly numbers.
print("\nNumbered:")
for number, fruit in enumerate(fruits, start=1):
    print(f"  {number}. {fruit}")

# ---------------------------------------------------------------
# 6. Checking membership
# ---------------------------------------------------------------
# 'in' answers: is this value inside the list?
if "mango" in fruits:
    print("\nMango is in the basket")
else:
    print("\nNo mango today")

# ---------------------------------------------------------------
# 7. List comprehension: build a new list from an old one
# ---------------------------------------------------------------
# Pattern: [what_to_keep for item in old_list if condition]
# Here: keep only the fruits whose name has more than 5 letters.
long_names = [f for f in fruits if len(f) > 5]
print("\nLong names:", long_names)

# Transform every item: make each name upper case.
shouting = [f.upper() for f in fruits]
print("Upper case:", shouting)

# ---------------------------------------------------------------
# 8. Sorting
# ---------------------------------------------------------------
marks = [42, 91, 67, 88]

# sorted() returns a NEW list; the original is untouched.
highest_first = sorted(marks, reverse=True)
print("\nHighest first:", highest_first)
print("Original     :", marks)

# marks.sort() would change the original list in place and return None.

# Top 2 marks: sort, then slice.
print("Top 2        :", highest_first[:2])

# ---------------------------------------------------------------
# 9. Gotcha: copying a list
# ---------------------------------------------------------------
# '=' does NOT copy a list. Both names point to the SAME list.
original = ["pen", "notebook"]
alias = original
alias.append("ruler")
print("\nOriginal changed too:", original)

# To get an independent copy, use .copy() (or a full slice [:]).
safe_copy = original.copy()
safe_copy.append("eraser")
print("Original untouched  :", original)
print("Copy                :", safe_copy)
