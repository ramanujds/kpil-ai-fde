"""
Concept 2: Tuples

A tuple is an ordered collection like a list, but it CANNOT be changed
after it is created.
Everyday examples: a map location (latitude, longitude), a colour
(red, green, blue), a date (day, month, year).

Use a list when the collection grows or changes.
Use a tuple when it is a fixed record.

Run:  python 02_tuples.py
"""

# ---------------------------------------------------------------
# 1. Creating a tuple
# ---------------------------------------------------------------
# Round brackets, items separated by commas.
location = (23.0225, 72.5714)  # (latitude, longitude)
print("Location:", location)

# The brackets are optional; the commas make the tuple.
colour = 255, 140, 0
print("Colour  :", colour)

# Gotcha: a tuple with ONE item needs a trailing comma.
not_a_tuple = (5)  # just the number 5 in brackets
one_item = (5,)  # a real tuple with one item
print("\n(5)  is", type(not_a_tuple).__name__)
print("(5,) is", type(one_item).__name__)

# ---------------------------------------------------------------
# 2. Indexing and slicing: same as lists
# ---------------------------------------------------------------
print("\nLatitude :", location[0])
print("Longitude:", location[1])
print("Last colour value:", colour[-1])
print("First two colour values:", colour[:2])

# ---------------------------------------------------------------
# 3. Tuples cannot be changed
# ---------------------------------------------------------------
# Lists allow location[0] = ..., tuples raise a TypeError.
# try/except lets us show the error without stopping the program.
try:
    location[0] = 19.0760
except TypeError as error:
    print("\nCannot change a tuple ->", error)

# To "change" a tuple, build a new one.
moved = (19.0760, location[1])
print("New tuple:", moved)
print("Old tuple:", location)

# ---------------------------------------------------------------
# 4. Unpacking: split a tuple into named variables
# ---------------------------------------------------------------
# One variable per item, in order. Far more readable than colour[0].
red, green, blue = colour
print(f"\nred={red}, green={green}, blue={blue}")

# Unpacking works in a swap too. No temporary variable needed.
a, b = 1, 2
a, b = b, a
print("After swap: a =", a, ", b =", b)

# Use * to grab "the rest". Handy when the length is not fixed.
first, *middle, last = (10, 20, 30, 40, 50)
print("first:", first, "| middle:", middle, "| last:", last)

# Use _ for a value you do not need.
_, longitude = location
print("Only longitude:", longitude)

# ---------------------------------------------------------------
# 5. Returning several values from a function
# ---------------------------------------------------------------
# A function can return a tuple; the caller unpacks it.
# (Functions are covered in detail in Concept 4.)
def min_and_max(numbers):
    return min(numbers), max(numbers)  # returns one tuple


lowest, highest = min_and_max([42, 91, 67, 88])
print(f"\nLowest={lowest}, Highest={highest}")

# ---------------------------------------------------------------
# 6. A list of tuples
# ---------------------------------------------------------------
# Each tuple is one fixed record: (name, marks).
students = [("Asha", 91), ("Ravi", 67), ("Meera", 88)]

# Unpack right in the for loop.
print("\nResults:")
for name, marks in students:
    print(f"  {name} scored {marks}")

# Sort by the second item (marks) using a key.
# lambda t: t[1] means "for each tuple t, look at t[1]".
ranked = sorted(students, key=lambda t: t[1], reverse=True)
print("Ranked:", ranked)

# ---------------------------------------------------------------
# 7. Handy tuple methods and conversions
# ---------------------------------------------------------------
letters = ("a", "b", "a", "c", "a")
print("\nCount of 'a':", letters.count("a"))
print("Position of 'c':", letters.index("c"))
print("Length:", len(letters))
print("'b' in tuple:", "b" in letters)

# Convert between the two when needed.
as_list = list(letters)  # now editable
as_list.append("d")
back_to_tuple = tuple(as_list)  # locked again
print("List :", as_list)
print("Tuple:", back_to_tuple)

# ---------------------------------------------------------------
# 8. List vs tuple at a glance
# ---------------------------------------------------------------
#   list   [ ]  changeable   grows and shrinks   a collection of similar things
#   tuple  ( )  fixed        same size forever   one record with different parts
