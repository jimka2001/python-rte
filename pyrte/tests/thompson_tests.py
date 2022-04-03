# Copyright (©) 2022 EPITA Research and Development Laboratory
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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import unittest

from genus.s_atomic import SAtomic
from genus.s_top import STop
from genus.s_not import SNot
from genus.s_and import SAnd
from genus.s_or import SOr
from genus.s_eql import SEql
from genus.s_member import SMember
from genus.s_satisfies import SSatisfies
from rte.r_cat import Cat
from rte.r_emptyset import EmptySet
from rte.r_epsilon import Epsilon
from rte.r_or import Or
from rte.r_and import And
from rte.r_random import random_rte
from rte.r_sigma import Sigma
from rte.r_singleton import Singleton
from rte.r_star import Star
from rte.r_not import Not
from rte.thompson import constructThompsonDfa, accessible, simulateTransitions
from rte.xymbolyco import Dfa
from genus.depthgenerator import Test2, Test1, TestB, TestA

# default value of num_random_tests is 1000, but you can temporarily edit this file
#   and set it to a smaller number for a quicker run of the tests.
num_random_tests = 1000


class ThompsonCase(unittest.TestCase):

    def test_Epsilon(self):
        dfa = constructThompsonDfa(Epsilon, 42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([]))
        self.assertIsNone(dfa.simulate([1, 2, 3]))

    def test_Sigma(self):
        dfa = constructThompsonDfa(Sigma, 42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([1]))
        self.assertEqual(42, dfa.simulate(["hello"]))
        self.assertIsNone(dfa.simulate([1, 2, 3]))

    def test_SigmaStar(self):
        dfa = constructThompsonDfa(Star(Sigma), 42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([1]))
        self.assertEqual(42, dfa.simulate(["hello"]))
        self.assertEqual(42, dfa.simulate([1, 2, 3]))

    def test_EmptySet(self):
        dfa = constructThompsonDfa(EmptySet, 42)
        self.assertTrue(Dfa == type(dfa))
        self.assertFalse(dfa.inhabited())

    def test_EmptySetStar(self):
        dfa = constructThompsonDfa(Star(EmptySet), 42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([]))
        self.assertIsNone(dfa.simulate([1, 2, 3]))

    def test_Singleton(self):
        dfa = constructThompsonDfa(Singleton(SAtomic(int)), 42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([1]))
        self.assertIsNone(dfa.simulate([1, 2, 3]))

    def test_Star(self):
        dfa = constructThompsonDfa(Star(Singleton(SAtomic(int))), 42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([1]))
        self.assertEqual(42, dfa.simulate([1, 2, 3]))
        self.assertIsNone(dfa.simulate([1, 2.0, 3]))

    def test_Cat(self):
        dfa = constructThompsonDfa(Cat(Singleton(SAtomic(int)),
                                       Singleton(SAtomic(str))),
                                   42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([1, "hello"]))
        self.assertIsNone(dfa.simulate([]))
        self.assertIsNone(dfa.simulate([1, "hello", "hello"]))
        self.assertIsNone(dfa.simulate([1, 2.0, 3]))

    def test_Or(self):
        dfa = constructThompsonDfa(Or(Singleton(SAtomic(int)),
                                      Singleton(SAtomic(str))),
                                   42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([1]))
        self.assertEqual(42, dfa.simulate(["hello"]))
        self.assertIsNone(dfa.simulate([]))
        self.assertIsNone(dfa.simulate([1, "hello", "hello"]))
        self.assertIsNone(dfa.simulate([1, 2.0, 3]))

    def test_Not(self):
        dfa = constructThompsonDfa(Not(Or(Singleton(SAtomic(int)),
                                          Singleton(SAtomic(str)))),
                                   42)
        #dfa.to_dot(view=True,title="xor", label="neither int nor str", draw_sink=True)
        self.assertTrue(Dfa == type(dfa))
        self.assertIsNone(dfa.simulate([1]))
        self.assertIsNone(dfa.simulate(["hello"]))
        self.assertEqual(42, dfa.simulate([]))
        self.assertEqual(42, dfa.simulate([1, "hello", "hello"]),
                         f"[1 'hello', 'hello'] is int or str")
        self.assertEqual(42, dfa.simulate([1, 2.0, 3]))

    def test_And(self):
        # begins with int and ends with str
        dfa = constructThompsonDfa(And(Cat(Singleton(SAtomic(int)), Star(Sigma)),
                                       Cat(Star(Sigma), Singleton(SAtomic(str)))),
                                   42)
        self.assertTrue(Dfa == type(dfa))
        self.assertEqual(42, dfa.simulate([1, "hello", "hello"]))
        self.assertEqual(42, dfa.simulate([1, 2.2, 2.2, "hello", "hello"]))
        self.assertIsNone(dfa.simulate([1, 2.2, 2.2]))
        self.assertIsNone(dfa.simulate([2.2, 2.2, "hello", "hello"]))
        self.assertIsNone(dfa.simulate([]))

    def check(self, depth, pattern):
        dfa_thompson = constructThompsonDfa(pattern, 42)
        dfa_brzozowski = pattern.to_dfa(42)
        dfa_xor = dfa_thompson.xor(dfa_brzozowski)
        # equivalent might return None or True, but need to fail if returns False
        if dfa_brzozowski.equivalent(dfa_thompson) is False:
            dfa_brzozowski.to_dot(title="brzozowski",
                                  view=True,
                                  abbrev=True,
                                  label=f"{depth} {pattern}")
            dfa_thompson.to_dot(title="thompson",
                                abbrev=True,
                                view=True,
                                label=f"{depth} {pattern}")
            dfa_xor.to_dot(title="xor",
                           abbrev=True,
                           view=True,
                           label=f"XOR{depth} {pattern}")
        self.assertTrue(dfa_brzozowski.equivalent(dfa_thompson) is not False,
                        f"problem detected with depth={depth} {pattern}")

    def test_randomCreate(self):
        for depth in range(4):
            for r in range(num_random_tests):
                pattern = random_rte(depth)
                self.check(depth, pattern)

    def test_discovered1(self):
        odd = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
        pattern = Not(And(Not(Cat(Not(Singleton(SAtomic(int))),
                                  Cat(Singleton(SEql(1)),
                                      Singleton(SEql(0))))),
                          Or(Star(Or(Singleton(SAtomic(Test2)),
                                     Singleton(odd))),
                             Sigma)))

        self.check(5, pattern)

    def test_discovered2(self):
        pattern = Cat(Or(Singleton(SMember('a', 'b', 'c')),
                         Singleton(SAtomic(float))),
                      Or(Singleton(SMember('a', 'b', 'c')),
                         Singleton(SEql(3.14))))
        self.check(2, pattern)

    def test_discovered3(self):
        from rte.thompson import profile
        odd = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")

        for pattern in [
            Cat(Star(Singleton(SAtomic(TestA))), And(Singleton(SEql(3.14)), Singleton(STop))),
            Or(Or(Singleton(SMember(1,2,3)),
                  Singleton(SEql('a'))), Or(Singleton(SAtomic(int)), Singleton(STop))),
            Or(Star(Singleton(SMember())), Not(Singleton(odd))),
            Cat(Or(Singleton(SAtomic(Test1)), Singleton(SEql(''))), Cat(Singleton(SEql(1)),
                                                                        Singleton(SEql('a')))),
            Cat(Not(Singleton(SEql(''))), Star(Singleton(SEql(0)))),
            Singleton(
                SNot(SNot(SOr(SAnd(odd, SNot(SEql('a'))), SAnd(SAnd(SAtomic(TestB), SEql('a')), SNot(SMember())))))),
            Or(Singleton(SOr(even, SAnd(SOr(SEql(3.14), SAnd(SEql(''), SEql(''))),
                                        SAnd(SOr(SMember('a', 'b', 'c'), SAtomic(TestA)), SEql(3.14))))),
               Or(Singleton(SOr(SAtomic(TestB), SAnd(SOr(SAtomic(Test1), SAtomic(Test2)),
                                                     SAnd(SEql(0), SAtomic(TestB))))),
                  Not(Or(Cat(Singleton(SAtomic(Test1)), Singleton(SEql(3.14))), Not(Singleton(SEql(0))))))),
            Not(Star(And(Cat(Singleton(SNot(SAtomic(Test2))),
                             And(Singleton(SAtomic(TestB)), Singleton(SMember()))),
                         Or(Cat(Singleton(SEql(-1)), Singleton(SEql('a'))),
                            Star(Singleton(SEql(0)))))))
        ]:
            self.assertTrue(profile(pattern, 2, 1))

    def test_accessible(self):
        ini, outs, transitions = accessible(0,
                                            [97, 98, 99],
                                            [(0, STop, 1),
                                             (1, STop, 97),
                                             (1, STop, 98),
                                             (2, STop, 99)])
        self.assertEqual(ini, 0)
        self.assertEqual(set(outs), {97, 98})
        self.assertEqual(set(transitions), {(0, STop, 1),
                                            (1, STop, 97),
                                            (1, STop, 98)})

    def test_simulate(self):
        ini = 0
        outs = [1, 2]
        transitions = [(0, STop, 1),
                       (1, SAtomic(int), 2),
                       (1, SOr(SAtomic(str),
                               SAtomic(int)), 3),
                       (3, STop, 0)]
        self.assertEqual(simulateTransitions([1, 2], 42,
                                             ini, outs, transitions), 42)
        self.assertIs(simulateTransitions([1, 2, 3], 42,
                                          ini, outs, transitions), None)
        self.assertEqual(simulateTransitions([1, 2, 3, 4], 42,
                                             ini, outs, transitions), 42)


if __name__ == '__main__':
    unittest.main()
