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
from rte.r_or import Or
from rte.r_and import And
from rte.r_cat import Cat


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

    def test_or(self):
        self.assertEqual(Or(Sigma,Sigma,Sigma).operands, [Sigma,Sigma,Sigma])

    def test_and(self):
        self.assertEqual(And(Sigma,Sigma,Sigma).operands, [Sigma,Sigma,Sigma])

    def test_cat(self):
        self.assertEqual(Cat(Sigma,Sigma,Sigma).operands, [Sigma,Sigma,Sigma])


if __name__ == '__main__':
    unittest.main()

