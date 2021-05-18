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

from abc import ABCMeta, abstractmethod
from genus.types import NormalForm
from genus.simple_type_d import SimpleTypeD

"""
[0-3] Advancement tracker

__init__ 1
create 1
unit 1
zero 1
annihilator 1
same_combination 1
canonicalize_once 1
cmp_to_same_class 0
"""
class SCombination(SimpleTypeD):
	"""SCombination is abstract because it has at least one abstractmethod and inherits from an abstract class"""
	def __init__(self, arglist):
		self.arglist = arglist
		pass

	@abstractmethod
	def create(self):
		pass

	@property
	@abstractmethod
	def unit(self):
		pass

	@property
	@abstractmethod
	def zero(self):
		pass

	@abstractmethod
	def annihilator(a, b):
		#apparently this name may change, so keep track of it
		pass
	
	def same_combination(td):
		return False

	def canonicalize_once(self, nf = None):
		#lambdas in python can only carry one expression, so i need inside defs
		def l_1():
			if not self.arglist: #empty or none
				# (and) -> STop,  unit=STop,   zero=SEmpty
				# (or) -> SEmpty, unit=SEmpty,   zero=STop
				return unit
				# (and A) -> A
				# (or A) -> A
			elif len(self.arglist) == 1: 
				return self.arglist[0]
			else:
				return self

		def l_2():
			# (and A B SEmpty C D) -> SEmpty,  unit=STop,   zero=SEmpty
			# (or A B STop C D) -> STop,     unit=SEmpty,   zero=STop
			if zero in self.arglist:
				return zero
			else:
				return self

		def l_3():
			# (and A (not A)) --> SEmpty,  unit=STop,   zero=SEmpty
			# (or A (not A)) --> STop,     unit=SEmpty, zero=STop
			if any(map(lambda td: SNot(td) in self.arglist, self.arglist)):
				return self.zero
			else:
				return self

		def l_4():
			# SAnd(A,STop,B) ==> SAnd(A,B),  unit=STop,   zero=SEmpty
			# SOr(A,SEmpty,B) ==> SOr(A,B),  unit=SEmpty, zero=STop
			if self.unit in self.arglist:
				return self.create(list(filter(lambda x: x != self.unit)))
			else:
				return self

		def l_5():
			# (and A B A C) -> (and A B C)
			# (or A B A C) -> (or A B C)
			#list(set(x)) with x is a list ensures the elements are distinct
			return self.create(list(set(self.arglist)))
		
		def l_6():
			# (and A (and B C) D) --> (and A B C D)
			# (or A (or B C) D) --> (or A B C D)
			if same_combination not in self.arglist:
				return self
			else:
				def flat_map(f, xs):
					ys = []
					for x in xs:
						ys.extend(f(x))
					return ys

				def flat_lambda(td):
					if isinstance(td, SCombination) and self.same_combination(td):
						return td.arglist
					else:
						return [td]
				return self.create(flat_map(flat_lambda, self.arglist)) 

		def l_7():
			i2 = self.create(map(lambda t: t.canonicalize(nf).sort(), self.arglist).sort(key = cmp_type_designators)).maybe_dnf(nf).maybe_cnf(nf)
			if self == i2:
				return self
			else:
				return i2

		def l_8():
			#I'm not absolutely sure about this
			def l_8_predicate(x):
				for td in self.arglist:
					if td == type(SNot) and annihilator(x, td.s) == True:
						return True
				return False
			found = list(filter(l_8_predicate, self.arglist))
			if found == []:
				return self
			else:
				return self.zero

		simplifiers = [l_1, l_2, l_3, l_4, l_5, l_6, l_7, l_8]
		return self.find_simplifier(simplifiers)

	def cmp_to_same_class_obj(self, td):
		#TODO: check this, this is is probably wrong
		if self == td:
			return False
		else:
			if isinstance(td, SCombination):
				#do it when Types is implemented
				raise NotImplementedError
			else:
				return super.cmp_to_same_class_obj(td)
