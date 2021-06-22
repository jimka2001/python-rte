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
"""
[0-3] Advancement tracker

__init__ 1
__str__ 1
create 1
unit 1
zero 1
annihilator 1
same_combination 1
typep 1
inhabited_down 0
_disjoint_down 0
subtypep 0
canonicalize_once 0
compute_cnf 0
"""

from s_combination import SCombination
from genus_types import createSOr
from s_empty import SEmpty
from s_top import STop


class SOr(SCombination):
	"""docstring for SOr"""
	def __init__(self, *tds):
		super(SOr, self).__init__(tds)

	def __str__(self):
		return "[SOr " + ",".join([str(td) for td in self.tds]) + "]"

	def create(self, tds):
		return createSOr(tds)

	unit = SEmpty
	zero = STop

	def annihilator(self, a, b):
		return b.subtypep(a)

	def typep(self, a):
		return any(td.typep(a) for td in self.tds)

	def inhabited_down(self):
		raise NotImplementedError
