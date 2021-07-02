# Copyright (©) 2021 EPITA Research and Development Laboratory
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

from genus.depthgenerator import random_type_designator, test_values, DepthGenerator
from genus.genus_types import NormalForm
from genus.genus_types import combop, memberimplp, notp, notp, orp, andp, atomicp, topp
from genus.genus_types import createSAnd, createSOr, createSMember, cmp_type_designators
from genus.mdtd import mdtd
from genus.s_and import SAnd
from genus.s_atomic import SAtomic
from genus.s_combination import SCombination
from genus.s_custom import SCustom
from genus.s_empty import SEmptyImpl, SEmpty
from genus.s_eql import SEql
from genus.s_member import SMemberImpl, SMember
from genus.s_not import SNot
from genus.s_or import SOr
from genus.s_top import STopImpl, STop
from genus.simple_type_d import SimpleTypeD, TerminalType
from genus.utils import compare_sequence, get_all_subclasses
from genus.utils import find_simplifier, find_first
from genus.utils import flat_map, generate_lazy_val, fixed_point
from genus.utils import remove_element, search_replace, uniquify

# default value of num_random_tests is 1000, but you can temporarily edit this file
#   and set it to a smaller number for a quicker run of the tests.
num_random_tests = 1000


def t_verboseonlyprint(s):
    if 'genusverbose' in os.environ and os.environ['genusverbose'] == str(True):
        print(s)


