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
typep 1
inhabited_down 1
disjoint_down 1
subtypep 1
canonicalize_once 1
compute_dnf 0
compute_cnf 1
cmp_to_same_class_obj 3
"""
from genus import *


class SNot(SimpleTypeD):
	"""A negation of a type.
	@param s the type we want to get the complement"""
	def __init__(self, s):
		super(SNot, self).__init__()
		assert isinstance(s, SimpleTypeD)
		self.s = s
	
	def __str__(self):
		return "SNot(" + str(self.s) + ")"

	def __eq__(self, that):
		return type(self) is type(that) and \
			self.s == that.s

	def __hash__(self):
		return hash(self.s)

	def typep(self, a):
		return not self.s.typep(a)

	def inhabited_down(self):
		from genus.genus_types import topp, emptyp, memberp, eqlp, atomicp, notp
		if topp(self.s):
			return False
		elif emptyp(self.s):
			return True
		elif self.s == SAtomic(object):
			return False
		elif atomicp(self.s):
			return True
		elif memberp(self.s):
			return True
		elif eqlp(self.s):
			return True
		elif notp(self.s):
			return self.s.s.inhabited()
		else:
			return None

	def disjoint_down(self, t):
		assert isinstance(t, SimpleTypeD)
		# is SNot(s) disjoint with t
		# first we ask whether t is a subtype of s,
		#  t <: s = > not (s) // t
		if t.subtypep(self.s) is True:  # if it is empty this is empty and is thus evaluated as False
			return True
		else:
			return super().disjoint_down(t)

	def subtypep_down(self, t):
		from genus.utils import generate_lazy_val
		from genus.genus_types import notp, atomicp
		# SNot(a).subtypep(SNot(b)) iff b.subtypep(a)
		#    however b.subtypep(a) might return None
		os = generate_lazy_val(lambda: t.s.subtypep(self.s) if notp(t) else None)
		# SNot(SAtomic(Long)).subtype(SAtomic(Double)) ??

		def h():
			if not atomicp(t):
				return None
			elif not atomicp(self.s):
				return None
			elif self.s.disjoint(t):
				return False
			else:
				return None

		hosted = generate_lazy_val(h)

		if self.s.inhabited() is True and self.s.subtypep(t) is True:
			return False
		elif hosted() is not None:
			return hosted()
		elif os() is not None:
			return os()
		else:
			return super().subtypep_down(t)

	def canonicalize_once(self, nf=None):
		from genus.genus_types import notp, topp, emptyp
		if notp(self.s):
			return self.s.s.canonicalize_once(nf)
		elif topp(self.s):
			return SEmpty
		elif emptyp(self.s):
			return STop
		else:
			return SNot(self.s.canonicalize_once(nf)).to_nf(nf)

	def compute_dnf(self):
		# SNot(SAnd(x1, x2, x3))
		# --> SOr(SNot(x1), SNot(x2), SNot(x3)
		#
		# SNot(SOr(x1, x2, x3))
		# --> SAnd(SNot(x1), SNot(x2), SNot(x3))
		from genus.genus_types import orp, andp, createSOr, createSAnd
		if andp(self.s):
			return createSOr([SNot(td) for td in self.s.tds])
		elif orp(self.s):
			return createSAnd([SNot(td) for td in self.s.tds])
		else:
			return self

	def compute_cnf(self):
		# we convert a not to DNF or CNF the same way, i.e., by pushing down the SNot
		#   and converting SAnd to SOr
		return self.compute_dnf()

	def cmp_to_same_class_obj(self, td):
		from genus.genus_types import cmp_type_designators
		if type(self) != type(td):
			return super().cmp_to_same_class_obj(td)
		elif self == td:
			return 0
		else:
			return cmp_type_designators(self.s, td.s)
