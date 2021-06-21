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

import simple_type_d

class SOr(SimpleTypeD):
	"""docstring for SOr"""
	def __init__(self, tds):
		super(SOr, self).__init__()
		self.tds = tds

	def __str__(self):
		s = "[Or "
		for arg in self.arg_list:
			s += str(arg)
			s += ","
		s += "]"
		return s

	def create(tds):
		return SOr(tds)

	unit = SEmpty.get_epsilon()
	zero = STop.get_omega()

	def annihilator(a, b):
		return b.subtypep(a)

	def same_combination(self, td):
		return td in self.tds #this may be wrong

	def typep(self, a):
		for td in self.td:
			if(td.typep(a)):
				return True
		return False

	def inhabited_down(self):
		raise NotImplementedError