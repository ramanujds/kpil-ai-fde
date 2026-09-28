"""
Concept 5: Classes and Objects

A class is a blueprint. An object is one thing built from that blueprint.
A class bundles DATA (attributes) and ACTIONS (methods) together.
Everyday example: the blueprint of a house is the class; each house built
from it is an object. Same design, but each house has its own address,
its own colour, its own people living inside.

Run:  python 05_classes_and_objects.py
"""

from dataclasses import dataclass

# ---------------------------------------------------------------
# 1. The simplest class
# ---------------------------------------------------------------
# Class names use CapitalCase. 'pass' means "nothing here yet".
class Empty:
    pass


thing = Empty()  # calling the class builds an object
print("Type of thing:", type(thing).__name__)


# ---------------------------------------------------------------
# 2. __init__ and self: giving each object its own data
# ---------------------------------------------------------------
# __init__ runs automatically when an object is created.
# 'self' is the object being built. Attributes are stored on self.
class Student:
    def __init__(self, name, marks):
        self.name = name  # attribute
        self.marks = marks  # attribute

    # A method is a function inside a class. It always takes self first,
    # so it can read and change this object's own data.
    def introduce(self):
        return f"I am {self.name} and I scored {self.marks}."

    def is_passing(self):
        return self.marks >= 40


# Create objects. Notice we do not pass self; Python does that for us.
asha = Student("Asha", 91)
ravi = Student("Ravi", 35)

print("\n" + asha.introduce())
print(ravi.introduce())

# Each object has its own data.
print("Asha passing?", asha.is_passing())
print("Ravi passing?", ravi.is_passing())

# Attributes can be read and changed with a dot.
ravi.marks = 55
print("Ravi after re-test:", ravi.marks, "| passing?", ravi.is_passing())


# ---------------------------------------------------------------
# 3. Objects that remember state
# ---------------------------------------------------------------
# Methods can change the object's data, so the object "remembers".
# This example also uses default values (Concept 4) and a list (Concept 1).
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []  # a NEW list for every account

    def deposit(self, amount):
        if amount <= 0:
            # raise stops the method with an error
            raise ValueError("Deposit must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))  # a tuple (Concept 2)

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Not enough balance")
        self.balance -= amount
        self.history.append(("withdraw", amount))

    # __str__ controls what print() shows for the object.
    def __str__(self):
        return f"{self.owner}: Rs {self.balance}"


account = BankAccount("Asha", 1000)
account.deposit(500)
account.withdraw(200)
print("\n" + str(account))
print("History:", account.history)

try:
    account.withdraw(99999)
except ValueError as error:
    print("Rejected:", error)

# Two accounts never share data.
other = BankAccount("Ravi")
print(other, "| history:", other.history)


# ---------------------------------------------------------------
# 4. Class attributes vs instance attributes
# ---------------------------------------------------------------
# An attribute set on the class is shared by ALL objects.
# An attribute set on self belongs to ONE object.
class Employee:
    company = "Acme Ltd"  # class attribute: same for everyone
    count = 0  # class attribute used as a counter

    def __init__(self, name):
        self.name = name  # instance attribute: differs per object
        Employee.count += 1


e1 = Employee("Meera")
e2 = Employee("Kabir")
print("\nCompany:", e1.company, "|", e2.company)
print("Employees created:", Employee.count)


# ---------------------------------------------------------------
# 5. Private-by-convention attributes
# ---------------------------------------------------------------
# Python has no strict "private". A leading underscore is a polite signal:
# "internal detail, please use the methods instead".
class Counter:
    def __init__(self):
        self._value = 0  # internal

    def increment(self):
        self._value += 1

    def current(self):
        return self._value


counter = Counter()
counter.increment()
counter.increment()
print("\nCounter:", counter.current())


# ---------------------------------------------------------------
# 6. Inheritance: build on an existing class
# ---------------------------------------------------------------
# SavingsAccount IS-A BankAccount, plus something extra.
# Put the parent class in brackets. It gets all the parent's attributes
# and methods for free.
class SavingsAccount(BankAccount):
    def __init__(self, owner, balance=0, rate=0.04):
        super().__init__(owner, balance)  # let the parent set up its part
        self.rate = rate

    def add_interest(self):
        interest = self.balance * self.rate
        self.deposit(interest)  # reuse the parent's method

    # Override: same name as the parent's method, new behaviour.
    def __str__(self):
        return f"{self.owner} (savings): Rs {self.balance:.2f}"


savings = SavingsAccount("Meera", 2000)
savings.add_interest()
print("\n" + str(savings))
print("Is it also a BankAccount?", isinstance(savings, BankAccount))


# ---------------------------------------------------------------
# 7. Objects working together (composition)
# ---------------------------------------------------------------
# An object can hold other objects. A Classroom HAS students.
class Classroom:
    def __init__(self, name):
        self.name = name
        self.students = []  # a list of Student objects

    def add(self, student):
        self.students.append(student)

    def average_marks(self):
        return sum(s.marks for s in self.students) / len(self.students)

    def toppers(self, minimum=80):
        return [s.name for s in self.students if s.marks >= minimum]


room = Classroom("Class 10-A")
room.add(asha)
room.add(ravi)
room.add(Student("Meera", 88))
print("\nAverage marks:", room.average_marks())
print("Toppers:", room.toppers())


# ---------------------------------------------------------------
# 8. @dataclass: a shortcut for classes that mainly hold data
# ---------------------------------------------------------------
# Python writes __init__ and a readable print for you.
# Fields need a type hint; a default value makes the field optional.
@dataclass
class Book:
    title: str
    author: str
    pages: int = 100


book = Book("Wings of Fire", "A. P. J. Abdul Kalam", 180)
print("\n", book)
print("Title:", book.title)
print("Default pages:", Book("Untitled", "Unknown").pages)
