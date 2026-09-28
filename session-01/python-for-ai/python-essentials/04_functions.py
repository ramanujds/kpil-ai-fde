"""
Concept 4: Functions

A function is a named, reusable block of code. You write it once and
call it as many times as you need.
Everyday example: a recipe. The name is "make tea", the ingredients are
the inputs, and the cup of tea is the output.

Run:  python 04_functions.py
"""

# ---------------------------------------------------------------
# 1. Defining and calling a function
# ---------------------------------------------------------------
# 'def' + name + brackets + colon. The indented lines are the body.
def greet():
    print("Hello!")


greet()  # nothing happens until you CALL the function
greet()  # call it again, no need to rewrite the code


# ---------------------------------------------------------------
# 2. Parameters: giving a function its inputs
# ---------------------------------------------------------------
# 'name' is a parameter (the placeholder in the definition).
# "Asha" below is an argument (the real value passed in the call).
def greet_person(name):
    print(f"Hello, {name}!")


print()
greet_person("Asha")
greet_person("Ravi")


# ---------------------------------------------------------------
# 3. return: getting a result back
# ---------------------------------------------------------------
# print shows something on screen. return hands a value back to the caller,
# so you can store it or use it in another calculation.
def add(a, b):
    return a + b


total = add(3, 4)
print("\n3 + 4 =", total)
print("(3 + 4) * 2 =", add(3, 4) * 2)


# A function with no return gives back None.
def say_hi():
    print("hi")


result = say_hi()
print("say_hi returned:", result)


# ---------------------------------------------------------------
# 4. Default values
# ---------------------------------------------------------------
# A parameter with '=' is optional. The default is used if you skip it.
def greet_with(name, greeting="Hello"):
    return f"{greeting}, {name}!"


print()
print(greet_with("Asha"))  # uses the default greeting
print(greet_with("Asha", "Namaste"))  # overrides it


# ---------------------------------------------------------------
# 5. Keyword arguments
# ---------------------------------------------------------------
# Pass arguments by name. Order no longer matters, and the call
# reads like a sentence.
def make_tea(sugar=1, milk=True, size="regular"):
    milk_text = "with milk" if milk else "without milk"
    return f"{size} tea, {sugar} sugar, {milk_text}"


print()
print(make_tea())
print(make_tea(size="large", sugar=0))
print(make_tea(milk=False))


# ---------------------------------------------------------------
# 6. Returning several values
# ---------------------------------------------------------------
# Return a tuple (Concept 2) and unpack it on the way out.
def min_and_max(numbers):
    return min(numbers), max(numbers)


low, high = min_and_max([42, 91, 67, 88])
print(f"\nLow={low}, High={high}")


# ---------------------------------------------------------------
# 7. Docstrings and type hints
# ---------------------------------------------------------------
# A docstring (the triple-quoted text) explains what the function does.
# Type hints say what kinds of values go in and come out.
# Python does NOT enforce hints, but editors and readers love them.
def average(numbers: list[float]) -> float:
    """Return the average of a list of numbers."""
    return sum(numbers) / len(numbers)


print("\nAverage:", average([42, 91, 67, 88]))
print("Docstring:", average.__doc__)


# ---------------------------------------------------------------
# 8. *args: any number of arguments
# ---------------------------------------------------------------
# A * in front of the parameter collects extra arguments into a tuple.
def total_of(*numbers):
    print("  received:", numbers)
    return sum(numbers)


print()
print("Total:", total_of(1, 2, 3))
print("Total:", total_of(10, 20, 30, 40, 50))


# ---------------------------------------------------------------
# 9. **kwargs: any number of named arguments
# ---------------------------------------------------------------
# ** collects extra named arguments into a dict (Concept 3).
def show_profile(**details):
    print("  received:", details)
    for key, value in details.items():
        print(f"  {key}: {value}")


print()
show_profile(name="Asha", city="Ahmedabad", age=22)

# The reverse also works: ** unpacks a dict into named arguments.
data = {"sugar": 2, "size": "large"}
print(make_tea(**data))


# ---------------------------------------------------------------
# 10. Functions are values too
# ---------------------------------------------------------------
# You can pass a function into another function, like any other value.
def double(n):
    return n * 2


def apply_to_all(func, items):
    return [func(item) for item in items]


print("\nDoubled:", apply_to_all(double, [1, 2, 3]))

# lambda: a tiny one-line function without a name.
# You saw it earlier in sorted(..., key=lambda ...).
print("Squared:", apply_to_all(lambda n: n * n, [1, 2, 3]))

# Functions can also be stored in a dict and chosen by name.
operations = {"add": add, "double": double}
chosen = "add"
print("Chosen operation result:", operations[chosen](5, 6))


# ---------------------------------------------------------------
# 11. Scope: variables live inside their function
# ---------------------------------------------------------------
def make_message():
    message = "I only exist inside the function"
    return message


print("\n" + make_message())
# print(message)  # would fail with NameError: message is not defined here


# ---------------------------------------------------------------
# 12. Gotcha: never use a list or dict as a default value
# ---------------------------------------------------------------
# The default is created ONCE and shared by every call.
def add_item_bad(item, basket=[]):
    basket.append(item)
    return basket


print("\nBad first call :", add_item_bad("apple"))
print("Bad second call:", add_item_bad("banana"))  # apple is still there!


# Fix: default to None, then create a fresh list inside.
def add_item_good(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item)
    return basket


print("Good first call :", add_item_good("apple"))
print("Good second call:", add_item_good("banana"))  # a clean list each time
