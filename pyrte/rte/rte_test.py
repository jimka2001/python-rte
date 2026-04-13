# Copyright (©) 2026 EPITA Research Laboratory
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.r_rte.py

from rte.r_cat import Cat
from rte.r_or import Or
from rte.r_not import Not
from rte.r_and import And
from rte.syntax_sugar import *
from rte.r_star import Star

test_sequences = [[],
                  [1],
                  [3],
                  [1, 2, 3, 4],
                  [1, 2, 3.0, 4.0],
                  [1.1, 2.1, 3, 4],
                  [1.0],

                  ["hello"],
                  ["hello", 3],
                  [3, "hello"],
                  ["hello", 3.1],
                  [3.1, "hello"],
                  [""],
                  ["hello", "world"],
                  ["hello", 1, "world", 2.0],
                  [1, 2, "hello", 3.0, "world"],
                  [1, 2, "hello", 3, "world"],
                  ]
test_rtes = [Star(Atomic(int)),
             Star(Atomic(float)),
             Star(Cat(Atomic(str), Atomic(int))),
             Star(Cat(Atomic(str), Atomic(float))),
             Or(Cat(Atomic(int), Atomic(str)),
                Cat(Atomic(str), Atomic(int))),
             Or(Cat(Atomic(float), Atomic(str)),
                Cat(Atomic(str), Atomic(float))),
             Star(Or(Atomic(float), Atomic(int))),
             And(Not(Eql(1)), Atomic(int)),
             Star(And(Not(Eql(1)), Atomic(int))),
             Star(And(Not(Eql(1)), Atomic(float))),
             Plus(Atomic(int)),
             Plus(Atomic(float)),
             Plus(Or(Atomic(int), Atomic(float))),
             Plus(Cat(Atomic(str), Optional(Atomic(int)))),
             Cat(Star(Atomic(str)), Atomic(int)),
             And(Plus(Cat(Atomic(str), Optional(Atomic(int)))),
                 Cat(Star(Atomic(str)), Atomic(int))),
             And(Contains(Atomic(str)), Contains(Atomic(int))),
             And(Contains(Atomic(str)), Not(Contains(Atomic(int)))),
             And(Not(Contains(Atomic(str))), Contains(Atomic(int))),
             ]

if __name__ == '__main__':
    # the variables test_sequences and test_rtes have
    #   been chosen so that every rte matches at least one
    #   sequence and every sequence matches at least one rte.
    print("counting rtes")
    for seq in test_sequences:
        count = len([rte for rte in test_rtes
                     if rte.simulate(True, seq)])
        print(count)
        if count == 0:
            print(f"seq = {seq}")

    print("counting sequences")
    for rte in test_rtes:
        count = len([seq for seq in test_sequences
                     if rte.simulate(True, seq)])
        print(count)
        if count == 0:
            print(f"rte = {rte}")
