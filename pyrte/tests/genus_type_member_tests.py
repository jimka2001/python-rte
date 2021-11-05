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


class GenusMemberTypeCase(unittest.TestCase):

    def test_member_1(self):
        self.assertTrue(SMember(1, 2, 3).typep(1))

    def test_member_2(self):
        self.assertFalse(SMember(1, 2, 3).typep(1.0))

    def test_member_3(self):
        self.assertTrue(SOr(SMember(1, 2, 3), SEql(1.0)).typep(1))

    def test_member_4(self):
        self.assertTrue(SOr(SMember(1, 2, 3), SEql(1.0)).typep(1.0))

    def test_member_5(self):
        self.assertTrue(SOr(SAtomic(int), SEql(1.0)).typep(1.0))

    def test_member_6(self):
        self.assertTrue(SOr(SAtomic(int), SEql(1.0)).typep(1))

    def test_member_7(self):
        self.assertTrue(SAtomic(int).subtypep(SOr(SAtomic(int), SEql(1.0))))

    def test_member_8(self):
        self.assertEqual(SOr(SAtomic(int), SEql(1)).canonicalize(),
                         SAtomic(int))

    def test_member_9(self):
        self.assertNotEqual(SOr(SAtomic(int), SEql(1.0)).canonicalize(),
                            SAtomic(int))

    def test_member_10(self):
        self.assertNotEqual(SOr(SMember(1, 2, 3), SEql(1.0)).canonicalize(),
                            SMember(1, 2, 3))

    def test_member_11(self):
        self.assertEqual(SMember(1, 1.0).canonicalize(),
                         SMember(1, 1.0))

    def test_member_12(self):
        self.assertNotEqual(SMember(1, 1.0).canonicalize(),
                            SEql(1))
        self.assertNotEqual(SMember(1, 1.0).canonicalize(),
                            SEql(1.0))

    def test_member_13(self):
        self.assertFalse(SMember(1, 1.0).subtypep(SEql(1)))
        self.assertFalse(SMember(1, 1.0).subtypep(SEql(1.0)))

    def test_member_14(self):
        self.assertTrue(SEql(1).subtypep(SMember(1, 1.0)))
        self.assertTrue(SEql(1.0).subtypep(SMember(1, 1.0)))

    def test_disjoint_1(self):
        self.assertFalse(SMember(1, 1.0, 2, 2.0).disjoint(SMember(1, 2, 3)))
        self.assertFalse(SMember(1, 1.0, 2, 2.0).disjoint(SMember(1.0, 2.0, 3.0)))
        self.assertFalse(SMember(1, 1.0, 2, 2.0).disjoint(SMember(1.0, 1)))

    def test_disjoint_2(self):
        self.assertFalse(SMember(1, 1.0, 2, 2.0).canonicalize().disjoint(SMember(1, 2, 3)))
        self.assertFalse(SMember(1, 1.0, 2, 2.0).canonicalize().disjoint(SMember(1.0, 2.0, 3.0)))
        self.assertFalse(SMember(1, 1.0, 2, 2.0).canonicalize().disjoint(SMember(1.0, 1)))

    def test_eql_1(self):
        self.assertNotEqual(SEql(1),SEql(1.0))
        self.assertEqual(SEql(1), SEql(1))
        self.assertEqual(SEql(1.0), SEql(1.0))


if __name__ == '__main__':
    unittest.main()
