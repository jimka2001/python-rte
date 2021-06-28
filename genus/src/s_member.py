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

"""
[0-3] Advancement tracker
__init__ 1
__str__ 1
typep 3
inhabited_down 1
disjoint_down 1
subtypep 1
canonicalize_once 0
cmp_to_same_class_obj 0

<???> case class SMember </???>
"""


class SMemberImpl(SimpleTypeD):
	"""docstring for SMemberImpl"""
	def __init__(self, *arglist):
		super(SMemberImpl, self).__init__()
		self.arglist = list(arglist)
	
	def __str__(self):
		return "SMember(" + ", ".join([str(x) for x in self.arglist]) + ")"

	def __eq__(self, that):
		return type(self) is type(that) and \
			set(self.arglist) == set(that.arglist)

	def __hash__(self):
		return hash(frozenset(self.arglist))

	def typep(self, a):
		return a in self.arglist

	def inhabited_down(self):
		return [] != self.arglist

	def disjoint_down(self, t2):
		assert isinstance(t2, SimpleTypeD)
		return not any(t2.typep(a) for a in self.arglist)

	def subtypep_down(self, t2):
		return all(t2.typep(a) for a in self.arglist)

	def canonicalize_once(self, _nf):
		return self

	def cmp_to_same_class_obj(self, t):
		if type(self) != type(t):
			return super().cmp_to_same_class_obj(t)
		elif self == t:
			return False
		else:
			def comp(a, b):
				if not a and not b:
					raise Exception(f"not expecting equal sequences {self.arglist}, {t.arglist}")
				elif not a:
					return True
				elif not b:
					return False
				elif a[0] == b[0]:
					return comp(a[1:], b[1:])
				elif str(a[0]) != str(b[0]):
					return str(a[0]) < str(b[0])
				else:
					raise Exception(f"different values which print the same {a[0]} vs {b[0]}")
			return comp(self.arglist, t.arglist)


class SMember(SMemberImpl, TerminalType):
	pass
