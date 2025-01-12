# Copyright (©) 2021,22 EPITA Research and Development Laboratory
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


import os
import unittest

from genus.depthgenerator import random_type_designator, test_values
from genus.genus_types import NormalForm
from genus.mdtd import mdtd
from genus.s_and import SAnd, createSAnd, andp
from genus.s_atomic import SAtomic
from genus.s_satisfies import SSatisfies
from genus.s_empty import SEmptyImpl, SEmpty
from genus.s_eql import SEql
from genus.s_member import SMember
from genus.s_not import SNot, notp
from genus.s_or import SOr, createSOr, orp
from genus.s_top import STopImpl, STop
from genus.simple_type_d import TerminalType
from genus.utils import compare_sequence, cmp_objects
from genus.utils import find_simplifier, find_first
from genus.utils import generate_lazy_val, fixed_point
from genus.utils import uniquify, trace_graph, remove_element, search_replace, search_replace_splice

# default value of num_random_tests is 1000, but you can temporarily edit this file
#   and set it to a smaller number for a quicker run of the tests.
num_random_tests = 1000


def t_verboseonlyprint(s):
    if 'genusverbose' in os.environ and os.environ['genusverbose'] == str(True):
        print(s)


class GenusCase(unittest.TestCase):

    def test_atomic(self):
        def x():
            from genus.depthgenerator import TestA
            return TestA

        def y():
            class TestA:
                pass

            return TestA

        self.assertTrue(SAtomic(int) is SAtomic(int))
        self.assertTrue(SAtomic(int) is not SAtomic(str))
        self.assertTrue(SAtomic(x()) is SAtomic(x()))
        self.assertTrue(SAtomic(x()) is not SAtomic(y()))

    def test_fixed_point(self):
        self.assertTrue(fixed_point(0, (lambda x: x), (lambda x, y: x == y)) == 0)
        self.assertTrue(fixed_point(0, (lambda x: x // 2), (lambda x, y: x == y)) == 0)

    def test_fixed_point2(self):

        # fixed_point is just a way to incrementally apply a function on a value
        # until another function deem the delta between two consecutive values to be negligible
        def increment(x):
            return x

        def evaluator(x, y):
            return x == y

        self.assertTrue(fixed_point(5, increment, evaluator) == 5)
        self.assertTrue(fixed_point(5, lambda x: x + 1, lambda x, y: x == 6 and y == 7) == 6)

    def test_fixed_point3(self):

        def invariant(x):
            return x == 2

        self.assertTrue(fixed_point(2, lambda x: x, lambda x, y: x == y, invariant) == 2)

        def f(x):
            if x % 2 == 0:
                return x + 1
            return x - 1

        with self.assertRaises(AssertionError):
            fixed_point(1, lambda x: x, lambda x, y: x == y, invariant)
            fixed_point(1, lambda x: x + 1, lambda x, y: x == y, invariant)
            fixed_point(2, f, lambda x, y: x == y + 4, invariant)

    def test_STop(self):

        # STop has to be unique
        self.assertTrue(id(STop) == id(STopImpl()))
        self.assertTrue(STop is STopImpl())

        # str(a) has to be "STop"
        self.assertTrue((str(STop) == "STop"))

        from genus.depthgenerator import test_values
        for x in test_values:
            self.assertTrue((STop.typep(x)))

        # obviously, `a` is inhabited as it contains everything by definition
        self.assertTrue((STop.inhabited() is True))

        # `a` is never disjoint with anything but the empty subtype
        self.assertTrue(STop.disjoint(SAtomic(object)) is False)
        self.assertTrue(STop.disjoint(SEmpty) is True)

        # on the contrary, `a` is never a subtype of any type
        # since types are sets and top is the set that contains all sets
        self.assertTrue((STop.subtypep(SAtomic(object)) is True))
        self.assertTrue(STop.subtypep(STop) is True)

    def test_ssatisfies(self):
        def l_odd(n):
            return isinstance(n, int) and n % 2 == 1

        guinea_pig = SSatisfies(l_odd, "[odd numbers]")
        self.assertTrue(guinea_pig.f == l_odd)
        self.assertTrue(guinea_pig.printable == "[odd numbers]")
        self.assertTrue(str(guinea_pig) == "[odd numbers]?")
        for x in range(-100, 100):
            if x % 2 == 1:
                self.assertTrue(guinea_pig.typep(x))
            else:
                self.assertTrue(not guinea_pig.typep(x))
        assert (not guinea_pig.typep("hello"))
        assert (guinea_pig.subtypep(SAtomic(type(4))) is None)

    def test_ssatisfies2(self):
        def l_odd(n):
            return isinstance(n, int) and n % 2 == 1

        self.assertTrue(SSatisfies(l_odd, "odd").disjoint(SMember(1, 2, 3)) is False)

    def test_sand1(self):
        quadruple = SSatisfies((lambda x: x % 4 == 0), "quadruple")

        triple = SSatisfies(lambda x: isinstance(x, int) and (x % 3 == 0), "triple")

        tri_n_quad = SAnd(triple, quadruple)
        create_tri_n_quad = createSAnd([triple, quadruple])

        self.assertTrue(str(tri_n_quad) == "SAnd(triple?, quadruple?)")
        self.assertTrue(str(create_tri_n_quad) == "SAnd(triple?, quadruple?)")

        self.assertTrue(tri_n_quad.typep(12))
        self.assertTrue(create_tri_n_quad.typep(12))
        self.assertTrue(not tri_n_quad.typep(6))
        self.assertTrue(not create_tri_n_quad.typep(6))
        self.assertTrue(not tri_n_quad.typep(3))
        self.assertTrue(not create_tri_n_quad.typep(3))
        self.assertTrue(tri_n_quad.typep(0))
        self.assertTrue(create_tri_n_quad.typep(0))
        self.assertTrue(not tri_n_quad.typep("hello"))
        self.assertTrue(not create_tri_n_quad.typep("hello"))

    def test_sand2(self):

        quadruple = SSatisfies((lambda x: x % 4 == 0), "quadruple")

        triple = SSatisfies(lambda x: isinstance(x, int) and (x % 3 == 0), "triple")

        tri_n_quad = SAnd(triple, quadruple)
        create_tri_n_quad = createSAnd([triple, quadruple])
        self.assertTrue(tri_n_quad.subtypep(STop))
        self.assertTrue(tri_n_quad.subtypep(triple))

        self.assertTrue(tri_n_quad.subtypep(quadruple))
        self.assertTrue(tri_n_quad.subtypep(SAtomic(type(5))) is None,
                        "%s != None" % tri_n_quad.subtypep(SAtomic(type(5))))

        self.assertTrue(SAnd().unit() == STop)
        self.assertTrue(SAnd().zero() == SEmpty)

        self.assertTrue(tri_n_quad.same_combination(create_tri_n_quad))
        self.assertTrue(tri_n_quad.same_combination(createSAnd([quadruple, triple])))

        self.assertTrue(not tri_n_quad.same_combination(STop))
        self.assertTrue(not tri_n_quad.same_combination(createSAnd([])))

    def test_sor(self):
        quadruple = SSatisfies(lambda x: isinstance(x, int) and x % 4 == 0, "quadruple")
        triple = SSatisfies(lambda x: isinstance(x, int) and x % 3 == 0, "triple")

        tri_o_quad = SOr(triple, quadruple)
        create_tri_o_quad = createSOr([triple, quadruple])

        self.assertTrue(str(tri_o_quad) == "SOr(triple?, quadruple?)")
        self.assertTrue(str(create_tri_o_quad) == "SOr(triple?, quadruple?)")

        self.assertTrue(tri_o_quad.typep(12))
        self.assertTrue(create_tri_o_quad.typep(12))

        self.assertTrue(tri_o_quad.typep(6))
        self.assertTrue(create_tri_o_quad.typep(6))

        self.assertTrue(tri_o_quad.typep(3))
        self.assertTrue(create_tri_o_quad.typep(3))

        self.assertTrue(tri_o_quad.typep(0))
        self.assertTrue(create_tri_o_quad.typep(0))

        self.assertTrue(not tri_o_quad.typep(5))
        self.assertTrue(not create_tri_o_quad.typep(5))

        self.assertTrue(not tri_o_quad.typep("hello"))
        self.assertTrue(not create_tri_o_quad.typep("hello"))

        self.assertTrue(SOr().unit() == SEmpty)

        self.assertTrue(SOr().zero() == STop)

        self.assertTrue(tri_o_quad.subtypep(STop))
        self.assertTrue(tri_o_quad.subtypep(SAtomic(type(5))) is None)

        self.assertTrue(tri_o_quad.same_combination(create_tri_o_quad))
        self.assertTrue(tri_o_quad.same_combination(createSOr([quadruple, triple])))

        self.assertTrue(not tri_o_quad.same_combination(STop))
        self.assertTrue(not tri_o_quad.same_combination(createSOr([])))

    def test_or_membership(self):
        x = SEql(1)
        y = SEql(2)

        self.assertTrue(SOr(x, y).typep(1) is True)
        self.assertTrue(SOr(x, y).typep(2) is True)
        self.assertTrue(SOr(x, y).typep(3) is False)

    def test_and_membership(self):
        x = SMember(1, 2, 3)
        y = SMember(2, 3, 4)

        self.assertTrue(SAnd(x, y).typep(0) is False)
        self.assertTrue(SAnd(x, y).typep(1) is False)
        self.assertTrue(SAnd(x, y).typep(2) is True)
        self.assertTrue(SAnd(x, y).typep(3) is True)
        self.assertTrue(SAnd(x, y).typep(4) is False)
        self.assertTrue(SAnd(x, y).typep(5) is False)

    def test_snot(self):
        pair = SSatisfies(lambda x: isinstance(x, int) and x & 1 == 0, "pair")

        with self.assertRaises(Exception):
            SNot([])

        npair = SNot(pair)

        self.assertTrue(SNot(SNot(pair)).canonicalize() == pair)

        self.assertTrue(str(npair) == "SNot(pair?)")

        self.assertTrue(npair.typep(5))
        self.assertTrue(npair.typep("hello"))
        self.assertTrue(not npair.typep(4))
        self.assertTrue(not npair.typep(0))

    def test_STop2(self):
        # STop has to be unique
        self.assertTrue(id(STop) == id(STopImpl()))
        self.assertTrue(STop is STopImpl())

        # str(a) has to be "Top"
        self.assertTrue(str(STop) == "STop")

        # a.subtypep(t) indicates whether t is a subtype of `a`, which is always the case by definition
        self.assertTrue(STop.subtypep(SAtomic(object)) is True)
        self.assertTrue(STop.subtypep(STop) is True)

        # obviously, `a` is inhabited as it contains everything by definition
        self.assertTrue(STop.inhabited() is True)

        # `a` is never disjoint with anything but the empty subtype
        self.assertTrue(STop.disjoint(SAtomic(object)) is False)
        self.assertTrue(STop.disjoint(SEmpty) is True)

        # on the contrary, `a` is never a subtype of any type
        # since types are sets and top is the set that contains all sets
        self.assertTrue(STop.subtypep(SAtomic(object)) is not False)
        self.assertTrue(STop.subtypep(STop) is True)

    def test_SEmpty(self):

        # SEmpty has to be unique
        self.assertTrue(id(SEmpty) == id(SEmptyImpl()))
        self.assertTrue(SEmpty is SEmptyImpl())

        # str(a) has to be "Empty"
        self.assertTrue(str(SEmpty) == "SEmpty")

        # a.typep(t) indicates whether t is a subtype of `a`, which is never the case
        self.assertTrue(SEmpty.typep(3) is False)
        self.assertTrue(SEmpty.subtypep(SEmpty) is True)
        for x in test_values:
            self.assertTrue(SEmpty.typep(x) is False)

        # obviously, `a` is not inhabited as it is by definition empty
        self.assertTrue(SEmpty.inhabited() is False)

        # `a` is disjoint with anything as it is empty
        self.assertTrue(SEmpty.disjoint(SAtomic(object)) is True)

        # on the contrary, `a` is always a subtype of any type
        # since types are sets and the empty set is a subset of all sets
        self.assertTrue(SEmpty.subtypep(SAtomic(object)) is True)
        self.assertTrue(SEmpty.subtypep(SEmpty) is True)

    def test_disjoint_310(self):
        # (disjoint? SNot(SMember(1, 2, 3)) SNot(SAtomic(str)))
        from genus.depthgenerator import Test2
        self.assertIs(SNot(SMember(1, 2, 3)).disjoint(SNot(SAtomic(str))), False)
        self.assertIs(SNot(SAtomic(str)).disjoint(SNot(SMember(1, 2, 3))), False)
        self.assertIs(SNot(SMember(1, 2, 3, "hello")).disjoint(SNot(SAtomic(str))), False)
        self.assertIs(SNot(SAtomic(str)).disjoint(SNot(SMember(1, 2, 3, "hello"))), False)
        self.assertIs(SNot(SOr(SNot(SEql(3.14)), SOr(SEql(0), SEql(-1))))
                      .disjoint(SNot(SOr(STop, SAtomic(Test2)))), True)
        self.assertIs(SNot(SOr(STop, SAtomic(Test2)))
                      .disjoint(SNot(SOr(SNot(SEql(3.14)), SOr(SEql(0), SEql(-1))))), True)
        self.assertIs(SOr(STop, STop).disjoint(SNot(SOr(STop, SAtomic(float)))), True)
        self.assertIs(SOr(STop, SNot(SEmpty)).disjoint(SNot(STop)), True)
        self.assertIs(SNot(SOr(STop, SAtomic(float))).disjoint(SOr(STop, SNot(SEmpty))), True)
        self.assertIs(STop.disjoint(SNot(SOr(STop, SAtomic(float)))), True)
        self.assertIs(SNot(SEmpty).disjoint(SNot(SOr(STop, SAtomic(float)))), True)
        self.assertIs(SOr(STop, SNot(SEmpty)).disjoint(SNot(SOr(STop, SAtomic(float)))), True)
        self.assertIs(SOr(STop, SNot(SMember())).disjoint(SNot(SOr(STop, SAtomic(float)))), True)
        self.assertIs(SOr(SAnd(STop, STop), SNot(SMember())).disjoint(SNot(SOr(STop, SAtomic(float)))), True)

    def test_disjoint_320(self):
        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td1 = random_type_designator(depth)
                td2 = random_type_designator(depth)
                d12 = td1.disjoint(td2)
                d21 = td2.disjoint(td1)
                self.assertIs(d12, d21,
                              f"\ntd1={td1}\ntd2={td2}\ntd1.disjoint(td2)={d12}\ntd2.disjoint(td1)={d21}")

    def test_disjoint_375(self):
        # Traceback (most recent call last):
        #  File "/Users/jnewton/Repos/python-rte/pyrte/tests/genus_tests.py", line 316, in test_disjoint_375
        #   self.assertTrue(td1.disjoint(td2) is not False,
        # AssertionError: False is not true : found types with empty intersection but not disjoint
        # td1=SOr(SNot([= 3.14]), SOr([= 0], [= -1]))
        # td2=SNot(SOr(STop, SAtomic(Test2)))

        # self.assertTrue(td1.disjoint(td2) is not False,
        #   AssertionError: False is not true : found types with empty intersection but not disjoint
        #   td1=SNot(SAnd(SAtomic(int), [= 1]))
        #   td2=SNot(SOr(SAtomic(int), STop))
        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td1 = random_type_designator(depth)
                td2 = random_type_designator(depth)
                d12 = td1.disjoint(td2)
                if SAnd(td1, td2).canonicalize(NormalForm.DNF) is SEmpty:
                    self.assertTrue(d12 is not False,
                                    "found types with empty intersection but not disjoint" +
                                    f"\ntd1={td1}" +
                                    f"\ntd2={td2}" +
                                    f"\n intersection = {SAnd(td1, td2).canonicalize(NormalForm.DNF)}" +
                                    f"\ntd1.disjoint(td2) = {d12}")

    def test_discovered_case_385(self):
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        td1 = STop
        td2 = SAnd(SEmpty, even)
        self.assertIs(SAnd(td1, td2).canonicalize(NormalForm.DNF), SEmpty)
        self.assertIsNot(td1.disjoint(td2), False, f"td1.disjoint(td2) = {td1.disjoint(td2)}")

    def test_discovered_case_375(self):
        from genus.depthgenerator import TestB, Test1
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        td1 = SAnd(SNot(SAtomic(TestB)),
                   SNot(SAtomic(int)),
                   SOr(SAtomic(Test1), even))
        td2 = SAnd(SNot(SAnd(SNot(SAtomic(TestB)),
                             SOr(SAtomic(Test1), even))),
                   SNot(SAtomic(int)))
        # self.assertIs(SAnd(td1,td2).canonicalize(NormalForm.DNF), SEmpty)
        self.assertIsNot(td1.disjoint_down(td2), False)
        self.assertIsNot(td1.disjoint(td2), False,
                         f"\ntd1={td1}\ntd2={td2}\ntd1.disjoint(td2) = {td1.disjoint(td2)}")

    def test_discovered_case_375b(self):
        from genus.depthgenerator import TestB, Test1
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        td1 = SAnd(SNot(SAtomic(TestB)),
                   SNot(SAtomic(int)),
                   SOr(SAtomic(Test1), even)).canonicalize()
        td2 = SAnd(SNot(SAnd(SNot(SAtomic(TestB)),
                             SOr(SAtomic(Test1), even))),
                   SNot(SAtomic(int))).canonicalize()
        self.assertIs(SAnd(td1, td2).canonicalize(NormalForm.DNF), SEmpty)
        self.assertIsNot(td1.disjoint(td2), False,
                         f"\ntd1={td1}\ntd2={td2}\ntd1.disjoint(td2) = {td1.disjoint(td2)}")

    def test_discovered_case_375c(self):
        from genus.depthgenerator import TestB, Test1
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        td1 = SAnd(SNot(SAtomic(TestB)),
                   SNot(SAtomic(int)),
                   SOr(SAtomic(Test1), even)).canonicalize(NormalForm.DNF)
        td2 = SAnd(SNot(SAnd(SNot(SAtomic(TestB)),
                             SOr(SAtomic(Test1), even))),
                   SNot(SAtomic(int))).canonicalize(NormalForm.DNF)
        self.assertIs(SAnd(td1, td2).canonicalize(NormalForm.DNF), SEmpty)
        self.assertIsNot(td1.disjoint(td2), False,
                         f"\ntd1={td1}\ntd2={td2}\ntd1.disjoint(td2) = {td1.disjoint(td2)}")

    def test_discovered_case_375d(self):
        from genus.depthgenerator import TestB, Test1
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        td1 = SAnd(SNot(SAtomic(TestB)),
                   SNot(SAtomic(int)),
                   SOr(SAtomic(Test1), even)).canonicalize(NormalForm.CNF)
        td2 = SAnd(SNot(SAnd(SNot(SAtomic(TestB)),
                             SOr(SAtomic(Test1), even))),
                   SNot(SAtomic(int))).canonicalize(NormalForm.CNF)
        self.assertIs(SAnd(td1, td2).canonicalize(NormalForm.DNF), SEmpty)
        self.assertIsNot(td1.disjoint(td2), False,
                         f"\n td1={td1}\n td2={td2}\n td1.disjoint(td2) = {td1.disjoint(td2)}")

    def test_discovered_case_297(self):
        from genus.depthgenerator import TestA, TestB
        self.assertTrue(True)
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        b = SAtomic(TestB)
        a = SAtomic(TestA)
        # [SAnd[SNot SAtomic(TestB)], [SNot[SOr[SAnd SAtomic(TestA), SAtomic(TestB)],
        #      [SAnd SAtomic(TestB), even?], [SAnd SAtomic( int), even?]]]]

        # this was an infinite loop.   calling .inhabited() here asserts that this is no longer an infinite loop

        # [SAnd[SNot[SAnd even?, [SOr SAtomic(TestB), SAtomic(int)]]], [SNot SAtomic(TestB)]]
        SAnd(SNot(SAnd(even,
                       SOr(b, SAtomic(int)))),
             SNot(b)).inhabited()

        # [SAnd[SNot SAtomic(TestB)], [SNot[SOr[SAnd SAtomic(TestB), even?], [SAnd SAtomic(int), even?]]]]
        SAnd(SNot(b), SNot(SOr(SAnd(b, even), SAnd(SAtomic(int), even)))).inhabited()

        SAnd(SNot(b),
             SNot(SOr(SAnd(a, b), SAnd(b, even),
                      SAnd(SAtomic(int), even)))).inhabited()

    def test_discovered_case_240(self):
        from genus.depthgenerator import Test2, TestA

        td1 = SAnd(SAtomic(Test2), SAtomic(TestA))
        td2 = SAnd(SAtomic(int), SAtomic(float))
        td3 = SAnd(SNot(td1), SNot(td2))
        td4 = SOr(td1, td2)
        td5 = SNot(td4)
        self.assertTrue(td2.inhabited() is False, f"{td2}.inhabited = {td2.inhabited()}")
        self.assertTrue(td3.subtypep(td4) is not True)
        self.assertTrue(td4.subtypep(td3) is not True)
        s = td5.subtypep(td3)
        self.assertTrue(s is not False,
                        f"td1={td1}\ntd2={td2} returned {s}")

    def test_subtypep1(self):
        from genus.depthgenerator import random_type_designator
        for depth in range(0, 3):
            for _ in range(num_random_tests):
                td1 = random_type_designator(depth)
                td2 = random_type_designator(depth)
                self.assertIs(td1.subtypep(td1), True)
                self.assertIsNot(SAnd(td1, td2).subtypep(td1), False,
                                 f"\n  td1={td1}\n  td2={td2}")
                self.assertIsNot(td1.subtypep(SOr(td1, td2)), False,
                                 f"\n  td1={td1}\n  td2={td2}")
                self.assertIsNot(SAnd(td1, td2).subtypep(SAnd(td2, td1)), False,
                                 f"\n  td1={td1}\n  td2={td2}")
                self.assertIsNot(SOr(td1, td2).subtypep(SOr(td2, td1)), False,
                                 f"td1={td1}\ntd2={td2}")
                self.assertIsNot(SAnd(td1, td2).subtypep(SOr(td1, td2)), False,
                                 f"\n  td1={td1}\n  td2={td2}")
                self.assertIsNot(SAnd(SNot(td1), SNot(td2)).subtypep(SNot(SOr(td1, td2))), False,
                                 f"\n  td1={td1}\n  td2={td2}")
                self.assertIsNot(SOr(SNot(td1), SNot(td2)).subtypep(SNot(SAnd(td1, td2))), False,
                                 f"\n  td1={td1}\n  td2={td2}")
                self.assertIsNot(SNot(SOr(td1, td2)).subtypep(SAnd(SNot(td1), SNot(td2))), False,
                                 f"td1={td1}\ntd2={td2}")
                self.assertIsNot(SNot(SAnd(td1, td2)).subtypep(SOr(SNot(td1), SNot(td2))), False,
                                 f"\n  td1={td1}\n  td2={td2}")

    def test_discovered_case_445(self):
        # td1 = SAnd(SOr([ = 0], SAtomic(Test2)), SAnd(SAtomic(TestA), odd?))
        # td2 = SOr(SOr(SAtomic(Test1), SAtomic(int)), SAnd([ = 3.14], [ =]))
        odd = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
        from genus.depthgenerator import Test2, Test1, TestA
        td1 = SAnd(SOr(SEql(0), SAtomic(Test2)),
                   SAnd(SAtomic(TestA), odd))

        td2 = SOr(SOr(SAtomic(Test1), SAtomic(int)),
                  SAnd(SEql(3.14), SEql("")))
        self.assertIsNot(SOr(SNot(td1), SNot(td2)).subtypep(SNot(SAnd(td1, td2))), False,
                         f"\n  td1={td1}\n  td2={td2}")

    def test_discovered_case_463(self):
        from genus.depthgenerator import Test2, Test1, TestA

        td1 = SAnd(SOr(SAtomic(int), SAtomic(Test2)),
                   SAtomic(TestA))
        td2 = SOr(SAtomic(Test1), SAtomic(int))
        self.assertIs(td1.disjoint(td2), True)
        self.assertIs(SAnd(td1, td2).subtypep_down(SNot(td1)), True,
                      f"\n  td1={td1}\n  td2={td2}")
        self.assertIs(SAnd(td1, td2).subtypep(SNot(td1)), True,
                      f"\n  td1={td1}\n  td2={td2}")
        self.assertIs(SAnd(td1, td2).subtypep(SNot(td2)), True)
        self.assertIs(SAnd(td1, td2).subtypep(SOr(SNot(td1), SNot(td2))), True)
        # since td1 and td2 are disjoint, the lhs and rhs are STop
        #   but subtypep gets the answer wrong
        self.assertIsNot(SOr(SNot(td1), SNot(td2)).inhabited(), False)
        self.assertIsNot(SNot(SAnd(td1, td2)).inhabited(), False)
        self.assertIs(SAnd(td1, td2).subtypep(td1), True)
        self.assertIs(td1.subtypep(SNot(SAnd(td1, td2))), True)
        self.assertIsNot(SNot(td1).subtypep(SNot(SAnd(td1, td2))), False,
                         f"\n  td1={td1}\n  td2={td2}")
        self.assertIsNot(SNot(td2).subtypep(SNot(SAnd(td1, td2))), False)
        self.assertIsNot(SOr(SNot(td1), SNot(td2)).subtypep_down(SNot(SAnd(td1, td2))), False,
                         f"\n  td1={td1}\n  td2={td2}")
        self.assertIsNot(SOr(SNot(td1), SNot(td2)).subtypep(SNot(SAnd(td1, td2))), False,
                         f"\n  td1={td1}\n  td2={td2}")

    def test_subtypep2(self):
        from genus.depthgenerator import random_type_designator
        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td = random_type_designator(depth)
                tdc1 = td.canonicalize()
                tdc2 = td.canonicalize(NormalForm.DNF)
                tdc3 = td.canonicalize(NormalForm.CNF)

                self.assertIsNot(td.subtypep(tdc1), False)
                self.assertIsNot(td.subtypep(tdc2), False)
                self.assertIsNot(td.subtypep(tdc3), False)
                self.assertIsNot(tdc1.subtypep(td), False,
                                 f"expecting tdc1={tdc1} subtype of {td} got {tdc1.subtypep(td)}")
                self.assertIsNot(tdc2.subtypep(td), False,
                                 f"expecting tdc2={tdc2} subtype of {td} got {tdc2.subtypep(td)}")
                self.assertIsNot(tdc3.subtypep(td), False,
                                 f"expecting tdc3={tdc3} subtype of {td} got {tdc3.subtypep(td)}")

    def test_uniquify(self):
        self.assertTrue(uniquify([]) == [])
        self.assertTrue(uniquify([1]) == [1])
        self.assertTrue(uniquify([5, 4, 3, 2, 1]) == [5, 4, 3, 2, 1])
        self.assertTrue(uniquify([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5])
        self.assertTrue(uniquify([1, 1, 1, 1, 1]) == [1])
        self.assertTrue(uniquify([1, 2, 1, 2]) == [1, 2])
        self.assertTrue(uniquify([1, 2, 1]) == [2, 1])

    def test_lazy(self):
        c = 0

        def g():
            nonlocal c
            c = c + 1
            return c

        self.assertTrue(c == 0)
        self.assertTrue(g() == 1)
        self.assertTrue(c == 1)

        f = generate_lazy_val(lambda: g())
        self.assertTrue(c == 1)
        self.assertTrue(f() == 2)
        self.assertTrue(c == 2)
        self.assertTrue(f() == 2)
        self.assertTrue(c == 2)

    def test_discovered_cases(self):
        def f(_a):
            return False

        self.assertTrue(SNot(SAtomic(int)).subtypep(SNot(SSatisfies(f, "f"))) is None)
        self.assertTrue(SAtomic(int).disjoint(SSatisfies(f, "f")) is None)
        self.assertTrue(SAtomic(int).disjoint(SNot(SSatisfies(f, "f"))) is None)
        self.assertTrue(SNot(SAtomic(int)).disjoint(SSatisfies(f, "f")) is None)
        self.assertTrue(SNot(SAtomic(int)).disjoint(SNot(SSatisfies(f, "f"))) is None)

        self.assertTrue(SAtomic(int).subtypep(SSatisfies(f, "f")) is None)
        self.assertTrue(SAtomic(int).subtypep(SNot(SSatisfies(f, "f"))) is None)
        self.assertTrue(SNot(SAtomic(int)).subtypep(SSatisfies(f, "f")) is None)

    def test_or(self):
        self.assertTrue(len(SOr(SEql(1), SEql(2)).tds) == 2)
        self.assertTrue(SOr().tds == [])

    def test_member(self):
        self.assertEqual(SMember(1, 2, 3).argpairs, [(SAtomic(int), 1), (SAtomic(int), 2), (SAtomic(int), 3)])
        self.assertEqual(SMember().argpairs, [])
        self.assertIs(SMember(1, 2, 3).subtypep(SMember(1, 2, 3, 4, 5)), True)
        self.assertIs(SMember(1, 2, 3).subtypep(SMember(1, 2)), False)
        self.assertIs(SMember(1, 2, 3).subtypep(SOr(SAtomic(str), SMember(1, 2, 3, 4, 5))), True)
        self.assertIs(SMember(1, 2, 3).subtypep(SAtomic(int)), True)

        self.assertEqual(SMember(1, 3, 1, 2, 3, 2).canonicalize(), SMember(1, 2, 3))
        self.assertEqual(SMember(3, 2, 1).canonicalize(), SMember(1, 2, 3))

    def test_eql(self):
        self.assertTrue(SEql(1).pair[1] == 1)
        self.assertTrue(SEql(1).argpairs == [(SAtomic(int), 1)],
                        f"expecting argpairs=[(SAtomic(int), 1)], got {SEql(1).argpairs}")

    def test_discovered_cases2(self):
        td = SAnd(SEql(3.14), SMember("a", "b", "c"))
        tdc = td.canonicalize()
        self.assertTrue(tdc == SEmpty, f"expecting td={td} to canonicalize to SEmpty, got {tdc}")

        td = SOr(SEql("a"), SAtomic(int))
        tdc = td.canonicalize()
        self.assertTrue(tdc != SAtomic(int))

    def test_membership(self):
        from genus.depthgenerator import random_type_designator, test_values
        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td = random_type_designator(depth)
                tdc1 = td.canonicalize()
                tdc2 = td.canonicalize(NormalForm.DNF)
                tdc3 = td.canonicalize(NormalForm.CNF)
                for v in test_values:
                    self.assertTrue(td.typep(v) == tdc1.typep(v),
                                    f"v={v} membership\n     of type   td={td} is {td.typep(v)}\n" +
                                    f" but of type tdc1={tdc1} is {tdc1.typep(v)}")
                    self.assertTrue(td.typep(v) == tdc2.typep(v),
                                    f"v={v} membership\n     of type   td={td} is {td.typep(v)}\n" +
                                    f" but of type tdc2={tdc2} is {tdc2.typep(v)}")
                    self.assertTrue(td.typep(v) == tdc3.typep(v),
                                    f"v={v} membership\n     of type   td={td} is {td.typep(v)}\n" +
                                    f" but of type tdc3={tdc3} is {tdc3.typep(v)}")

    def test_canonicalize_subtype(self):
        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td = random_type_designator(depth)
                tdc1 = td.canonicalize()
                tdc2 = td.canonicalize(NormalForm.DNF)
                tdc3 = td.canonicalize(NormalForm.CNF)
                for t1 in [td, tdc1, tdc2, tdc3]:
                    for t2 in [td, tdc1, tdc2, tdc3]:
                        self.assertTrue(t1.subtypep(t2) is not False)

    def test_combo_conversion1(self):
        self.assertTrue(SAnd().conversion1() == STop)
        self.assertTrue(SOr().conversion1() == SEmpty)
        self.assertTrue(SAnd(SEql(1)).conversion1() == SEql(1))
        self.assertTrue(SOr(SEql(1)).conversion1() == SEql(1))

    def test_combo_conversion2(self):
        # (and A B SEmpty C D) -> SEmpty,  unit=STop,   zero=SEmpty
        # (or A B STop C D) -> STop,     unit=SEmpty,   zero=STop
        a = SEql("a")
        b = SEql("b")
        c = SEql("c")
        d = SEql("d")
        self.assertTrue(SAnd(a, b, SEmpty, c, d).conversion2() == SEmpty)
        self.assertTrue(SOr(a, b, SEmpty, c, d).conversion2() == SOr(a, b, SEmpty, c, d))
        self.assertTrue(SAnd(a, b, STop, c, d).conversion2() == SAnd(a, b, STop, c, d))
        self.assertTrue(SOr(a, b, STop, c, d).conversion2() == STop)

    def test_combo_conversion3(self):
        # (and A (not A)) --> SEmpty,  unit=STop,   zero=SEmpty
        # (or A (not A)) --> STop,     unit=SEmpty, zero=STop
        a = SEql("a")
        self.assertTrue(SAnd(a, SNot(a)).conversion3() == SEmpty)
        self.assertTrue(SOr(a, SNot(a)).conversion3() == STop)

    def test_combo_conversion4(self):
        # SAnd(A,STop,B) ==> SAnd(A,B),  unit=STop,   zero=SEmpty
        # SOr(A,SEmpty,B) ==> SOr(A,B),  unit=SEmpty, zero=STop
        a = SEql("a")
        b = SEql("b")
        self.assertTrue(SAnd(a, STop, b).conversion4() == SAnd(a, b))
        self.assertTrue(SOr(a, STop, b).conversion4() == SOr(a, STop, b))
        self.assertTrue(SAnd(a, SEmpty, b).conversion4() == SAnd(a, SEmpty, b))
        self.assertTrue(SOr(a, SEmpty, b).conversion4() == SOr(a, b))

    def test_combo_conversion5(self):
        # (and A B A C) -> (and A B C)
        # (or A B A C) -> (or A B C)
        a = SEql("a")
        b = SEql("b")
        c = SEql("c")
        self.assertTrue(SAnd(a, b, a, c).conversion5() == SAnd(b, a, c))
        self.assertTrue(SOr(a, b, a, c).conversion5() == SOr(b, a, c))

    def test_combo_conversion6(self):
        # (and A ( and B C) D) --> (and A B C D)
        # (or A ( or B C) D) --> (or A B C D)
        a = SEql("a")
        b = SEql("b")
        c = SEql("c")
        d = SEql("d")
        self.assertTrue(SAnd(a, SAnd(b, c), d).conversion6() == SAnd(a, b, c, d))
        self.assertTrue(SOr(a, SAnd(b, c), d).conversion6() == SOr(a, SAnd(b, c), d))
        self.assertTrue(SOr(a, SAnd(b, c), d).conversion6() == SOr(a, SAnd(b, c), d))
        self.assertTrue(SOr(a, SOr(b, c), d).conversion6() == SOr(a, b, c, d))

    def test_combo_conversion98(self):
        a = SEql("a")
        b = SEql("b")
        c = SEql("c")
        d = SEql("d")
        self.assertTrue(SAnd(b, c, a, d).conversion98() == SAnd(a, b, c, d), f"got {SAnd(b, c, a, d).conversion98()}")
        self.assertTrue(SOr(b, c, a, d).conversion98() == SOr(a, b, c, d))

    def test_combo_conversion8(self):
        # (or A ( not B)) --> STop if B is subtype of A, zero = STop
        # (and A ( not B)) --> SEmpty if B is supertype of A, zero = SEmpty
        a = SEql("a")
        ab = SMember("a", "b")
        c = SEql("c")
        self.assertTrue(a.subtypep(ab) is True)
        self.assertTrue(ab.supertypep(a) is True)

        self.assertTrue(SAnd(a, SNot(ab), c).conversion8() == SEmpty)
        self.assertTrue(SAnd(SNot(a), ab, c).conversion8() == SAnd(SNot(a), ab, c))

        self.assertTrue(SOr(a, SNot(ab), c).conversion8() == SOr(a, SNot(ab), c))
        self.assertTrue(SOr(SNot(a), ab, c).conversion8() == STop)

    def test_combo_conversion9(self):
        # (A + B + C)(A + !B + C)(X) -> (A + B + C)(A + C)(X)
        # (A + B +!C)(A +!B + C)(A +!B+!C) -> (A + B +!C)(A + !B + C)(A + !C)
        # (A + B +!C)(A +!B + C)(A +!B+!C) -> does not reduce to(A + B + !C)(A +!B+C)(A)
        a = SEql("a")
        b = SEql("b")
        c = SEql("c")
        x = SEql("x")
        self.assertTrue(SAnd(SOr(a, b, c),
                             SOr(a, SNot(b), c),
                             x).conversion9() == SAnd(SOr(a, b, c),
                                                      SOr(a, c),
                                                      x))
        self.assertTrue(SAnd(SOr(a, b, SNot(c)),
                             SOr(a, SNot(b), c),
                             SOr(a, SNot(b), SNot(c))).conversion9() == SAnd(SOr(a, b, SNot(c)),
                                                                             SOr(a, SNot(b), c),
                                                                             SOr(a, SNot(c))))
        self.assertTrue(SAnd(SOr(a, b, SNot(c)),
                             SOr(a, SNot(b), c),
                             SOr(a, SNot(b), SNot(c))).conversion9() ==
                        SAnd(SOr(a, b, SNot(c)),
                             SOr(a, SNot(b), c),
                             SOr(a, SNot(c))))

        self.assertTrue(SOr(SAnd(a, b, c), SAnd(a, SNot(b), c), x).conversion9() == SOr(SAnd(a, b, c), SAnd(a, c), x))
        self.assertTrue(SOr(SAnd(a, b, SNot(c)),
                            SAnd(a, SNot(b), c),
                            SAnd(a, SNot(b), SNot(c))).conversion9() ==
                        SOr(SAnd(a, b, SNot(c)), SAnd(a, SNot(b), c), SAnd(a, SNot(c))))
        self.assertTrue(SOr(SAnd(a, b, SNot(c)),
                            SAnd(a, SNot(b), c),
                            SAnd(a, SNot(b), SNot(c))).conversion9() ==
                        SOr(SAnd(a, b, SNot(c)), SAnd(a, SNot(b), c), SAnd(a, SNot(c))))

    def test_combo_conversion10(self):
        # (and A B C) --> (and A C) if A is subtype of B
        # (or A B C) -->  (or B C) if A is subtype of B
        a = SEql("a")
        ab = SMember("a", "b")
        c = SEql("c")
        self.assertTrue(a.subtypep(ab) is True)
        self.assertTrue(ab.supertypep(a) is True)
        self.assertTrue(SAnd(a, ab, c).conversion10() == SAnd(a, c))
        self.assertTrue(SOr(a, ab, c).conversion10() == SOr(ab, c))

    def test_combo_conversion11(self):
        # A + A! B -> A + B
        # A + A! BX + Y = (A + BX + Y)
        # A + ABX + Y = (A + Y)
        a = SEql("a")
        b = SEql("b")
        x = SEql("x")
        y = SEql("y")
        self.assertTrue(SOr(a, SAnd(SNot(a), b)).conversion11() == SOr(a, b))
        self.assertTrue(SOr(a, SAnd(SNot(a), b, x), y).conversion11() == SOr(a, SAnd(b, x), y))
        self.assertTrue(SOr(a, SAnd(a, b, x), y).conversion11() == SOr(a, y))

        self.assertTrue(SAnd(a, SOr(SNot(a), b)).conversion11() == SAnd(a, b))
        self.assertTrue(SAnd(a, SOr(SNot(a), b, x), y).conversion11() == SAnd(a, SOr(b, x), y))
        self.assertTrue(SAnd(a, SOr(a, b, x), y).conversion11() == SAnd(a, y))

    def test_combo_conversion12(self):
        # AXBC + !X = ABC + !X
        a = SEql("a")
        b = SEql("b")
        c = SEql("c")
        x = SEql("x")
        self.assertTrue(SOr(SAnd(a, x, b, c), SNot(x)).conversion12() == SOr(SAnd(a, b, c), SNot(x)))
        self.assertTrue(SAnd(SOr(a, x, b, c), SNot(x)).conversion12() == SAnd(SOr(a, b, c), SNot(x)))

    def test_combo_conversion13(self):
        # multiple !member
        # SOr(x,!{-1, 1},!{1, 2, 3, 4})
        # --> SOr(x,!{1}) // intersection of non-member
        # SAnd(x,!{-1, 1},!{1, 2, 3, 4})
        # --> SOr(x,!{-1, 1, 2, 3, 4}) // union of non-member
        x = SAtomic(int)

        self.assertTrue(SOr(x,
                            SNot(SMember(-1, 1)),
                            SNot(SMember(1, 2, 3, 4))).conversion13() == SOr(x,
                                                                             SNot(SEql(1))))
        self.assertTrue(SAnd(x,
                             SNot(SMember(-1, 1)),
                             SNot(SMember(1, 2, 3, 4))).conversion13() == SAnd(x,
                                                                               SNot(SMember(-1, 1, 2, 3, 4))))

    def test_combo_conversion14(self):
        # multiple member
        # (or (member 1 2 3) (member 2 3 4 5)) --> (member 1 2 3 4 5)
        # (and (member 1 2 3) (member 2 3 4 5)) --> (member 2 3)
        x = SAtomic(int)
        self.assertTrue(SOr(x, SMember(1, 2, 3), SMember(2, 3, 4, 5)).conversion14() == SOr(x, SMember(1, 2, 3, 4, 5)))
        self.assertTrue(SAnd(x, SMember(1, 2, 3), SMember(2, 3, 4, 5)).conversion14() == SAnd(x, SMember(2, 3)))

    def test_combo_conversion15(self):
        x = SAtomic(int)
        self.assertTrue(
            SOr(x, SMember(0, 1, 2, 3), SNot(SMember(2, 3, 4, 5))).conversion15() == SOr(x, SNot(SMember(4, 5))))
        self.assertTrue(
            SAnd(x, SMember(0, 1, 2, 3), SNot(SMember(2, 3, 4, 5))).conversion15() == SAnd(x, SMember(0, 1)))

    def test_combo_conversion16(self):
        self.assertTrue(SAnd(SEql("a"), SAtomic(int)).conversion16() == SAnd(SEmpty, SAtomic(int)))
        self.assertTrue(SOr(SEql("a"), SAtomic(int)).conversion16() == SOr(SEql("a"), SAtomic(int)))
        # SAnd check for confusing of float and integer
        self.assertEqual(
            SAnd(SAtomic(float), SMember(1, 1.0, 2, 2.0)).conversion16(),
            SAnd(SAtomic(float), SMember(1.0, 2.0)))
        self.assertNotEqual(
            SAnd(SAtomic(float), SMember(1, 1.0, 2, 2.0)).conversion16(),
            SAnd(SAtomic(float), SMember(1, 2)))

        self.assertEqual(
            SAnd(SAtomic(int), SMember(1, 1.0, 2, 2.0)).conversion16(),
            SAnd(SAtomic(int), SMember(1, 2)))
        self.assertNotEqual(
            SAnd(SAtomic(int), SMember(1, 1.0, 2, 2.0)).conversion16(),
            SAnd(SAtomic(int), SMember(1.0, 2.0)))

        self.assertEqual(
            SAnd(SAtomic(float), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SAnd(SAtomic(float), SNot(SMember(1.0, 2.0))))
        self.assertNotEqual(
            SAnd(SAtomic(float), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SAnd(SAtomic(float), SNot(SMember(1, 2))))

        self.assertEqual(
            SAnd(SAtomic(int), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SAnd(SAtomic(int), SNot(SMember(1, 2))))
        self.assertNotEqual(
            SAnd(SAtomic(int), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SAnd(SAtomic(int), SNot(SMember(1.0, 2.0))))

        # SOr check for confusing of float and integer
        self.assertEqual(
            SOr(SAtomic(float), SMember(1, 1.0, 2, 2.0)).conversion16(),
            SOr(SAtomic(float), SMember(1, 2)))
        self.assertNotEqual(
            SOr(SAtomic(float), SMember(1, 1.0, 2, 2.0)).conversion16(),
            SOr(SAtomic(float), SMember(1.0, 2.0)))

        self.assertEqual(
            SOr(SAtomic(int), SMember(1, 1.0, 2, 2.0)).conversion16(),
            SOr(SAtomic(int), SMember(1.0, 2.0)))
        self.assertEqual(
            SOr(SAtomic(int), SMember(1, 1.0, 2, 2.0), SMember(3, 3.0, 4, 4.0)).conversion16(),
            SOr(SAtomic(int), SMember(1.0, 2.0), SMember(3.0, 4.0)))
        self.assertNotEqual(
            SOr(SAtomic(int), SMember(1, 1.0, 2, 2.0)).conversion16(),
            SOr(SAtomic(int), SMember(1, 2)))
        self.assertNotEqual(
            SOr(SAtomic(int), SMember(1, 1.0, 2, 2.0), SMember(3, 3.0, 4, 4.0)).conversion16(),
            SOr(SAtomic(int), SMember(1, 2), SMember(3, 4)))

        self.assertEqual(
            SOr(SAtomic(float), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SOr(SAtomic(float), SNot(SMember(1, 2))))
        self.assertNotEqual(
            SOr(SAtomic(float), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SOr(SAtomic(float), SNot(SMember(1.0, 2.0))))

        self.assertEqual(
            SOr(SAtomic(int), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SOr(SAtomic(int), SNot(SMember(1.0, 2.0))))
        self.assertNotEqual(
            SOr(SAtomic(int), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SOr(SAtomic(int), SNot(SMember(1, 2))))

        self.assertEqual(
            SOr(SAtomic(int), SNot(SMember(1, 1.0, 2, 2.0)), SNot(SMember(3, 3.0, 4, 4.0))).conversion16(),
            SOr(SAtomic(int), SNot(SMember(1.0, 2.0)), SNot(SMember(3.0, 4.0))))
        self.assertNotEqual(
            SOr(SAtomic(int), SNot(SMember(1, 1.0, 2, 2.0))).conversion16(),
            SOr(SAtomic(int), SNot(SMember(1, 2))))

    def test_conversion17(self):
        odd = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        t0 = SOr(SAnd(SNot(odd), even), SAnd(even,odd))
        assert t0.conversion17() == SOr(even, even)
        assert t0.canonicalize() == even, f"canonicalize = {t0.canonicalize()}"

        t1 = SAnd(SOr(SNot(odd),even), SOr(even,odd))
        assert t1.conversion17() == SAnd(even, even)
        assert t1.canonicalize() == even
        a = SEql("a")
        b = SEql("b")
        c = SEql("c")
        d = SEql("d")
        self.assertEqual( SOr(SAnd(a,b,c),
                             SAnd(a,SNot(b),c)).conversion17(),
                          SOr(SAnd(a,c),SAnd(a,c)))
        self.assertEqual( SAnd(SOr(a,b,c),SOr(a,SNot(b),c)).conversion17(),
                          SAnd(SOr(a,c),SOr(a,c)))

        self.assertEqual( SOr(SAnd(a, b, c, d), SAnd(a, SNot(b), c, d)).conversion17(),
                          SOr(SAnd(a, c, d), SAnd(a, c, d)))
        self.assertEqual( SAnd(SOr(a, b, c, d), SOr(a, SNot(b), c, d)).conversion17(),
                          SAnd(SOr(a, c, d), SOr(a, c, d)))

        self.assertEqual( SOr(SAnd(a, b, c, d), SAnd(a, SNot(b), c, SNot(d))).conversion17(),
                          SOr(SAnd(a, b, c, d), SAnd(a, SNot(b), c, SNot(d))))
        self.assertEqual( SAnd(SOr(a, b, c, d), SOr(a, SNot(b), c, SNot(d))).conversion17(),
                          SAnd(SOr(a, b, c, d), SOr(a, SNot(b), c, SNot(d))))

    def test_combo_conversionD1(self):
        # SOr(SNot(SMember(42, 43, 44, "a","b")), String)
        # == > SNot(SMember(42, 43, 44))
        self.assertTrue(
            SOr(SNot(SMember(1, 2, 3, "a", "b", "c")), SAtomic(int)).conversionD1() == SNot(SMember("a", "b", "c")))

        # to SAnd(SMember(42, 43, 44), SInt)
        # while conversionA1() converts it to
        # SMember(42, 43, 44)
        self.assertTrue(SAnd(SMember(1, 2, 3, "a", "b", "c"), SAtomic(int)).conversionD1() == SMember(1, 2, 3))

    def test_combo_conversionD3(self):
        # find disjoint pair
        self.assertTrue(SAnd(SMember(1, 2), SMember(3, 4)).conversionD3() == SEmpty)
        self.assertTrue(SAnd(SMember("a", "b"), SAtomic(int)).conversionD3() == SEmpty)
        self.assertTrue(
            SAnd(SMember(1, 2, "a", "b"), SAtomic(int)).conversionD3() == SAnd(SMember(1, 2, "a", "b"), SAtomic(int)))

        self.assertTrue(SOr(SNot(SMember(1, 2)), SNot(SMember(3, 4))).conversionD3() == STop)
        self.assertTrue(SOr(SNot(SMember("a", "b")), SNot(SAtomic(int))).conversionD3() == STop)
        self.assertTrue(SOr(SNot(SMember(1, 2, "a", "b")), SNot(SAtomic(int))).conversionD3() ==
                        SOr(SNot(SMember(1, 2, "a", "b")), SNot(SAtomic(int))))

    def test_discovered_cases3(self):
        class Test1:
            pass

        self.assertTrue(SNot(SAtomic(Test1)).subtypep(SAtomic(int)) is False)
        self.assertTrue(SAtomic(int).subtypep(SAtomic(Test1)) is False)
        self.assertTrue(SAtomic(Test1).subtypep(SAtomic(int)) is False)
        self.assertTrue(SAtomic(int).subtypep(SNot(SAtomic(Test1))) is True)
        self.assertTrue(SAtomic(Test1).subtypep(SNot(SAtomic(int))) is True)
        self.assertTrue(SNot(SAtomic(int)).subtypep(SAtomic(Test1)) is False)
        self.assertTrue(SAnd(SAtomic(int), SNot(SAtomic(Test1))).canonicalize() == SAtomic(int))
        self.assertTrue(SOr(SAtomic(int), SNot(SAtomic(Test1))).canonicalize() == SNot(SAtomic(Test1)))

    def test_depth_generator(self):
        from genus.depthgenerator import DepthGenerator
        self.assertTrue(self)
        rand_lambda = DepthGenerator(2).rand_lambda_str_generator()
        for i in range(10):
            rand_lambda[0](i)
        DepthGenerator(5).generate_tree()

    def test_discovered_cases4(self):
        self.assertTrue(SNot(SEmpty).canonicalize() == STop)
        self.assertTrue(SAtomic(float).disjoint(SEmpty) is True)
        self.assertTrue(SAtomic(float).inhabited() is True)
        self.assertTrue(SNot(SEmpty).inhabited() is True)
        self.assertTrue(SAtomic(float).subtypep(SEmpty) is False)
        self.assertTrue(SAtomic(float).disjoint(SNot(SEmpty)) is not True)
        self.assertTrue(SAnd(SAtomic(float), SNot(SEmpty)).canonicalize() == SAtomic(float))

    def test_canonicalize_cache(self):
        a = SEql("a")
        td = SOr(a, a, a)
        self.assertTrue(td.canonicalized_hash == {})
        tdc = td.canonicalize()
        self.assertTrue(td.canonicalized_hash[None] == tdc)
        self.assertTrue(tdc.canonicalized_hash[None] == tdc)

        tdc2 = td.canonicalize(NormalForm.DNF)
        self.assertTrue(td.canonicalized_hash[NormalForm.DNF] == tdc2)
        self.assertTrue(tdc2.canonicalized_hash[NormalForm.DNF] == tdc2)

        tdc3 = td.canonicalize(NormalForm.CNF)
        self.assertTrue(td.canonicalized_hash[NormalForm.CNF] == tdc3)
        self.assertTrue(tdc3.canonicalized_hash[NormalForm.CNF] == tdc3)

    def test_to_dnf2(self):

        def termp(td):
            if isinstance(td, TerminalType):
                return True
            elif notp(td) and isinstance(td.s, TerminalType):
                return True
            else:
                return False

        def andTermp(td):
            return andp(td) and all(termp(td2) for td2 in td.tds)

        def dnfp(td):
            if termp(td):
                return True
            elif andp(td):
                return andTermp(td)
            elif orp(td):
                return all(termp(td2) or andTermp(td2) for td2 in td.tds)
            else:
                return False

        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td = random_type_designator(depth)
                dnf = td.canonicalize(NormalForm.DNF)
                self.assertTrue(dnfp(dnf), f"expecting DNF, got {dnf}")

    def test_to_cnf2(self):
        def termp(td):
            if isinstance(td, TerminalType):
                return True
            elif notp(td) and isinstance(td.s, TerminalType):
                return True
            else:
                return False

        def orTermp(td):
            return orp(td) and all(termp(td2) for td2 in td.tds)

        def cnfp(td):
            if termp(td):
                return True
            elif orp(td):
                return orTermp(td)
            elif andp(td):
                return all(termp(td2) or orTermp(td2) for td2 in td.tds)
            else:
                return False

        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td = random_type_designator(depth)
                cnf = td.canonicalize(NormalForm.CNF)
                self.assertTrue(cnfp(cnf), f"expecting DNF, got {cnf}")

    def test_to_dnf(self):
        # convert SAnd( x1, x2, SOr(y1,y2,y3), x3, x4)
        #    --> td = SOr(y1,y2,y3)
        # --> SOr(SAnd(x1,x2,  y1,  x3,x4),
        #          SAnd(x1,x2,  y2,  x3,x4),
        #          SAnd(x1,x2,  y3,  x3,x4),
        #     )

        x1 = SEql("x1")
        x2 = SEql("x2")
        x3 = SEql("x3")
        x4 = SEql("x4")
        y1 = SEql("y1")
        y2 = SEql("y2")
        y3 = SEql("y3")
        td = SAnd(x1, x2, SOr(y1, y2, y3), x3, x4)
        dnf = SOr(SAnd(x1, x2, y1, x3, x4),
                  SAnd(x1, x2, y2, x3, x4),
                  SAnd(x1, x2, y3, x3, x4))
        self.assertTrue(td.compute_dnf() == dnf)
        self.assertTrue(td.to_nf(NormalForm.DNF) == dnf)
        self.assertTrue(td.to_nf(NormalForm.CNF) == td)
        self.assertTrue(td.compute_cnf() == td)

    def test_to_cnf(self):
        # convert SOr( x1, x2, SAnd(y1,y2,y3), x3, x4)
        #    --> td = SAnd(y1,y2,y3)
        # --> SAnd(SOr(x1,x2,  y1,  x3,x4),
        #          SOr(x1,x2,  y2,  x3,x4),
        #          SOr(x1,x2,  y3,  x3,x4),
        #     )
        x1 = SEql("x1")
        x2 = SEql("x2")
        x3 = SEql("x3")
        x4 = SEql("x4")
        y1 = SEql("y1")
        y2 = SEql("y2")
        y3 = SEql("y3")
        td = SOr(x1, x2, SAnd(y1, y2, y3), x3, x4)
        cnf = SAnd(SOr(x1, x2, y1, x3, x4),
                   SOr(x1, x2, y2, x3, x4),
                   SOr(x1, x2, y3, x3, x4))
        self.assertTrue(td.compute_cnf() == cnf)
        self.assertTrue(td.to_nf(NormalForm.CNF) == cnf)
        self.assertTrue(td.to_nf(NormalForm.DNF) == td)
        self.assertTrue(td.compute_dnf() == td)

    def test_discovered_cases_867(self):
        class Test1:
            pass

        self.assertTrue(SAtomic(float).subtypep(SNot(SEmpty)) is True)
        self.assertTrue(SNot(SAtomic(Test1)).subtypep(SAtomic(Test1)) is False)

    def test_compare_sequence(self):
        self.assertTrue(compare_sequence([SEql(1)], [SEql(2)]) < 0)
        self.assertTrue(compare_sequence([], []) == 0)
        self.assertTrue(compare_sequence([SEql(1)], [SEql(1)]) == 0)
        self.assertTrue(compare_sequence([SEql(2)], [SEql(1)]) > 0)
        self.assertTrue(compare_sequence([SEql(1), SEql(1)], [SEql(1), SEql(1)]) == 0)
        self.assertTrue(compare_sequence([SEql(1), SEql(2)], [SEql(1), SEql(1)]) > 0,
                        f"returned {compare_sequence([SEql(1), SEql(2)], [SEql(1), SEql(1)])}")
        self.assertTrue(compare_sequence([SEql(1), SEql(1)], [SEql(1), SEql(2)]) < 0)

        self.assertTrue(compare_sequence([SEql(1), SEql(1)], [SEql(1)]) > 0)  # short list < long list
        self.assertTrue(compare_sequence([SEql(1)], [SEql(1), SEql(1)]) < 0)

        self.assertTrue(cmp_objects(SEql(1), SEql(2)) < 0)
        self.assertTrue(cmp_objects(SEql(1), SEql(1)) == 0)
        self.assertTrue(cmp_objects(SEql(2), SEql(1)) > 0)

        self.assertTrue(cmp_objects(SMember(1), SMember(1)) == 0)
        self.assertTrue(cmp_objects(SMember(1), SMember(2)) < 0)
        self.assertTrue(cmp_objects(SMember(2), SMember(1)) > 0)
        self.assertTrue(cmp_objects(SMember(1), SMember(1, 2)) < 0)  # short list < long list
        self.assertTrue(cmp_objects(SMember(1, 2), SMember(1)) > 0)
        self.assertTrue(cmp_objects(SMember(1, 2), SMember(1, 2)) == 0)
        self.assertTrue(cmp_objects(SMember(1, 2), SMember(1, 3)) < 0)
        self.assertTrue(cmp_objects(SMember(1, 2), SMember(1, 1)) > 0)

        self.assertTrue(cmp_objects(SEql(1), SMember(1, 1)) < 0)  # compare alphabetically
        self.assertTrue(cmp_objects(SMember(1, 2), SEql(1)) > 0)

        self.assertTrue(cmp_objects(SAnd(SEql(1), SEql(2)), SAnd(SEql(1), SEql(2))) == 0)
        self.assertTrue(cmp_objects(SAnd(SEql(1), SEql(2)), SAnd(SEql(2), SEql(1))) < 0)
        self.assertTrue(cmp_objects(SAnd(SEql(2), SEql(2)), SAnd(SEql(2), SEql(1))) > 0)

        self.assertTrue(cmp_objects(SOr(SEql(2), SEql(1)), SOr(SEql(2), SEql(2))) < 0)
        self.assertTrue(cmp_objects(SOr(SEql(2), SEql(3)), SOr(SEql(2), SEql(2))) > 0)
        self.assertTrue(cmp_objects(SAnd(SEql(2), SEql(2)), SAnd(SEql(2), SEql(2))) == 0)

        self.assertTrue(cmp_objects(SOr(SEql(2), SEql(1)), SAnd(SEql(2), SEql(2))) > 0)  # alphabetical
        self.assertTrue(cmp_objects(SAnd(SEql(2), SEql(1)), SOr(SEql(2), SEql(2))) < 0)

        self.assertTrue(cmp_objects(SNot(SEql(1)), SNot(SEql(2))) < 0)
        self.assertTrue(cmp_objects(SNot(SEql(1)), SNot(SEql(1))) == 0)
        self.assertTrue(cmp_objects(SNot(SEql(2)), SNot(SEql(1))) > 0)

        self.assertTrue(cmp_objects(STop, STop) == 0)
        self.assertTrue(cmp_objects(SEmpty, SEmpty) == 0)
        self.assertTrue(cmp_objects(SEmpty, STop) < 0)
        self.assertTrue(cmp_objects(STop, SEmpty) > 0)

        self.assertTrue(cmp_objects(SAtomic(int), SAtomic(int)) == 0)
        self.assertTrue(cmp_objects(SAtomic(int), SAtomic(str)) < 0)
        self.assertTrue(cmp_objects(SAtomic(str), SAtomic(int)) > 0)

        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        odd = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
        self.assertTrue(cmp_objects(even, even) == 0)
        self.assertTrue(cmp_objects(even, odd) < 0, f"expecting {even} < {odd}")  # alphabetical by printable
        self.assertTrue(cmp_objects(odd, even) > 0)

    def test_mdtd(self):
        for depth in range(0, 4):
            for length in range(1, 5):
                for _ in range(num_random_tests):
                    tds = [random_type_designator(depth) for _ in range(length)]
                    computed = mdtd(tds)
                    for i in range(len(computed)):
                        td_i, factors_i, disjoints_i = computed[i]
                        for j in range(i + 1, len(computed)):
                            td_j, factors_j, disjoints_j = computed[j]
                            cc = td_i.disjoint(td_j)
                            intersection = SAnd(td_i, td_j).canonicalize(NormalForm.DNF)
                            self.assertTrue(cc is not False,
                                            f"\n tds={tds}" +
                                            f"\n mdtd={computed}" +
                                            f"\n {td_i}.disjoint({cc})" +
                                            f"\n intersection = {intersection}")

                    for v in test_values:
                        containing = [td for (td, factors, disjoint) in computed if td.typep(v)]
                        self.assertEqual(len(containing), 1,
                                         f"expecting exactly one partition to contain v={v}" +
                                         f"\n tds={tds}\n mdtd={computed}\n containing={containing}")

    def test_trace_graph(self):
        def edges(i):  # V => List[(L,V)]
            if i == 0:
                return [("a", 1), ("b", 2)]
            elif i == 1:
                return [("a", 2)]
            else:
                return [("b", 2), ("a", 0)]

        self.assertEqual(trace_graph(0, edges),
                         ([0, 1, 2], [[("a", 1), ("b", 2)],
                                      [("a", 2)],
                                      [("b", 2), ("a", 0)]]))

    def test_discovered_case_1018(self):
        from genus.depthgenerator import Test2
        odd = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
        self.assertIs(SOr(SAtomic(Test2), odd).subtypep(SOr(odd, SAtomic(Test2))), True)

    def test_discovered_case_134(self):  # test case copied from clojure code
        self.assertIs(SNot(SMember(1, 2, 3)).disjoint(SNot(SAtomic(str))), False)
        self.assertIs(SAnd(SNot(SMember(1, 2, 3)), SNot(SAtomic(str))).inhabited(), True)
        self.assertIs(SAnd(SNot(SMember(1, 2, 3)), SNot(SAtomic(str))).disjoint(STop), False)

    def test_group_by(self):
        from genus.utils import group_by
        grouped = group_by(lambda n: n % 3, [1, 2, 3, 4, 10, 11, 12])
        self.assertEqual(set(grouped[0]), {3, 12})
        self.assertEqual(set(grouped[1]), {1, 4, 10})
        self.assertEqual(set(grouped[2]), {2, 11})

    def test_find_eqv_class(self):
        from genus.utils import find_eqv_class
        self.assertEqual((1, 2, 3), find_eqv_class([(1, 2, 3), (4, 5, 6)], 2))
        self.assertIsNone(find_eqv_class([(1, 2, 3), (4, 5, 6)], 0))

    def test_split_eqv_class(self):
        from genus.utils import split_eqv_class
        partition = split_eqv_class((1, 2, 3, 10, 11, 12), lambda n: n % 3)
        self.assertTrue((1, 10) in partition)
        self.assertTrue((2, 11) in partition)
        self.assertTrue((3, 12) in partition)

    def test_transition_to_ite(self):
        from genus.ite import transitions_to_ite
        self.assertEqual(transitions_to_ite([], default=None), (None,))
        self.assertEqual(transitions_to_ite([(STop, 42)], None), (42,))
        self.assertEqual(transitions_to_ite([(SEmpty, 42)], None), (None,))
        self.assertEqual(transitions_to_ite([(SEmpty, 42),
                                             (STop, 43)], None), (43,))
        self.assertEqual(transitions_to_ite([(SAtomic(int), 42),
                                             (SAtomic(str), 43)], None),
                         (SAtomic(int), (42,),
                          (SAtomic(str), (43,), (None,))))
        self.assertEqual(transitions_to_ite([(SOr(SAtomic(int),
                                                  SEql("hello")), 42),
                                             (SAtomic(str), 43)], None),
                         (SAtomic(int), (42,),
                          (SEql("hello"), (42,),
                           (SAtomic(str), (43,), (None,)))))
        self.assertEqual(transitions_to_ite([(SNot(SEql("hello")), 41),
                                             (SOr(SAtomic(int),
                                                  SEql("hello")), 42),
                                             (SAtomic(str), 43)], None),
                         (SEql("hello"), (42,), (41,)))

        self.assertEqual(transitions_to_ite([(SMember(1, 2, 3), 42),
                                             (SMember(1, 2), 43),
                                             (SMember(1), 44)]),
                         (SMember(1, 2, 3), (42,), (None,)))

        self.assertEqual(transitions_to_ite([(SMember(1, 2), 43),
                                             (SMember(1, 2, 3), 42),
                                             (SMember(1), 44)]),
                         (SMember(1, 2), (43,), (SEql(3), (42,), (None,))))

        self.assertEqual(transitions_to_ite([(SOr(SMember(1, 2), SAtomic(tuple)), 43),
                                             (SOr(SMember(1, 2, 3), SAtomic(str)), 42),
                                             (SOr(SMember(1), SAtomic(list)), 44)]),
                         (SAtomic(tuple),
                          (43,),
                          (SMember(1, 2),
                           (43,),
                           (SAtomic(str), (42,), (SEql(3), (42,), (SAtomic(list), (44,), (None,)))))))

        class TestX:
            pass

        class TestY(TestX):
            pass

        class Test1:
            pass

        class Test2(Test1):
            pass

        self.assertEqual(transitions_to_ite([(SOr(SAtomic(TestX), SAtomic(Test2)), 44),
                                             (SOr(SAtomic(TestY), SAtomic(Test1)), 43)]),
                         (SAtomic(Test2),
                          (44,),
                          (SAtomic(TestX), (44,), (SAtomic(Test1), (43,), (None,)))))

        self.assertEqual(transitions_to_ite([(SOr(SAtomic(TestY), SAtomic(Test1)), 44),
                                             (SOr(SAtomic(TestX), SAtomic(Test2)), 43)]),
                         (SAtomic(Test1),
                          (44,),
                          (SAtomic(TestY), (44,), (SAtomic(TestX), (43,), (None,)))))
        self.assertEqual(transitions_to_ite([(SNot(SOr(SAtomic(TestY), SAtomic(Test1))), 44),
                                             (SOr(SAtomic(TestX), SAtomic(Test2)), 43)]),
                         (SAtomic(Test1),
                          (SAtomic(Test2), (43,), (None,)),
                          (SAtomic(TestY), (43,), (44,))))

    def test_ite_2(self):
        from genus.ite import transitions_to_ite, eval_ite
        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td = random_type_designator(depth)
                ite = transitions_to_ite([(td, True)], False)
                for v in test_values:
                    self.assertIs(eval_ite(ite, v), td.typep(v))

    def test_ite_3(self):
        from genus.ite import transitions_to_ite, eval_ite
        for depth in range(0, 4):
            for _ in range(num_random_tests * 5):
                td1 = random_type_designator(depth)
                td2 = SAnd(random_type_designator(depth), SNot(td1))
                ite = transitions_to_ite([(td2, 2),
                                          (td1, 1)], 3)
                for v in test_values:
                    if td1.typep(v):
                        expected = 1
                    elif td2.typep(v):
                        expected = 2
                    else:
                        expected = 3

                    self.assertIs(eval_ite(ite, v), expected)

    def test_typeEquivalent_random(self):
        import random
        for i in range(0, 1000):
            d = random.randint(0, 4)
            t1 = random_type_designator(d)
            t2 = random_type_designator(d)

            self.assertTrue(t1.typeEquivalent(t1))
            self.assertTrue(t1.typeEquivalent(SNot(t1)) is not True)
            self.assertTrue(SNot(SAnd(t1, t2)).typeEquivalent(SOr(SNot(t1), SNot(t2))) is not False)

    def test_typeEquivalent(self):
        def f():
            return True

        def g():
            return True

        t1 = SSatisfies(f, "f")
        t2 = SSatisfies(g, "g")

        def oddp(a):
            return a % 2 == 1 if type(a) is int else False

        sodd = SSatisfies(oddp, "odd")

        L = [
            # A < B = None    B < A = None
            (t1, t2, None, None, None),
            # A < B = None   B < A = False
            (sodd, SEql(2), None, False, False),
            # A < B = None   B < A = True
            (t1, SEmpty, None, True, None),

            # A < B = True   B < A = None
            (SEmpty, t1, True, None, None),
            # A < B = True   B < A = False
            (SMember(1, 2), SMember(1, 2, 3), True, False, False),
            # A < B = True   B < A = True
            (SMember(1, 2, 3), SMember(2, 1, 3), True, True, True),

            # A < B = False  B < A = None
            (SMember(2, 4), sodd, False, None, False),
            # A < B = False  B < A = False
            (SMember(1, 2, 3), SMember(2, 3, 4), False, False, False),
            # A < B = False  B < A = True
            (SMember(1, 2, 3), SMember(2, 3), False, True, False)
        ]

        for (a, b, lt, gt, eq) in L:
            self.assertTrue(a.subtypep(b) == lt, f"\na={a}\nb={b}\nexpecting a < b = {lt}, got {a.subtypep(b)}")
            self.assertTrue(b.subtypep(a) == gt, f"\na={a}\nb={b}\nexpecting a > b = {gt}, got {b.subtypep(a)}")
            self.assertTrue(a.typeEquivalent(b) == eq,
                            f"\na={a}\nb={b}\nexpecting a = b = {eq}, got {a.typeEquivalent(b)}")

    def test_search_replace(self):
        li = [SMember(1, 2, 3), SMember(2, 1, 3), SMember(3, 1, 2)]
        replace = [SMember(4, 5, 6), SMember(5, 4, 6), SMember(6, 4, 5)]

        # Searching something that doesn't exist won't change the list
        li = search_replace(li, SMember(8, 9, 2), replace[2])
        self.assertEqual(li[0], SMember(1, 2, 3))
        self.assertEqual(li[1], SMember(2, 1, 3))
        self.assertEqual(li[2], SMember(3, 1, 2))
        self.assertTrue(len(li) == 3)

        # Searching every element and replacing them with Replace elements
        li = search_replace(li, SMember(1, 2, 3), replace[0])
        li = search_replace(li, SMember(2, 1, 3), replace[1])
        li = search_replace(li, SMember(3, 1, 2), replace[2])
        self.assertEqual(li, replace)
        self.assertTrue(len(li) == 3)

        # Empty list
        self.assertEqual(search_replace([], li[0], SMember(4, 6, 0)), [])

    def test_search_replace_splice(self):
        li = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(search_replace_splice(li, 7, [7, 8, 9, 10]), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_find_simplifier(self):
        t = SMember(1, 2, 3)
        simplifiers = []
        self.assertEqual(find_simplifier(t, simplifiers), t)
        simplifiers.append(lambda: t)
        self.assertEqual(find_simplifier(t, simplifiers), t)
        simplifiers.append(lambda: SMember(2, 1, 3))
        self.assertEqual(find_simplifier(t, simplifiers), SMember(2, 1, 3))
        simplifiers.append(lambda: SMember(3, 2, 1))
        self.assertEqual(find_simplifier(t, simplifiers), SMember(2, 1, 3))

    def test_remove_element(self):
        # Empty list
        self.assertEqual(remove_element([], "h"), [])

        # Removing element that occurs 1 time
        li = ["s", "j", "v", "h", "t", "j", "f", "o", "j", "e", "h"]
        self.assertEqual(remove_element(li, "s"), ["j", "v", "h", "t", "j", "f", "o", "j", "e", "h"])

        # Removing element that occurs 2+ times
        li = ["s", "j", "v", "h", "t", "j", "f", "o", "j", "e", "h"]
        self.assertEqual(remove_element(li, "h"), ["s", "j", "v", "t", "j", "f", "o", "j", "e"])
        self.assertEqual(remove_element(li, "j"), ["s", "v", "h", "t", "f", "o", "e", "h"])

        # Removing element that isn't included
        self.assertEqual(remove_element(li, "r"), li)

    def test_cmp_objects(self):
        t = 1
        s = 1
        # objects are the same
        self.assertEqual(cmp_objects(t, s), 0)
        # objects are not the same type
        t = SMember(1, 2, 3)
        self.assertEqual(cmp_objects(t, s), -1)
        # objects are same type not equal
        # t < s
        s = SMember(2, 1, 3)
        self.assertEqual(cmp_objects(t, s), -1)
        # t > s
        t = SMember(3, 1, 2)
        self.assertEqual(cmp_objects(t, s), 1)

    def test_find_first(self):
        # Empty list testing the default argument also
        self.assertEqual(find_first(lambda _: True, []), None)
        self.assertEqual(find_first(lambda _ : True, [], "Test"), "Test")

        # No elements makes the predicate true
        li = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(find_first(lambda x: x + 1 == 9, li), None)
        # first element is the last
        self.assertEqual(find_first(lambda x: x + 1 == 8, li), 7)
        # first element is the first
        self.assertEqual(find_first(lambda x: x + 1 == 2, li), 1)
        # first element is one of them
        self.assertEqual(find_first(lambda x: x + 1 == 5, li), 4)

    def test_canonicalize_1464(self):
        odd = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
        even = SSatisfies(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        t0 = SOr(SAnd(SNot(odd), even), SAnd(even,odd))
        assert t0.conversion17() == SOr(even, even)
        assert t0.canonicalize() == even, f"canonicalize = {t0.canonicalize()}"

        t1 = SAnd(SOr(SNot(odd),even), SOr(even,odd))
        self.assertEqual( t1.conversion17(), SAnd(even, even))
        self.assertEqual( t1.canonicalize(), even)


if __name__ == '__main__':
    unittest.main()
