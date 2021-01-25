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

from simple_type_d import SimpleTypeD 

class SCombination(SimpleTypeD):
	
	#is create really needed ? it could be an __init__
	@abstractmethod
	def __init__(self, arglist):
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
			#TODO: implement when SNot is implemented
			raise NotImplementedError

		def l_4():
			# SAnd(A,STop,B) ==> SAnd(A,B),  unit=STop,   zero=SEmpty
			# SOr(A,SEmpty,B) ==> SOr(A,B),  unit=SEmpty, zero=STop
			#TODO: implement when I understand the _* idiom
			if self.unit in self.arglist:
				return SCombination(list(filter(lambda x: x != self.unit)))
			else:
				return self

		def l_5():
			# (and A B A C) -> (and A B C)
			# (or A B A C) -> (or A B C)
			#list(set(x)) with x is a list ensures the elements are distinct
			return SCombination(list(set(self.arglist)))
		
		def l_6():
			# (and A (and B C) D) --> (and A B C D)
			# (or A (or B C) D) --> (or A B C D)
			pass
		
		simplifiers = []

		