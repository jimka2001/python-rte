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

import unittest
from rte.r_sigma import Sigma, SigmaImpl
from rte.r_epsilon import Epsilon, EpsilonImpl
from rte.r_emptyset import EmptySet, EmptySetImpl
from rte.r_star import Star
from rte.r_and import And, createAnd
from rte.r_or import Or, createOr
from rte.r_singleton import Singleton
from rte.r_not import Not
from rte.r_cat import Cat, createCat, catxyp, catp
from rte.r_random import random_rte
from rte.r_constants import notSigma, sigmaSigmaStarSigma, notEpsilon, sigmaStar
from genus.s_eql import SEql
from genus.s_top import STop
from genus.s_empty import SEmpty
from genus.s_member import SMember
from genus.s_atomic import SAtomic
from genus.s_and import SAnd
from genus.s_or import SOr

# default value of num_random_tests is 1000, but you can temporarily edit this file
#   and set it to a smaller number for a quicker run of the tests.
num_random_tests = 1000


class RteCase(unittest.TestCase):
    def test_sigma(self):
        self.assertTrue(Sigma is Sigma)
        self.assertIs(Sigma, SigmaImpl())
        self.assertIs(SigmaImpl(), SigmaImpl())

    def test_epsilon(self):
        self.assertIs(Epsilon, Epsilon)
        self.assertIs(Epsilon, EpsilonImpl())
        self.assertIs(EpsilonImpl(), EpsilonImpl())

    def test_emptyset(self):
        self.assertTrue(EmptySet is EmptySet)
        self.assertIs(EmptySet, EmptySetImpl())
        self.assertIs(EmptySetImpl(), EmptySetImpl())

    def test_star(self):
        self.assertIs(Star(Sigma), Star(Sigma))
        self.assertIs(Star(Epsilon), Star(Epsilon))
        self.assertIs(Star(EmptySet), Star(EmptySet))

    def test_plus(self):
        from rte.syntax_sugar import Plus, Eql
        self.assertEqual(42, Plus(Eql(1)).simulate(42, [1]))
        self.assertEqual(42, Plus(Eql(1)).simulate(42, [1,1]))
        self.assertEqual(42, Plus(Eql(1)).simulate(42, [1,1,1]))
        self.assertIsNone(Plus(Eql(1)).simulate(42, []))

    def test_satisfies(self):
        from rte.syntax_sugar import Satisfies
        def oddp(n):
            if not isinstance(n, int):
                return False
            else:
                return n % 2 != 0

        self.assertEqual(42, Satisfies(oddp, "odd").simulate(42, [1]))
        self.assertIsNone(Satisfies(oddp, "odd").simulate(42, [2]))
        self.assertIsNone(Satisfies(oddp, "odd").simulate(42, ["hello"]))
        self.assertIsNone(Satisfies(oddp, "odd").simulate(42, [1,1]))
        self.assertIsNone(Satisfies(oddp, "odd").simulate(42, [1,1,1]))
        self.assertIsNone(Satisfies(oddp, "odd").simulate(42, []))

    def test_atomic(self):
        from rte.syntax_sugar import Atomic
        self.assertEqual(42, Atomic(int).simulate(42, [1]))
        self.assertIsNone(Atomic(int).simulate(42, [1, 1]))
        self.assertIsNone(Atomic(int).simulate(42, []))
        self.assertIsNone(Atomic(int).simulate(42, ["hello"]))

    def test_eql(self):
        from rte.syntax_sugar import Eql
        self.assertEqual(42, Eql(1).simulate(42, [1]))
        self.assertIsNone(Eql(1).simulate(42, [1, 1]))
        self.assertIsNone(Eql(1).simulate(42, []))
        self.assertIsNone(Eql(1).simulate(42, ["hello"]))

    def test_member(self):
        from rte.syntax_sugar import Member
        self.assertEqual(42, Member(1,2,3).simulate(42, [1]))
        self.assertEqual(42, Member(1, 2, 3).simulate(42, [2]))
        self.assertEqual(42, Member(1, 2, 3).simulate(42, [3]))
        self.assertIsNone(Member(1,2,3).simulate(42, [1, 3]))
        self.assertIsNone(Member(1,2,3).simulate(42, []))
        self.assertIsNone(Member(1,2,3).simulate(42, ["hello"]))

    def test_or(self):
        self.assertEqual(Or(Sigma, Sigma, Sigma).operands, [Sigma, Sigma, Sigma])
        self.assertIs(createOr([]), EmptySet)
        self.assertEqual(createOr([Singleton(SEql(1))]), Singleton(SEql(1)))
        self.assertEqual(createOr([Sigma, Sigma]), Or(Sigma, Sigma))

    def test_and(self):
        self.assertEqual(And(Sigma, Sigma, Sigma).operands, [Sigma, Sigma, Sigma])
        self.assertIs(createAnd([]), Star(Sigma))
        self.assertEqual(createAnd([Singleton(SEql(1))]), Singleton(SEql(1)))
        self.assertEqual(createAnd([Sigma, Sigma]), And(Sigma, Sigma))

    def test_cat(self):
        self.assertEqual(Cat(Sigma, Sigma, Sigma).operands, [Sigma, Sigma, Sigma])
        self.assertIs(createCat([]), Epsilon)
        self.assertEqual(createCat([Singleton(SEql(1))]), Singleton(SEql(1)))
        self.assertEqual(createCat([Sigma, Sigma]), Cat(Sigma, Sigma))

        self.assertEqual(Cat(Singleton(SEql(1)), Singleton(SEql(2)), Singleton(SEql(3))),
                         Cat(Singleton(SEql(1)), Singleton(SEql(2)), Singleton(SEql(3))))

    def test_singleton(self):
        self.assertEqual(Singleton(SEql(1)).operand, SEql(1))

    def test_random(self):
        self.assertTrue(self)
        for depth in range(5):
            for r in range(1000):
                random_rte(depth).__str__()

    def test_first_types(self):
        from genus.simple_type_d import SimpleTypeD
        for depth in range(5):
            for r in range(1000):
                rt = random_rte(depth)
                ft = rt.first_types()
                self.assertTrue(all(isinstance(td, SimpleTypeD) for td in ft))

    def test_nullable(self):
        for depth in range(5):
            for r in range(2000):
                rt = random_rte(depth)
                self.assertIs(rt.nullable(), rt.canonicalize().nullable(),
                              f"\nlhs = {rt.nullable()}\nrhs = {rt.canonicalize().nullable()}" +
                              f"\nrt={rt}" +
                              f"\nrt.canonicalize() = {rt.canonicalize()}")

    def test_star_conversion1(self):
        self.assertIs(Star(Epsilon).conversion1(), Epsilon)
        self.assertIs(Star(EmptySet).conversion1(), Epsilon)
        rt = Star(Singleton(SEql(1)))
        self.assertIs(Star(rt).conversion1(), rt)

    def test_star_conversion2(self):
        x = Singleton(SEql(1))
        sx = Star(x)

        # Star(Cat(x,Star(x))) -> Star(x)
        self.assertIs(Star(Cat(x, sx)).conversion2(), sx)

        # Star(Cat(Star(x),x)) -> Star(x)
        self.assertIs(Star(Cat(sx, x)).conversion2(), sx)

        # Star(Cat(Star(x),x,Star(x))) -> Star(x)
        self.assertIs(Star(Cat(sx, x, sx)).conversion2(), sx)

        self.assertEqual(Star(Cat(Star(x), x)).conversion2(), Star(x))
        self.assertEqual(Star(Cat(x, Star(x))).conversion2(), Star(x))
        self.assertEqual(Star(Cat(Star(x), x, Star(x))).conversion2(), Star(x))

    def test_star_conversion3(self):
        x = Singleton(SEql(1))
        y = Singleton(SEql(2))
        z = Singleton(SEql(3))
        # Star(Cat(X, Y, Z, Star(Cat(X, Y, Z))))
        #    -->    Star(Cat(X, Y, Z))
        self.assertEqual(Star(Cat(x, y, z, Star(Cat(x, y, z)))).conversion3(),
                         Star(Cat(x, y, z)))
        # Star(Cat(Star(Cat(X, Y, Z)), X, Y, Z))
        #    -->    Star(Cat(X, Y, Z))
        self.assertEqual(Star(Cat(Star(Cat(x, y, z)), x, y, z)).conversion3(),
                         Star(Cat(x, y, z)))
        # Star(Cat(Star(Cat(X, Y, Z)), X, Y, Z, Star(Cat(X, Y, Z)))
        #    -->    Star(Cat(X, Y, Z))
        self.assertEqual(Star(Cat(Star(Cat(x, y, z)), x, y, z, Star(Cat(x, y, z)))).conversion3(),
                         Star(Cat(x, y, z)))
        self.assertEqual(Star(Cat()).conversion3(),
                         Star(Cat()))
        self.assertEqual(Star(Cat(x)).conversion3(),
                         Star(Cat(x)))

    def test_not_conversion1(self):
        self.assertEqual(Not(Sigma).conversion1(), Or(Cat(Sigma, Sigma, Star(Sigma)), Epsilon))
        self.assertIs(Not(Sigma).conversion1(), notSigma)
        self.assertEqual(Not(Singleton(STop)).conversion1(), Or(sigmaSigmaStarSigma, Epsilon))
        self.assertIs(Not(Singleton(STop)).conversion1(), notSigma)
        self.assertIs(Not(Star(Sigma)).conversion1(), EmptySet)
        self.assertIs(Not(Epsilon).conversion1(), notEpsilon)
        self.assertEqual(Not(Epsilon).conversion1(), Cat(Sigma, Star(Sigma)))
        self.assertEqual(Not(EmptySet).conversion1(), Star(Sigma))
        self.assertIs(Not(EmptySet).conversion1(), sigmaStar)
        self.assertEqual(Not(Singleton(SEmpty)).conversion1(), Star(Sigma))
        self.assertIs(Not(Singleton(SEmpty)).conversion1(), sigmaStar)

    def test_not_conversion2(self):
        x = Singleton(SEql(1))
        self.assertIs(Not(Not(x)).conversion2(), x)

    def test_not_conversion3(self):
        x = Singleton(SEql(1))
        y = Singleton(SEql(2))
        z = Singleton(SEql(3))
        self.assertEqual(Not(Or(x, y, z)).conversion3(),
                         And(Not(x), Not(y), Not(z)))
        self.assertEqual(Not(And(x, y, z)).conversion3(),
                         Or(Not(x), Not(y), Not(z)))

    def test_cat_conversion6(self):
        # Cat(A, B, X *, X, C, D) --> Cat(A, B, X, X *, C, D)
        x = Singleton(SEql("x"))
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        d = Singleton(SEql("d"))
        self.assertEqual(Cat(a, b, Star(x), x, c, d).conversion6(),
                         Cat(a, b, x, Star(x), c, d))

    def test_cat_conversion1(self):
        x = Singleton(SEql("x"))
        self.assertIs(Cat().conversion1(), Epsilon)
        self.assertIs(Cat(x).conversion1(), x)
        self.assertEqual(Cat(x, x).conversion1(), Cat(x, x))

    def test_cat_conversion5(self):
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))

        # Cat(..., x*, x, x* ...) --> Cat(..., x*, x, ...)
        self.assertEqual(Cat(Star(x), x, Star(x)).conversion5(),
                         Cat(Star(x), x))
        self.assertEqual(Cat(y, Star(x), x, Star(x)).conversion5(),
                         Cat(y, Star(x), x))
        self.assertEqual(Cat(y, Star(x), x, Star(x), y).conversion5(),
                         Cat(y, Star(x), x, y))

        # and Cat(..., x*, x* ...) --> Cat(..., x*, ...)
        self.assertEqual(Cat(Star(x), Star(x)).conversion5(),
                         Star(x))
        self.assertEqual(Cat(y, Star(x), Star(x), y).conversion5(),
                         Cat(y, Star(x), y))
        self.assertEqual(Cat(Star(x), Star(x), y).conversion5(),
                         Cat(Star(x), y))
        self.assertEqual(Cat(y, Star(x), Star(x)).conversion5(),
                         Cat(y, Star(x)))

    def test_cat_conversion4(self):
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        self.assertEqual(Cat(x, Epsilon, y).conversion4(),
                         Cat(x, y))
        self.assertIs(Cat(x, Epsilon).conversion4(),
                      x)
        self.assertEqual(Cat(Cat(x, y), x, Cat(y, x)).conversion4(),
                         Cat(x, y, x, y, x))

    def test_cat_conversion3(self):
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        self.assertIs(Cat(x, EmptySet, y).conversion3(),
                      EmptySet)

    def test_combo_conversion1(self):
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        self.assertIs(And().conversionC1(), sigmaStar)
        self.assertIs(Or().conversionC1(), EmptySet)

        self.assertIs(And(x).conversionC1(), x)
        self.assertIs(Or(x).conversionC1(), x)

        self.assertEqual(And(x, y).conversionC1(), And(x, y))
        self.assertEqual(Or(x, y).conversionC1(), Or(x, y))

    def test_combo_conversionC3(self):
        # Or(... Sigma * ....) -> Sigma *
        # And(... EmptySet....) -> EmptySet
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        self.assertIs(Or(x, Star(Sigma), y).conversionC3(), sigmaStar)
        self.assertIs(And(x, EmptySet, y).conversionC3(), EmptySet)

    def test_combo_conversionC4(self):
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        self.assertEqual(Or(x, y, y, x, y, y).conversionC4(), Or(x, y))
        self.assertEqual(And(x, y, y, x, y, y).conversionC4(), And(x, y))

    def test_combo_conversionC5(self):
        # alphabetize
        w = Singleton(SEql("w"))
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        z = Singleton(SEql("z"))
        self.assertEqual(Or(z, y, x, w).conversionC5(), Or(w, x, y, z))
        self.assertEqual(And(z, y, x, w).conversionC5(), And(w, x, y, z))
        self.assertEqual(Or(Or(x, y), And(x, y)).conversionC5(), Or(And(x, y), Or(x, y)))

    def test_combo_conversionC6(self):
        w = Singleton(SEql("w"))
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        z = Singleton(SEql("z"))
        # remove Sigma* and flatten And(And(...)...)
        self.assertEqual(And(x, And(y, z)).conversionC6(), And(x, y, z))
        self.assertEqual(And(x, Star(Sigma), y).conversionC6(), And(x, y))
        self.assertEqual(And(And(w, x), Star(Sigma), And(y, z)).conversionC6(), And(w, x, y, z))

        # remove EmptySet and flatten Or(Or(...)...)
        self.assertEqual(Or(x, Or(y, z)).conversionC6(), Or(x, y, z))
        self.assertEqual(Or(x, EmptySet, y).conversionC6(), Or(x, y))
        self.assertEqual(Or(Or(w, x), EmptySet, Or(y, z)).conversionC6(), Or(w, x, y, z))

    def test_combo_conversionC7(self):
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        # (:or A B (:* B) C)
        # --> (:or A (:* B) C)
        self.assertEqual(Or(a, b, Star(b), c).conversionC7(), Or(a, Star(b), c))
        # (:and A B (:* B) C)
        # --> (:and A B C)
        self.assertEqual(And(a, b, Star(b), c).conversionC7(), And(a, b, c))

        self.assertEqual(And(Star(Epsilon), Not(Epsilon)).conversionC7(),
                         And(Star(Epsilon), Not(Epsilon)))

    def test_combo_conversionC11(self):
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        # And(..., x, Not(x)...) -> EmptySet
        self.assertIs(And(y, x, y, Not(x), y).conversionC11(), EmptySet)

        # Or(..., x, Not(x), ...) -> Sigma *
        self.assertIs(Or(y, x, y, Not(x), y).conversionC11(), sigmaStar)

    def test_combo_conversionC14(self):
        x = Singleton(SEql("x"))
        xy = Singleton(SMember("x", "y"))
        a = Singleton(SEql("a"))
        # Or(A, Not(B), X) -> Sigma * if B is subtype of A
        self.assertIs(Or(a, Not(x), xy).conversionC14(), sigmaStar)
        # And(A, Not(B), X) -> EmptySet if A is subtype of B
        self.assertIs(And(a, x, Not(xy)).conversionC14(), EmptySet)

    def test_combo_conversionC12(self):
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        # Or(   A, B, ... Cat(Sigma,Sigma,Sigma*) ... Not(Singleton(X)) ...)
        #   --> Or( A, B, ... Not(Singleton(X))
        self.assertEqual(Or(a, b, Cat(Star(a), a, b, Star(c)), Not(c)).conversionC12(),
                         Or(a, b, Not(c)))

        self.assertEqual(Or(a,
                            b,
                            Cat(Star(a), c, Star(c)),
                            Not(c)).conversionC12(),
                         Or(a, b, Cat(Star(a), c, Star(c)), Not(c)))
        # And(   A, B, ... Cat(Sigma,Sigma,Sigma*) ... Not(Singleton(X)) ...)
        #   --> Or( A, B, ... Cat(Sigma,Sigma,Sigma*) ...)
        self.assertEqual(And(a, b, Cat(Star(a), a, b, Star(c)), Not(c)).conversionC12(),
                         And(a, b, Cat(Star(a), a, b, Star(c))))

    def test_combo_conversionC15(self):
        # simplify to maximum of one SMember(...) and maximum of one Not(SMember(...))
        # Or(<{1,2,3,4}>,<{4,5,6,7}>,Not(<{10,11,12,13}>,Not(<{12,13,14,15}>)))
        #   --> Or(<{1,2,3,4,6,7}>,Not(<{12,13}>))
        self.assertEqual(Or(Singleton(SMember(1, 2, 3, 4)),
                            Singleton(SMember(4, 5, 6, 7)),
                            Not(Singleton(SMember(10, 11, 12, 13))),
                            Not(Singleton(SMember(12, 13, 14, 15)))).conversionC15(),
                         Or(Singleton(SMember(1, 2, 3, 4, 5, 6, 7)),
                            Not(Singleton(SMember(12, 13)))))

        # And(<{1,2,3,4}>,<{3,4,5,6,7}>,Not(<{10,11,12,13}>,Not(<{12,13,14,15}>)))
        #   --> And(<{3,4}>,Not(<{10,11,12,13,14,15}>))
        self.assertEqual(And(Singleton(SMember(1, 2, 3, 4)),
                             Singleton(SMember(3, 4, 5, 6, 7)),
                             Not(Singleton(SMember(10, 11, 12, 13))),
                             Not(Singleton(SMember(12, 13, 14, 15)))).conversionC15(),
                         And(Singleton(SMember(3, 4)),
                             Not(Singleton(SMember(10, 11, 12, 13, 14, 15)))))

    def test_combo_conversionC16(self):
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        ab = Singleton(SMember("a", "b"))
        ba = Singleton(SMember("b", "a"))
        bc = Singleton(SMember("b", "c"))
        # remove And superclasses
        self.assertEqual(And(a, b, c, ab, bc).conversionC16(), And(a, b, c))

        # remove Or subclasses
        self.assertEqual(Or(a, b, c, ab, bc).conversionC16(), Or(ab, bc))

        self.assertNotEqual(And(ab, ba).conversionC16(), sigmaStar)
        self.assertNotEqual(Or(ab, ba).conversionC16(), EmptySet)

    def test_combo_conversionC17(self):
        # And({1,2,3},Singleton(X),Not(Singleton(Y)))
        #  {...} selecting elements, x, for which SAnd(X,SNot(Y)).typep(x) is true
        self.assertEqual(And(Singleton(SMember("a", "b", 1, 2)), Singleton(SAtomic(str))).conversionC17(),
                         And(Singleton(SMember("a", "b")), Singleton(SAtomic(str))))

        # Or({1,2,3},Singleton(X),Not(Singleton(Y)))
        #  {...} deleting elements, x, for which SOr(X,SNot(Y)).typep(x) is true
        self.assertEqual(Or(Singleton(SMember("a", "b", 1, 2)), Singleton(SAtomic(str))).conversionC17(),
                         Or(Singleton(SMember(1, 2)), Singleton(SAtomic(str))))

    def test_combo_conversionC21(self):
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        ab = Singleton(SMember("a", "b"))
        self.assertIs(And(a, b, ab).conversionC21(), EmptySet)
        self.assertIs(Or(Not(a), Not(b), ab).conversionC21(), sigmaStar)

    def test_and_conversionA8(self):
        # if operands contains EmptyWord, then the intersection is either EmptyWord or EmptySet
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        self.assertIs(And(Star(a), Epsilon, Star(b)).conversionA8(), Epsilon)
        self.assertIs(And(Star(a), Epsilon, b).conversionA8(), EmptySet)
        self.assertEqual(And(a, b).conversionA8(), And(a, b))

    def test_and_conversionA9(self):
        # if x matches only singleton then And(x, y * ) -> And(x, y)
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        self.assertEqual(And(a, Star(b)).conversionA9(), And(a, b))

    def test_and_conversionA10(self):
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        d = Singleton(SEql("d"))
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        z = Singleton(SEql("z"))
        # And(A,B,Or(X,Y,Z),C,D)
        # --> Or(And(A,B,   X,   C, D)),
        #        And(A,B,   Y,   C, D)),
        #        And(A,B,   Z,   C, D)))
        self.assertEqual(And(a, b, Or(x, y, z), c, d).conversionA10(),
                         Or(And(a, b, x, c, d),
                            And(a, b, y, c, d),
                            And(a, b, z, c, d)))

    def test_and_conversionA13(self):
        # if there is an explicit Sigma and also a singleton which is inhabited, then
        #  we can simply remove the sigma.
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        self.assertEqual(And(a, b, Sigma).conversionA13(), And(a, b))

    def test_and_conversionA18(self):
        # if there is a singleton which is not inhabited
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        self.assertEqual(And(a, Singleton(SAnd(SEql(1), SEql(2))), b).conversionA18(), EmptySet)

    def test_combo_conversionD16b(self):
        # And(A, x, Not(y)) --> And(A, x) if x, y disjoint
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        a = Singleton(SMember("x", "y"))
        self.assertIs(x.operand.disjoint(y.operand), True)
        self.assertEqual(And(a, x, Not(y)).conversionD16b(), And(a, x))
        self.assertEqual(Or(a, x, Not(y)).conversionD16b(), Or(a, Not(y)))

    def test_and_conversionA17(self):
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        self.assertIs(And(x, Cat(Star(x), y, Star(x), y)).conversionA17(), EmptySet)
        self.assertEqual(And(Star(x), Cat(Star(x), y, Star(x), y)).conversionA17(),
                         And(Star(x), Cat(Star(x), y, Star(x), y)))

    def test_and_conversionA17a(self):
        #    And(Cat(a,b,c),Cat(x,y,z) ...)
        #    --> And(Cat(And(a,x),And(b,y),And(c,z),...)
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        d = Singleton(SEql("d"))
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        z = Singleton(SEql("z"))
        self.assertIs(And(Cat(a, b, c, d), Cat(x, y, z)).conversionA17a(), EmptySet)
        self.assertEqual(And(Cat(a, b, c, Star(d)), Cat(x, y, z)).conversionA17a(),
                         And(Cat(a, b, c, Star(d)), Cat(x, y, z)))
        self.assertEqual(And(Cat(a, b, c), x).conversionA17a(),
                         And(Cat(a, b, c), x))
        self.assertEqual(And(Cat(Sigma, Sigma, Star(Sigma)),
                             Cat(Cat(Sigma, Star(Sigma)))).conversionA17a(),
                         And(Cat(Sigma, Sigma, Star(Sigma)),
                             Cat(Cat(Sigma, Star(Sigma)))))

        self.assertTrue(And(Cat(a, b, c).search(catp)))

        self.assertIsNot(And(Cat(Cat(a, b, c)),
                             Cat(a, b, c)).conversionA17a(), EmptySet)

    def test_and_conversionA17a2(self):
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        d = Singleton(SEql("d"))
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        z = Singleton(SEql("z"))
        self.assertEqual(And(Cat(a, b, c, Star(d)), Cat(x, y, z)).conversionA17a2(),
                         And(Cat(a, b, c, Star(d)), Cat(x, y, z)))
        self.assertEqual(And(Cat(a, b, c), x).conversionA17a2(),
                         And(Cat(a, b, c), x))
        self.assertEqual(And(Cat(a, b, c), d, Cat(x, y, z)).conversionA17a2(),
                         And(d, Cat(And(a, x), And(b, y), And(c, z))))
        self.assertEqual(And(Cat(Cat(a, b, c)),
                             Cat(a, b, c)).conversionA17a2(),
                         And(Cat(Cat(a, b, c)),
                             Cat(a, b, c)))

    def test_and_conversionA17b(self):
        # after 17a we know that if there are multiple Cats(...) without a nullable,
        #   then all such Cats(...) without a nullable have same number of operands
        #   have been merged into one Cat(...)
        #   So assure that all other Cats have no more non-nullable operands.
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        d = Singleton(SEql("d"))
        self.assertIs(And(Cat(a, b, c), Cat(a, b, c, d, Star(c))).conversionA17b(), EmptySet)
        self.assertEqual(And(Cat(a, b, c), Cat(a, b, c, Star(c))).conversionA17b(),
                         And(Cat(a, b, c), Cat(a, b, c, Star(c))))
        self.assertEqual(And(Cat(a, b, c), Cat(a, b, Star(c))).conversionA17b(),
                         And(Cat(a, b, c), Cat(a, b, Star(c))))
        # And(Cat(Σ, Σ, Star(Σ)), Cat(Cat(Σ, Star(Σ))))
        self.assertIsNot(And(Cat(Sigma, Sigma, Star(Sigma)),
                             Cat(Cat(Sigma, Star(Sigma)))).conversionA17b(),
                         EmptySet)

    def test_and_conversionA17c(self):
        # if And(...) contains a Cat with no nullables, (or explicit Sigma or Singleton)
        #  then remove the nullables from ever other Cat with that many non-nullables,
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        d = Singleton(SEql("d"))
        self.assertEqual(And(Cat(a, b, c), Star(d), Cat(a, b, Star(c))).conversionA17c(),
                         And(Cat(a, b, c), Star(d), Cat(a, b, Star(c))))
        self.assertEqual(And(Cat(a, b, c), Star(d), Cat(a, b, c, Star(c))).conversionA17c(),
                         And(Cat(a, b, c), Star(d), Cat(a, b, c)))
        self.assertEqual(And(Cat(a, b, c), Star(d), Cat(Star(a), b, c, d, Star(c))).conversionA17c(),
                         And(Cat(a, b, c), Star(d), Cat(b, c, d)))
        problematic = And(Cat(Sigma,Sigma,Sigma),
                          Cat(Sigma,Star(Sigma),Sigma,Cat(Sigma,Sigma)))
        self.assertEqual(problematic,problematic.conversionA17c())

    def test_and_conversionA19(self):
        ab = Singleton(SMember("a", "b"))
        bc = Singleton(SMember("b", "c"))
        ac = Singleton(SMember("a", "c"))
        self.assertIs(And(ab, bc, ac).conversionA19(), EmptySet)
        self.assertIs(And(ab, Not(Singleton(SAtomic(str)))).conversionA19(), EmptySet)

    def test_starp(self):
        from rte.syntax_sugar import plusp, Plus
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        self.assertTrue(plusp(Cat(a, Star(a))))
        self.assertTrue(plusp(Cat(Star(a), a)))
        self.assertTrue(plusp(Plus(a)))
        self.assertFalse(plusp(Cat(a, Star(b))))
        self.assertFalse(Plus(a).nullable())

    def test_catxyp(self):
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        z = Singleton(SEql("z"))
        # Cat(x,y,z,Star(Cat(x,y,z)))
        self.assertTrue(catxyp(Cat(x, y, z, Star(Cat(x, y, z)))))
        self.assertTrue(catxyp(Cat(x, y, Star(Cat(x, y)))))
        self.assertTrue(catxyp(Cat(x, Star(Cat(x)))))
        self.assertFalse(catxyp(Cat(Star(Cat()))))
        self.assertFalse(catxyp(Cat(x, x, y, z, Star(Cat(x, y, z)))))
        self.assertFalse(catxyp(Cat(x, y, z, Star(Cat(x, x, y, z)))))

    def test_or_conversionO8(self):
        from rte.syntax_sugar import Plus
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        # (:or :epsilon (:cat X (:* X) ANYTHING)) -> itself
        self.assertEqual(Or(a, Epsilon, b, Cat(x, Star(x), y), c).conversionO8(),
                         Or(a, Epsilon, b, Cat(x, Star(x), y), c))
        self.assertEqual(Or(a, Epsilon, b, Cat(Star(x), x, y), c).conversionO8(),
                         Or(a, Epsilon, b, Cat(Star(x), x, y), c))
        # (:or A :epsilon B (:cat X (:* X)) C)
        #   --> (:or A :epsilon B (:* X) C )
        self.assertEqual(Or(a, Epsilon, b, Cat(x, Star(x)), c).conversionO8(),
                         Or(a, Epsilon, b, Star(x), c))
        self.assertEqual(Or(a, Epsilon, b, Cat(Star(x), x), c).conversionO8(),
                         Or(a, Epsilon, b, Star(x), c))
        # (:or :epsilon (:cat X (:* X)))
        #   --> (:or :epsilon (:* X))
        self.assertEqual(Or(Epsilon, Cat(x, Star(x))).conversionO8(),
                         Or(Epsilon, Star(x)))
        self.assertEqual(Or(Epsilon, Cat(Star(x), x)).conversionO8(),
                         Or(Epsilon, Star(x)))
        # (:or (:* Y) (:cat X (:* X)))
        #   --> (:or (:* Y) (:* X))
        self.assertEqual(Or(Star(y), Cat(x, Star(x))).conversionO8(),
                         Or(Star(y), Star(x)))
        self.assertEqual(Or(Star(y), Cat(Star(x), x)).conversionO8(),
                         Or(Star(y), Star(x)))

        # multiple instances
        self.assertEqual(Or(Star(y), Plus(a), Plus(b), Plus(c)).conversionO8(),
                         Or(Star(y), Star(a), Star(b), Star(c)))

        # no change
        self.assertEqual(Or(Star(y), Cat(Star(x), y)).conversionO8(),
                         Or(Star(y), Cat(Star(x), y)))
        self.assertEqual(Or(a, b, Cat(x, Star(x)), c).conversionO8(),
                         Or(a, b, Cat(x, Star(x)), c))

    def test_or_conversionO9(self):
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        x = Singleton(SEql("x"))
        y = Singleton(SEql("y"))
        z = Singleton(SEql("z"))
        # (:or A :epsilon B (:cat X Y Z (:* (:cat X Y Z))) C)
        #   --> (:or A :epsilon B (:* (:cat X Y Z)) C )
        self.assertEqual(Or(a, Epsilon, b, Cat(x, y, z, Star(Cat(x, y, z))), c).conversionO9(),
                         Or(a, Epsilon, b, Star(Cat(x, y, z)), c))

        # (:or :epsilon (:cat X Y Z (:* (:cat X Y Z))))
        #   --> (:or :epsilon (:* (:cat X Y Z)))
        self.assertEqual(Or(Epsilon, Cat(x, y, z, Star(Cat(x, y, z)))).conversionO9(),
                         Or(Epsilon, Star(Cat(x, y, z))))

        s = Star(Cat(x, y, z))
        c = Cat(x, y, z, s)
        self.assertEqual(Or(Epsilon, c, c, c).conversionO9(),
                         Or(Epsilon, s, s, s))

        self.assertEqual(Or(y, c).conversionO9(),
                         Or(y, c))

    def test_or_conversionO10(self):
        # (: or A :epsilon B (: * X) C)
        # --> (: or A B (: * X) C)
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        c = Singleton(SEql("c"))
        x = Singleton(SEql("x"))
        self.assertEqual(Or(a, Epsilon, b, Star(x), c).conversionO10(),
                         Or(a, b, Star(x), c))
        self.assertEqual(Or(a, Epsilon, b, Epsilon, c).conversionO10(),
                         Or(a, Epsilon, b, Epsilon, c))

    def test_or_conversionO11b(self):
        # if Sigma is in the operands, then filter out all singletons
        # Or(Singleton(A),Sigma,...) -> Or(Sigma,...)
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        self.assertEqual(Or(a, b, Sigma, Star(b)).conversionO11b(),
                         Or(Sigma, Star(b)))
        self.assertIs(Or(a, b, Sigma).conversionO11b(),
                      Sigma)
        self.assertEqual(Or(a, b, Star(b)).conversionO11b(),
                         Or(a, b, Star(b)))

    def test_or_conversionO15(self):
        # Or(Not(A),B*,C) = Or(Not(A),C) if A and B  disjoint,
        #   i.e. remove all B* where B is disjoint from A
        a = Singleton(SEql("a"))
        b = Singleton(SEql("b"))
        ab = Singleton(SMember("a", "b"))
        c = Singleton(SEql("c"))
        self.assertEqual(Or(Not(a), Star(b), c).conversionO15(),
                         Or(Not(a), c))
        self.assertEqual(Or(Not(a), Star(b), c, Star(c)).conversionO15(),
                         Or(Not(a), c))
        self.assertEqual(Or(Not(a), Not(b), Star(b), c, Star(c), Star(ab)).conversionO15(),
                         Or(Not(a), Not(b), c, Star(ab)))

    def test_discovered_case_619(self):
        # rte.r_rte.CannotComputeDerivative: Singleton.derivative_down cannot compute derivative of
        # Singleton(SAtomic(TestA))
        # wrt=SAnd(SNot(odd?), SOr(SAtomic(Test1), [= -1]))
        from genus.depthgenerator import TestA, Test1
        from genus.s_not import SNot
        from genus.s_satisfies import SSatisfies
        from genus.s_or import SOr
        r = Singleton(SAtomic(TestA))
        wrt = SAnd(SNot(SSatisfies(lambda a: isinstance(a, int) and a % 2 == 1, "odd")),
                   SOr(SAtomic(Test1)), SEql(-1))
        self.assertIsNotNone(r.derivative1(wrt))

    def test_derivatives(self):
        for depth in range(5):
            for r in range(1000):
                rt = random_rte(depth)
                self.assertTrue(rt.derivatives())

    def test_derivative_643(self):
        rt1 = Cat(Star(Sigma), Star(Singleton(SEql(1))))
        rt2 = Cat(Not(EmptySet), Star(Singleton(SEql(1))))
        v1, v2 = rt1.derivatives()
        self.assertTrue(v1)
        self.assertTrue(v2)
        u1, u2 = rt2.derivatives()
        self.assertTrue(u1)
        self.assertTrue(u2)

    def test_simulate(self):
        self.assertIs(True, Star(Singleton(SAtomic(str))).simulate(True, ["a", "b", "c"]))
        self.assertIs(None, Star(Singleton(SAtomic(str))).simulate(True, ["a", "b", 3]))
        self.assertIs(True, Star(Singleton(SAtomic(str))).simulate(True, []))
        self.assertEqual(42, Star(Singleton(SAtomic(str))).simulate(42, ["a", "b", "c"]))
        self.assertEqual(42, Or(Star(Singleton(SAtomic(str))),
                                Star(Singleton(SAtomic(int)))).simulate(42, ["a", "b", "c"]))
        self.assertEqual(42, Or(Star(Singleton(SAtomic(str))),
                                Star(Singleton(SAtomic(int)))).simulate(42, [1, 2, 3]))
        self.assertIs(None, Or(Star(Singleton(SAtomic(str))),
                               Star(Singleton(SAtomic(int)))).simulate(42, [1, "b", 3]))
        self.assertEqual(42, Star(Or(Singleton(SAtomic(str)),
                                     Singleton(SAtomic(int)))).simulate(42, [1, "b", 3]))
        self.assertEqual(42, Star(Or(Singleton(SOr(SAtomic(str), SAtomic(int))))).simulate(42, [1, "b", 3]))
        self.assertEqual(42, Star(Or(Singleton(SOr(SAtomic(str),
                                                   # warning True is an int in Python isinstance(True,int) --> True
                                                   SAtomic(int))))).simulate(42, [1, "b", True]))
        self.assertIs(None, Star(Or(Singleton(SOr(SAtomic(str),
                                                  SAtomic(int))))).simulate(42, [1, "b", 3.4]))

    def test_serialize(self):
        for depth in range(4):
            for r in range(num_random_tests):
                rt = random_rte(depth)
                self.assertTrue(rt.to_dfa(depth * 10).serialize())

    def test_serialize2(self):
        for depth in range(4):
            for r in range(num_random_tests):
                rt = random_rte(depth)
                i = rt.inhabited()
                v = rt.vacuous()
                if i is None:
                    self.assertIsNone(v)
                else:
                    self.assertEqual(i, not v)

    def test_discovered_682(self):
        so = Singleton(SEql(1))
        i = 0
        for rt in [Cat(And(Not(so), Sigma),  # 0
                       Star(so)),
                   Cat(Or(And(Not(so), Sigma),  # 1
                          Cat(so, Star(so), And(Not(so), Sigma))),
                       Star(so)),
                   Cat(Or(And(Not(so), Sigma),  # 2
                          Cat(so, Star(so), And(Not(so), Sigma))),
                       Star(Or(And(Not(so), Sigma),
                               Cat(so, Star(so), And(Not(so), Sigma)))),
                       Star(so)),
                   Or(Cat(Or(And(Not(so), Sigma),  # 3
                             Cat(so, Star(so), And(Not(so), Sigma))),
                          Star(Or(And(Not(so), Sigma),
                                  Cat(so, Star(so), And(Not(so), Sigma)))),
                          Star(so))),
                   Or(Cat(so, Star(so)),  # 4
                      Cat(Or(And(Not(so), Sigma),
                             Cat(so, Star(so), And(Not(so), Sigma))),
                          Star(Or(And(Not(so), Sigma),
                                  Cat(so, Star(so), And(Not(so), Sigma)))),
                          Star(so))),

                   Or(Cat(so, Star(so)),  # 5
                      Cat(Or(And(Not(so), Sigma),
                             Cat(so, Star(so), And(Not(so), Sigma))),
                          Star(Or(And(Not(so), Sigma),
                                  Cat(so, Star(so), And(Not(so), Sigma)))),
                          Star(so)),
                      Epsilon)
                   ]:
            can = rt.canonicalize()
            rt.to_dot(exit_value=True, view=False, title=f"rt-{i}")
            self.assertIs(rt.simulate(True, [2, 1]), True)
            can.to_dot(exit_value=True, view=False, title=f"can-{i}")
            self.assertIs(can.simulate(True, [2, 1]), True,
                          f"rt-{i} accepts [2,1], but rejects when canonicalized:\n rt={rt}\n can={can}")
            i = i + 1

    def test_discovered_733(self):
        from genus.utils import fixed_point
        so = Singleton(SEql(1))
        nso = And(Not(so), Sigma)
        rt = Or(Cat(so, Star(so)),
                Cat(Or(nso,
                       Cat(so, Star(so), nso)),
                    Star(Or(nso,
                            Cat(so, Star(so), nso))),
                    Star(so)),
                Epsilon)

        self.assertIs(rt.simulate(True, [2, 1]), True)

        def invariant(r):
            return r.simulate(True, [2, 1])

        fixed_point(rt, lambda r: r.canonicalize_once(), lambda a, b: a == b, invariant)

    def test_discovered_752(self):
        from genus.utils import fixed_point
        so = Singleton(SEql(1))
        rt = Or(Cat(Or(And(Not(EmptySet), Epsilon),
                       Cat(EmptySet, Star(so), And(Not(so), Sigma))),
                    Star(Or(And(Not(so), Sigma), Cat(so, Star(so), And(Not(so), Sigma)))),
                    Star(so)),
                EmptySet)

        self.assertIs(rt.simulate(True, [2, 1]), True)

        def invariant(r):
            return r.simulate(True, [2, 1])

        fixed_point(rt, lambda r: r.canonicalize_once(), lambda a, b: a == b, invariant)

    def test_discovered_785(self):
        # rt=And(Or(Or(∅, Σ), Not(Σ)), Cat(Not(ε), Not(ε)))
        # can=Cat(Σ, Σ)
        from rte.r_epsilon import Epsilon
        from genus.utils import fixed_point
        problematic = Or(And(Cat(Sigma, Sigma, Star(Sigma)),
                             Cat(Cat(Sigma, Star(Sigma)))))

        def good_enough(a, b):
            return type(a) == type(b) and a == b

        def try_example(rt, seq) -> bool:
            expecting = problematic.simulate(True, seq)
            got = rt.simulate(True, seq)
            if got is not expecting:
                print(f" seq= {seq}")
                print(f"  rt={rt}")
                print(f" expecting = {expecting}")
                print(f"       got = {got}")
            return got is expecting

        def invariant(rt: 'Rte') -> bool:
            return all(try_example(rt, seq)
                       for seq in [[1, 1],
                                   [1],
                                   [],
                                   [1, 1, 1]])

        self.assertTrue(fixed_point(problematic,
                                    lambda r: r.canonicalize_once(),
                                    good_enough,
                                    invariant))


if __name__ == '__main__':
    unittest.main()
