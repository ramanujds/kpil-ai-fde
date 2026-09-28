"""
Helper module for Concept 6 (the main method).

This file plays two roles:
  1. A module that other files can import and reuse.
  2. A small script you can run by itself to try it out.

Try both:
  python area_tools.py          (runs the demo at the bottom)
  python 06_main_method.py      (imports this file; the demo does NOT run)
"""

import math

# This line is at the top level, so it runs whenever the file is loaded,
# whether by running it or by importing it. Watch what __name__ says.
print(f"[area_tools loaded, __name__ = {__name__!r}]")


def circle_area(radius):
    return math.pi * radius**2


def rectangle_area(width, height):
    return width * height


def main():
    # A quick self-test. Only runs when this file is executed directly.
    print("Running area_tools on its own")
    print("Circle (r=3)    :", round(circle_area(3), 2))
    print("Rectangle (4x5) :", rectangle_area(4, 5))


if __name__ == "__main__":
    main()
