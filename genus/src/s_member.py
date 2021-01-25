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
from simple_type_d import SimpleTypeD, TerminalType

class SMemberImpl(SimpleTypeD, TerminalType):
	"""docstring for SMemberImpl"""
	def __init__(self, arglist):
		super(SMemberImpl, self).__init__()
		self.arglist = arglist
	
	def __str__(self):
		out = "[Member "
		for arg in self.arglist:
			out += str(arg)
			out += ","
		out += "]"

	def typep(self, a):
		return a in self.arglist

	def inhabited_down(self):
		return self.arglist #arglist not empty

	def _disjoint_down(self):
		for arg in arglist:
			if t.typep(arg):
				return False
		return True

	def subtypep(t):
		return all(map(lambda x: t.typep(x), self.arglist))

	def canonicalizeOnce(self, nf):
		def cmp(a, b):
			if a == b:
				return False
			elif type(a) != type(b):
				return str(type(a)) < str(type(b))
			elif str(a) != str(b):
				return str(a) < str(b)
			else:
				raise Exception("Cannot canonicalize", self, "because it contains two different elements with the same str():", str(a))

		if type(self.arglist) is list and not self.arglist:
			return SEmpty()
		elif type(self.arglist) is list:
			#TODO: implement once SEql is implemented
			raise NotImplementedError
		else:
			#TODO: implement once Types.scala is implemented
			raise NotImplementedError

	def cmp_to_same_class_obj(self, t):
		raise NotImplementedError 
		if this == t:
			return True
		else:
			if type(t) is SMember:
				def comp(a, b):
					if not (a and b):
						raise Exception("not expecting equal sequences $xs, $ys")