class GenusCase(unittest.TestCase):

    def test_atomic(self):
        def x():
            from pyrte.genus.depthgenerator import TestA
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

    def test_STop(self):

        # STop has to be unique
        self.assertTrue(id(STop) == id(STopImpl()))
        self.assertTrue(STop is STopImpl())

        # str(a) has to be "STop"
        self.assertTrue((str(STop) == "STop"))

        from pyrte.genus.depthgenerator import test_values
        for x in test_values:
            self.assertTrue((STop.typep(x)))

        # obviously, a is inhabited as it contains everything by definition
        self.assertTrue((STop.inhabited() is True))

        # a is never disjoint with anything but the empty subtype
        self.assertTrue(STop.disjoint(SAtomic(object)) is False)
        self.assertTrue(STop.disjoint(SEmpty) is True)

        # on the contrary, a is never a subtype of any type
        # since types are sets and top is the set that contains all sets
        self.assertTrue((STop.subtypep(SAtomic(object)) is True))
        self.assertTrue(STop.subtypep(STop) is True)

    def test_scustom(self):
        def l_odd(n):
            return isinstance(n, int) and n % 2 == 1

        guinea_pig = SCustom(l_odd, "[odd numbers]")
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

    def test_scustom2(self):
        def l_odd(n):
            return isinstance(n, int) and n % 2 == 1

        self.assertTrue(SCustom(l_odd, "odd").disjoint(SMember(1, 2, 3)) is False)

    def test_sand1(self):
        quadruple = SCustom((lambda x: x % 4 == 0), "quadruple")

        triple = SCustom(lambda x: isinstance(x, int) and (x % 3 == 0), "triple")

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
        quadruple = SCustom((lambda x: x % 4 == 0), "quadruple")

        triple = SCustom(lambda x: isinstance(x, int) and (x % 3 == 0), "triple")

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
        quadruple = SCustom(lambda x: isinstance(x, int) and x % 4 == 0, "quadruple")
        triple = SCustom(lambda x: isinstance(x, int) and x % 3 == 0, "triple")

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
        pair = SCustom(lambda x: isinstance(x, int) and x & 1 == 0, "pair")

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

        # a.subtypep(t) indicates whether t is a subtype of a, which is always the case by definition
        self.assertTrue(STop.subtypep(SAtomic(object)) is True)
        self.assertTrue(STop.subtypep(STop) is True)

        # obviously, a is inhabited as it contains everything by definition
        self.assertTrue(STop.inhabited() is True)

        # a is never disjoint with anything but the empty subtype
        self.assertTrue(STop.disjoint(SAtomic(object)) is False)
        self.assertTrue(STop.disjoint(SEmpty) is True)

        # on the contrary, a is never a subtype of any type
        # since types are sets and top is the set that contains all sets
        self.assertTrue(STop.subtypep(SAtomic(object)) is not False)
        self.assertTrue(STop.subtypep(STop) is True)

    def test_SEmpty(self):

        # SEmpty has to be unique
        self.assertTrue(id(SEmpty) == id(SEmptyImpl()))
        self.assertTrue(SEmpty is SEmptyImpl())

        # str(a) has to be "Empty"
        self.assertTrue(str(SEmpty) == "SEmpty")

        # a.typep(t) indicates whether t is a subtype of a, which is never the case
        self.assertTrue(SEmpty.typep(3) is False)
        self.assertTrue(SEmpty.subtypep(SEmpty) is True)
        for x in test_values:
            self.assertTrue(SEmpty.typep(x) is False)

        # obviously, a is not inhabited as it is by definition empty
        self.assertTrue(SEmpty.inhabited() is False)

        # a is disjoint with anything as it is empty
        self.assertTrue(SEmpty.disjoint(SAtomic(object)) is True)

        # on the contrary, a is always a subtype of any type
        # since types are sets and the empty set is a subset of all sets
        self.assertTrue(SEmpty.subtypep(SAtomic(object)) is True)
        self.assertTrue(SEmpty.subtypep(SEmpty) is True)

    def test_disjoint_375(self):
        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td1 = random_type_designator(depth)
                td2 = random_type_designator(depth)
                if SAnd(td1, td2).canonicalize(NormalForm.DNF) is SEmpty:
                    self.assertTrue(td1.disjoint(td2) is not False,
                                    "found types with empty intersection but not disjoint" +
                                    f"\ntd1={td1}" +
                                    f"\ntd2={td2}")

    def test_discovered_case_385(self):
        even = SCustom(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        td1 = STop
        td2 = SAnd(SEmpty, even)
        self.assertIs(SAnd(td1, td2).canonicalize(NormalForm.DNF), SEmpty)
        self.assertIsNot(td1.disjoint(td2), False, f"td1.disjoint(td2) = {td1.disjoint(td2)}")

    def test_discovered_case_375(self):
        from pyrte.genus.depthgenerator import TestB, Test1
        even = SCustom(lambda a: isinstance(a, int) and a % 2 == 0, "even")
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
        from pyrte.genus.depthgenerator import TestB, Test1
        even = SCustom(lambda a: isinstance(a, int) and a % 2 == 0, "even")
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
        from pyrte.genus.depthgenerator import TestB, Test1
        even = SCustom(lambda a: isinstance(a, int) and a % 2 == 0, "even")
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
        from pyrte.genus.depthgenerator import TestB, Test1
        even = SCustom(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        td1 = SAnd(SNot(SAtomic(TestB)),
                   SNot(SAtomic(int)),
                   SOr(SAtomic(Test1), even)).canonicalize(NormalForm.CNF)
        td2 = SAnd(SNot(SAnd(SNot(SAtomic(TestB)),
                             SOr(SAtomic(Test1), even))),
                   SNot(SAtomic(int))).canonicalize(NormalForm.CNF)
        # self.assertIs(SAnd(td1, td2).canonicalize(NormalForm.DNF), SEmpty)
        print("-----------------------")
        self.assertIsNot(td1.disjoint(td2), False,
                         f"\n td1={td1}\n td2={td2}\n td1.disjoint(td2) = {td1.disjoint(td2)}")

    def test_discovered_case_297(self):
        from pyrte.genus.depthgenerator import TestA, TestB

        even = SCustom(lambda a: isinstance(a, int) and a % 2 == 0, "even")
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
        from pyrte.genus.depthgenerator import Test2, TestA

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
        from pyrte.genus.depthgenerator import random_type_designator
        for depth in range(0, 3):
            for _ in range(num_random_tests):
                td1 = random_type_designator(depth)
                td2 = random_type_designator(depth)
                self.assertTrue(td1.subtypep(td1) is True)
                self.assertTrue(SAnd(td1, td2).subtypep(td1) is not False)
                self.assertTrue(td1.subtypep(SOr(td1, td2)) is not False)
                self.assertTrue(SAnd(td1, td2).subtypep(SAnd(td2, td1)) is not False)
                self.assertTrue(SOr(td1, td2).subtypep(SOr(td2, td1)) is not False,
                                f"td1={td1}\ntd2={td2}")
                self.assertTrue(SAnd(td1, td2).subtypep(SOr(td1, td2)) is not False)
                self.assertTrue(SAnd(SNot(td1), SNot(td2)).subtypep(SNot(SOr(td1, td2))) is not False)
                self.assertTrue(SOr(SNot(td1), SNot(td2)).subtypep(SNot(SAnd(td1, td2))) is not False)
                self.assertTrue(SNot(SOr(td1, td2)).subtypep(SAnd(SNot(td1), SNot(td2))) is not False,
                                f"td1={td1}\ntd2={td2}")
                self.assertTrue(SNot(SAnd(td1, td2)).subtypep(SOr(SNot(td1), SNot(td2))) is not False)

    def test_subtypep2(self):
        from pyrte.genus.depthgenerator import random_type_designator
        for depth in range(0, 4):
            for _ in range(num_random_tests):
                td = random_type_designator(depth)
                tdc1 = td.canonicalize()
                tdc2 = td.canonicalize(NormalForm.DNF)
                tdc3 = td.canonicalize(NormalForm.CNF)

                self.assertTrue(td.subtypep(tdc1) is not False)
                self.assertTrue(td.subtypep(tdc2) is not False)
                self.assertTrue(td.subtypep(tdc2) is not False)
                self.assertTrue(tdc1.subtypep(td) is not False,
                                f"expecting tdc1={tdc1} subtype of {td} got {tdc1.subtypep(td)}")
                self.assertTrue(tdc2.subtypep(td) is not False,
                                f"expecting tdc2={tdc2} subtype of {td} got {tdc2.subtypep(td)}")
                self.assertTrue(tdc3.subtypep(td) is not False,
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

        self.assertTrue(SNot(SAtomic(int)).subtypep(SNot(SCustom(f, "f"))) is None)
        self.assertTrue(SAtomic(int).disjoint(SCustom(f, "f")) is None)
        self.assertTrue(SAtomic(int).disjoint(SNot(SCustom(f, "f"))) is None)
        self.assertTrue(SNot(SAtomic(int)).disjoint(SCustom(f, "f")) is None)
        self.assertTrue(SNot(SAtomic(int)).disjoint(SNot(SCustom(f, "f"))) is None)

        self.assertTrue(SAtomic(int).subtypep(SCustom(f, "f")) is None)
        self.assertTrue(SAtomic(int).subtypep(SNot(SCustom(f, "f"))) is None)
        self.assertTrue(SNot(SAtomic(int)).subtypep(SCustom(f, "f")) is None)

    def test_or(self):
        self.assertTrue(len(SOr(SEql(1), SEql(2)).tds) == 2)
        self.assertTrue(SOr().tds == [])

    def test_member(self):
        self.assertTrue(SMember(1, 2, 3).arglist == [1, 2, 3])
        self.assertTrue(SMember().arglist == [])
        self.assertTrue(SMember(1, 2, 3).subtypep(SMember(1, 2, 3, 4, 5)) is True)
        self.assertTrue(SMember(1, 2, 3).subtypep(SMember(1, 2)) is False)
        self.assertTrue(SMember(1, 2, 3).subtypep(SOr(SAtomic(str), SMember(1, 2, 3, 4, 5))) is True)
        self.assertTrue(SMember(1, 2, 3).subtypep(SAtomic(int)) is True)

        self.assertTrue(SMember(1, 1, 2, 3, 2).canonicalize() == SMember(1, 3, 2))
        self.assertTrue(SMember(3, 2, 1).canonicalize() == SMember(1, 2, 3))

    def test_eql(self):
        self.assertTrue(SEql(1).a == 1)
        self.assertTrue(SEql(1).arglist == [1], f"expecting arglist=[1], got {SEql(1).arglist}")

    def test_discovered_cases2(self):
        td = SAnd(SEql(3.14), SMember("a", "b", "c"))
        tdc = td.canonicalize()
        self.assertTrue(tdc == SEmpty, f"expecting td={td} to canonicalize to SEmpty, got {tdc}")

        td = SOr(SEql("a"), SAtomic(int))
        tdc = td.canonicalize()
        self.assertTrue(tdc != SAtomic(int))

    def test_membership(self):
        from pyrte.genus.depthgenerator import random_type_designator, test_values
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
        from pyrte.genus.depthgenerator import DepthGenerator
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

        self.assertTrue(cmp_type_designators(SEql(1), SEql(2)) < 0)
        self.assertTrue(cmp_type_designators(SEql(1), SEql(1)) == 0)
        self.assertTrue(cmp_type_designators(SEql(2), SEql(1)) > 0)

        self.assertTrue(cmp_type_designators(SMember(1), SMember(1)) == 0)
        self.assertTrue(cmp_type_designators(SMember(1), SMember(2)) < 0)
        self.assertTrue(cmp_type_designators(SMember(2), SMember(1)) > 0)
        self.assertTrue(cmp_type_designators(SMember(1), SMember(1, 2)) < 0)  # short list < long list
        self.assertTrue(cmp_type_designators(SMember(1, 2), SMember(1)) > 0)
        self.assertTrue(cmp_type_designators(SMember(1, 2), SMember(1, 2)) == 0)
        self.assertTrue(cmp_type_designators(SMember(1, 2), SMember(1, 3)) < 0)
        self.assertTrue(cmp_type_designators(SMember(1, 2), SMember(1, 1)) > 0)

        self.assertTrue(cmp_type_designators(SEql(1), SMember(1, 1)) < 0)  # compare alphabetically
        self.assertTrue(cmp_type_designators(SMember(1, 2), SEql(1)) > 0)

        self.assertTrue(cmp_type_designators(SAnd(SEql(1), SEql(2)), SAnd(SEql(1), SEql(2))) == 0)
        self.assertTrue(cmp_type_designators(SAnd(SEql(1), SEql(2)), SAnd(SEql(2), SEql(1))) < 0)
        self.assertTrue(cmp_type_designators(SAnd(SEql(2), SEql(2)), SAnd(SEql(2), SEql(1))) > 0)

        self.assertTrue(cmp_type_designators(SOr(SEql(2), SEql(1)), SOr(SEql(2), SEql(2))) < 0)
        self.assertTrue(cmp_type_designators(SOr(SEql(2), SEql(3)), SOr(SEql(2), SEql(2))) > 0)
        self.assertTrue(cmp_type_designators(SAnd(SEql(2), SEql(2)), SAnd(SEql(2), SEql(2))) == 0)

        self.assertTrue(cmp_type_designators(SOr(SEql(2), SEql(1)), SAnd(SEql(2), SEql(2))) > 0)  # alphabetical
        self.assertTrue(cmp_type_designators(SAnd(SEql(2), SEql(1)), SOr(SEql(2), SEql(2))) < 0)

        self.assertTrue(cmp_type_designators(SNot(SEql(1)), SNot(SEql(2))) < 0)
        self.assertTrue(cmp_type_designators(SNot(SEql(1)), SNot(SEql(1))) == 0)
        self.assertTrue(cmp_type_designators(SNot(SEql(2)), SNot(SEql(1))) > 0)

        self.assertTrue(cmp_type_designators(STop, STop) == 0)
        self.assertTrue(cmp_type_designators(SEmpty, SEmpty) == 0)
        self.assertTrue(cmp_type_designators(SEmpty, STop) < 0)
        self.assertTrue(cmp_type_designators(STop, SEmpty) > 0)

        self.assertTrue(cmp_type_designators(SAtomic(int), SAtomic(int)) == 0)
        self.assertTrue(cmp_type_designators(SAtomic(int), SAtomic(str)) < 0)
        self.assertTrue(cmp_type_designators(SAtomic(str), SAtomic(int)) > 0)

        even = SCustom(lambda a: isinstance(a, int) and a % 2 == 0, "even")
        odd = SCustom(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
        self.assertTrue(cmp_type_designators(even, even) == 0)
        self.assertTrue(cmp_type_designators(even, odd) < 0, f"expecting {even} < {odd}")  # alphabetical by printable
        self.assertTrue(cmp_type_designators(odd, even) > 0)

    def test_mdtd(self):
        for depth in range(0, 4):
            for length in range(1, 5):
                for _ in range(num_random_tests):
                    tds = [random_type_designator(depth) for _ in range(length)]
                    computed = mdtd(tds)
                    for i in range(len(computed)):
                        for j in range(i + 1, len(computed)):
                            self.assertTrue(computed[i].disjoint(computed[j]) is not False,
                                            f"\n tds={tds}" +
                                            f"\n mdtd={computed}" +
                                            f"\n {computed[i]}.disjoint({computed[j]}) = {computed[i].disjoint(computed[j])}" +
                                            f"\n intersection = {SAnd(computed[i], computed[j]).canonicalize(NormalForm.DNF)}")

                    for v in test_values:
                        containing = [td for td in computed if td.typep(v)]
                        self.assertEqual(len(containing), 1,
                                         f"expecting exactly one partition to contain v={v}" +
                                         f"\n tds={tds}\n mdtd={computed}\n containing={containing}")


if __name__ == '__main__':
    unittest.main()
