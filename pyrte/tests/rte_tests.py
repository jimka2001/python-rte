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
from genus.s_eql import SEql
from rte.r_cat import Cat, createCat
from rte.r_random import random_rte


class RteCase(unittest.TestCase):
    def test_sigma(self):
        self.assertTrue( Sigma is Sigma)
        self.assertIs(Sigma, SigmaImpl())
        self.assertIs(SigmaImpl(),SigmaImpl())

    def test_epsilon(self):
        self.assertIs(Epsilon, Epsilon)
        self.assertIs(Epsilon, EpsilonImpl())
        self.assertIs(EpsilonImpl(),EpsilonImpl())

    def test_emptyset(self):
        self.assertTrue(EmptySet is EmptySet)
        self.assertIs(EmptySet, EmptySetImpl())
        self.assertIs(EmptySetImpl(), EmptySetImpl())

    def test_star(self):
        self.assertIs(Star(Sigma), Star(Sigma))
        self.assertIs(Star(Epsilon), Star(Epsilon))
        self.assertIs(Star(EmptySet), Star(EmptySet))

    def test_or(self):
        self.assertEqual(Or(Sigma,Sigma,Sigma).operands, [Sigma,Sigma,Sigma])
        self.assertIs(createOr([]),EmptySet)
        self.assertEqual(createOr([Singleton(SEql(1))]), Singleton(SEql(1)))
        self.assertEqual(createOr([Sigma,Sigma]), Or(Sigma,Sigma))

    def test_and(self):
        self.assertEqual(And(Sigma,Sigma,Sigma).operands, [Sigma,Sigma,Sigma])
        self.assertIs(createAnd([]),Star(Sigma))
        self.assertEqual(createAnd([Singleton(SEql(1))]), Singleton(SEql(1)))
        self.assertEqual(createAnd([Sigma,Sigma]), And(Sigma,Sigma))

    def test_cat(self):
        self.assertEqual(Cat(Sigma,Sigma,Sigma).operands, [Sigma,Sigma,Sigma])
        self.assertIs(createCat([]),Epsilon)
        self.assertEqual(createCat([Singleton(SEql(1))]), Singleton(SEql(1)))
        self.assertEqual(createCat([Sigma,Sigma]), Cat(Sigma,Sigma))

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
                self.assertIs(rt.nullable(), rt.canonicalize().nullable())


if __name__ == '__main__':
    unittest.main()

