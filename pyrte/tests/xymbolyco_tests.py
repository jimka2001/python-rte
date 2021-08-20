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
from rte.r_star import Star, plusp, Plus
from rte.r_and import And, createAnd
from rte.r_or import Or, createOr
from rte.r_singleton import Singleton
from rte.r_not import Not
from rte.r_cat import Cat, createCat, catxyp
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


class XymbolycoCase(unittest.TestCase):

    def test_createDfa(self):
        from rte.xymbolyco import createDfa
        for depth in range(4):
            for r in range(num_random_tests):
                rt = random_rte(depth)
                pattern,transitions, accepting, exit_map, combine_labels = rt.to_dfa(depth * 10).serialize()
                self.assertTrue(createDfa(pattern,transitions, accepting, exit_map, combine_labels))

    def test_extract_discovered_case_57(self):
        rt1 = Singleton(SNot(SOr(STop,SMember())))
        rt2 = rt1.to_dfa(True).to_rte()[True]
        empty1 = Or(And(rt2,Not(rt1)),
                    And(Not(rt2),rt1)).canonicalize()
        rt_empty = empty1.to_dfa(True).to_rte()[True]
        self.assertEqual(rt_empty,EmptySet)

    def test_extract_rte(self):
        for depth in range(5):
            for r in range(num_random_tests):
                rt1 = random_rte(depth)
                extracted = rt1.to_dfa(depth*10).extract_rte()
                if extracted:
                    rt2 = extracted[depth*10]
                    empty1 = Or(And(rt2,Not(rt1)),
                               And(Not(rt2),rt1)).canonicalize()
                    if empty1 != EmptySet:
                        rt_empty = empty1.to_dfa(True).to_rte()[True]
                        self.assertEqual(rt_empty,EmptySet,
                                         f"rt1={rt1}\n" +
                                         f"rt2={rt2}\n" +
                                         f"empty={empty1}\n" +
                                         f"  --> {rt_empty}\n"
                                         )



if __name__ == '__main__':
    unittest.main()
