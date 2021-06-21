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

from types import NormalForm
from simple_type_d import SimpleTypeD

"""
[0-3] Advancement tracker
__init__ 1
__str__ 1
typep 1
_inhabited_down 1
_disjoint_down 1
subtypep 1
canonicalize_once 1
compute_dnf 0
compute_cnf 1
cmp_to_same_class_obj 0
"""

class SNot(SimpleTypeD):
	"""A negation of a type.
	@param s the type we want to get the complement"""
	def __init__(self, s):
		super(SNot, self).__init__()
		self.s = s
	
	__str__(self):
		return "[Not " + str(self.s) + "]"
	
	def typep(a):
		return not self.s.typep(a)

	def _inhabited_down(self):
		nothing = type(None)
		any = object
		if self.s == STop.get_omega():
			return False
		elif self.s == STop.get_epsilon():
			return True
		elif self.s == SAtomic(type(None)):
			return True
		elif self.s == SAtomic(object):
			return False
		elif isinstance(self.s, SAtomic):
			return True
		#elif SMember
		#elif SEql
		elif isinstance(self.s, SNot):
			return self.s.s.inhabited()
		else:
			return None

	def _disjoint_down(self, t):
		if t.subtypep(self.s) : #if it is empty this is empty and is thus evaluated as False
			return True
		else:
			return super._disjoint_down(t)

	def subtypep(self, t):
		def os(t):
			if not hasattr(os, "holding"):
				os.holding = lambda b: b.subtypep(self.s) if subclass(b, SNot) else None
			return os.holding
		if True in self.s.inhabited() and True in self.s.subtypep(t):
			return False
		elif os() #not empty:
			return os()
		else:
			return super.subtypep(t)

	def canonicalize_once(self, nf = None):
		if subclass(self.s, SNot):
			return self.s.canonicalize_once(nf)
		elif subclass(self.s, STop):
			return SEmpty
		elif subclass(self.s, SEmpty):
			return STop
		elif subclass(self.s, SimpleTypeD):
			return SNot(self.s.canonicalize_once(nf))
		else:
			raise TypeError("invalid given type ", type(self.s), " is not a SimpleTypeD")

	def compute_dnf(self):
		#TODO: implement when SAnd and SOr are done
		raise NotImplementedError

	def compute_cnf(self):
		#wait, what? This one was unexpected
		return self.to_dnf()

	def cmp_to_same_class_obj(self, td):
		if self == td:
			return False
		elif subclass(td, SNot):
			raise NotImplementedError
			#uncomment when cmp_type_designator is done
			#return cmp_type_designator(self.s, td)
		else:
			return super.cmp_to_same_class_obj(td)
