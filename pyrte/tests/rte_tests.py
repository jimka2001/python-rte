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
from genus.s_eql import SEql
from genus.s_top import STop
from genus.s_empty import SEmpty
from rte.r_cat import Cat, createCat
from rte.r_random import random_rte
from rte.r_constants import notSigma, sigmaSigmaStarSigma, notEpsilon, sigmaStar


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
        for depth in range(5):
            for r in range(1000):
                random_rte(depth).__str__()

    def test_nullable(self):
        for depth in range(5):
            for r in range(1000):
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


if __name__ == '__main__':
    unittest.main()
