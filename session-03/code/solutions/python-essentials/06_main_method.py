"""
Concept 6: The main method

Python has no special "main" keyword like some languages. Instead, we use
a small, well-known pattern:

    def main():
        ...

    if __name__ == "__main__":
        main()

It means: "run main() only when this file is started directly, not when
another file imports it."
Everyday example: a shop with a front door. Customers (other files) can
walk in and use the shelves (functions), but the shop only opens for
business (main) when the owner unlocks it.

Run:  python 06_main_method.py
      python 06_main_method.py Asha          (with a command-line argument)
"""

import sys  # gives access to command-line arguments

# Importing runs the top of area_tools.py (you will see its "loaded" line),
# but NOT its demo, because that sits behind the main guard.
import area_tools

# ---------------------------------------------------------------
# 1. What is __name__?
# ---------------------------------------------------------------
# Python sets a built-in variable __name__ for every file.
#   - file started directly:  __name__ is "__main__"
#   - file imported:          __name__ is the file's name
print("This file's __name__ is:", repr(__name__))
print("area_tools' __name__ is:", repr(area_tools.__name__))
print()


# ---------------------------------------------------------------
# 2. Put reusable work in functions
# ---------------------------------------------------------------
# Keep the top level of the file for definitions only.
# The actual work goes inside functions.
def build_report(students):
    """Return a dict of summary numbers for a list of student dicts."""
    marks = [s["marks"] for s in students]
    return {
        "count": len(marks),
        "average": sum(marks) / len(marks),
        "top": max(students, key=lambda s: s["marks"])["name"],
    }


def greet(name="friend"):
    return f"Welcome, {name}!"


# ---------------------------------------------------------------
# 3. The main function: the single starting point
# ---------------------------------------------------------------
# Reading main() top to bottom tells the whole story of the program.
def main():
    # sys.argv is a list of the words typed on the command line.
    # argv[0] is the script name; the rest are the arguments.
    name = sys.argv[1] if len(sys.argv) > 1 else "friend"
    print(greet(name))

    # Using lists, dicts and functions from the earlier concepts:
    students = [
        {"name": "Asha", "marks": 91},
        {"name": "Ravi", "marks": 67},
        {"name": "Meera", "marks": 88},
    ]
    report = build_report(students)
    print("Report:", report)

    # Using the imported module.
    print("Circle area (r=2):", round(area_tools.circle_area(2), 2))

    # Return a status code: 0 means success (the convention everywhere).
    return 0


# ---------------------------------------------------------------
# 4. The guard
# ---------------------------------------------------------------
# Without this guard, main() would also run if another file did
# "import 06_main_method" (or any file imported this one).
#
# sys.exit(main()) passes main's return value to the operating system,
# so scripts and schedulers can tell success (0) from failure.
if __name__ == "__main__":
    sys.exit(main())

# ---------------------------------------------------------------
# 5. Habits worth keeping
# ---------------------------------------------------------------
#  - Definitions (imports, classes, functions) at the top of the file.
#  - The work lives in main() and the functions it calls.
#  - The guard is the last few lines of the file.
#  - For richer command-line options (flags, help text), Python's built-in
#    argparse module builds on the same idea.
