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

__init__ 3
__str__ 3
create 3
unit 3
zero 3
annihilator 1
same_combination 3
typep 3
inhabited_down 0
_disjoint_down 0
subtypep 3
canonicalize_once 0
compute_dnf 0
"""

from genus.simple_type_d import SimpleTypeD 
from genus.s_empty import SEmpty
from genus.s_top import STop

class SOr(SimpleTypeD):
	"""docstring for SOr"""
	def __init__(self, tds):
		super(SOr, self).__init__()
		self.tds = tds

	def __str__(self):
		s = "[Or "
		for arg in self.tds:
			s += str(arg)
			s += ","
		s += "]"
		return s

	@staticmethod
	def create(tds):
		return SOr(tds)

	unit = SEmpty.get_epsilon()
	zero = STop.get_omega()

	def annihilator(a, b):
		return b.subtypep(a)

	def same_combination(self, t):
		if not type(t) == type(self):
			return False
		for arg in self.tds:
			if not arg in t.tds:
				return False
		for arg in t.tds:
			if not arg in self.tds:
				return False
		return True

	def typep(self, a):
		for td in self.tds:
			if(td.typep(a)):
				return True
		return False

	def subtypep(self, t):
	    if not self.tds:
	        return SEmpty.get_epsilon().subtypep(t)        
	    elif hasattr(t, "typep") and all(t.typep(arg) for arg in self.tds):
	        return True
	    #elif hasattr(t, "inhabited") and t.inhabited() and self.inhabited() and all(x.disjoint(t) for x in self.tds):
	    #    return False
	    else:
	        return super().subtypep(t)

	def inhabited_down(self):
		raise NotImplementedError

	def _disjoint_down(self, t):
		raise NotImplementedError