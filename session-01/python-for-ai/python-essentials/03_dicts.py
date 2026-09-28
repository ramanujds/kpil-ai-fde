"""
Concept 3: Dictionaries (dicts)

A dict stores data as key -> value pairs. You look things up by key,
not by position.
Everyday examples: a phone book (name -> number), a student record
(field -> value), a price list (item -> price).

Run:  python 03_dicts.py
"""

# ---------------------------------------------------------------
# 1. Creating a dict
# ---------------------------------------------------------------
# Curly brackets, key: value pairs separated by commas.
student = {
    "name": "Asha",
    "age": 21,
    "city": "Ahmedabad",
}
print("Student:", student)

# An empty dict, filled later.
prices = {}

# ---------------------------------------------------------------
# 2. Reading values
# ---------------------------------------------------------------
# Square brackets with the key.
print("\nName:", student["name"])

# A missing key with [] raises a KeyError and stops the program.
try:
    print(student["email"])
except KeyError as error:
    print("KeyError, no such key:", error)

# .get() is the safe way: returns None, or a default you choose.
print("Email (get)     :", student.get("email"))
print("Email (default) :", student.get("email", "not provided"))

# ---------------------------------------------------------------
# 3. Adding, updating, deleting
# ---------------------------------------------------------------
# Assigning to a new key adds it; assigning to an existing key updates it.
student["email"] = "asha@example.com"  # add
student["age"] = 22  # update
print("\nAfter add and update:", student)

# del removes a key. pop removes it AND gives back the value.
del student["city"]
removed_email = student.pop("email")
print("Removed email:", removed_email)
print("Now:", student)

# ---------------------------------------------------------------
# 4. Checking for a key
# ---------------------------------------------------------------
# 'in' checks KEYS, not values.
print("\n'name' in student:", "name" in student)
print("'Asha' in student:", "Asha" in student)  # False, Asha is a value

# ---------------------------------------------------------------
# 5. Looping over a dict
# ---------------------------------------------------------------
prices = {"tea": 15, "coffee": 25, "biscuit": 10}

print("\nKeys only:")
for item in prices:  # looping a dict gives keys
    print("  -", item)

print("Values only:", list(prices.values()))
print("Total of all prices:", sum(prices.values()))

# .items() gives (key, value) tuples; unpack them (see Concept 2).
print("\nPrice list:")
for item, price in prices.items():
    print(f"  {item:<8} Rs {price}")

# ---------------------------------------------------------------
# 6. Nested dicts and lists inside dicts
# ---------------------------------------------------------------
# Values can be anything: numbers, lists, even other dicts.
profile = {
    "name": "Ravi",
    "skills": ["Python", "SQL"],  # a list as a value
    "address": {  # a dict as a value
        "city": "Surat",
        "pin": "395007",
    },
}
# Chain the brackets to go deeper.
print("\nFirst skill:", profile["skills"][0])
print("City       :", profile["address"]["city"])

profile["skills"].append("Git")  # changes the list inside the dict
print("Skills now :", profile["skills"])

# ---------------------------------------------------------------
# 7. A list of dicts
# ---------------------------------------------------------------
# The most common shape for a table of records: one dict per row.
students = [
    {"name": "Asha", "marks": 91},
    {"name": "Ravi", "marks": 67},
    {"name": "Meera", "marks": 88},
]

print("\nAbove 80:")
for s in students:
    if s["marks"] > 80:
        print("  ", s["name"], s["marks"])

# Sort the records by a field.
ranked = sorted(students, key=lambda s: s["marks"], reverse=True)
print("Top student:", ranked[0]["name"])

# Pull one field out of every record with a comprehension.
names = [s["name"] for s in students]
print("Names:", names)

# ---------------------------------------------------------------
# 8. Counting with a dict
# ---------------------------------------------------------------
# A classic pattern: how many times does each word appear?
words = ["tea", "coffee", "tea", "tea", "coffee", "milk"]
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1  # start at 0 if new
print("\nCounts:", counts)

# ---------------------------------------------------------------
# 9. Dict comprehension and merging
# ---------------------------------------------------------------
# Pattern: {key: value for item in collection}
squares = {n: n * n for n in range(1, 6)}
print("\nSquares:", squares)

# Merge two dicts with |. On a clash, the right-hand side wins.
defaults = {"theme": "light", "font_size": 12}
overrides = {"font_size": 16}
settings = defaults | overrides
print("Settings:", settings)

# ---------------------------------------------------------------
# 10. Gotcha: copying a dict
# ---------------------------------------------------------------
# Like lists, '=' does not copy. Use .copy() for a new dict.
original = {"pen": 10}
alias = original
alias["ruler"] = 5
print("\nOriginal changed too:", original)

safe_copy = original.copy()
safe_copy["eraser"] = 3
print("Original untouched  :", original)

# Note: .copy() is shallow. Nested lists or dicts inside are still shared.
# Use copy.deepcopy() from the standard library for a fully separate copy.
