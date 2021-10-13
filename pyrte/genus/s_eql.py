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

from genus.s_member import SMemberImpl
from genus.simple_type_d import SimpleTypeD, TerminalType
from typing import Any, Literal, Optional
from typing_extensions import TypeGuard


class SEql(SMemberImpl, TerminalType):
	"""The equal type, a type that is equal to a given object.
	It has holds an "a" which is the object defining the type
	"""
	def __init__(self, a: Any) -> None:
		super(SEql, self).__init__(a)
		self.a = a
	
	def __str__(self) -> str:
		return "[= " + str(self.a) + "]"

	def __eq__(self, that: Any) -> bool:
		return type(self) is type(that) and \
			self.a == that.a

	def __hash__(self):
		return hash(self.a)

	def typep(self, b: Any) -> bool:
		return self.a == b

	def inhabited_down(self) -> Literal[True]:
		return True

	def disjoint_down(self, t: SimpleTypeD) -> Optional[bool]:
		assert isinstance(t, SimpleTypeD)
		return not t.typep(self.a)

	def subtypep(self, t) -> Optional[bool]:
		return t.typep(self.a)


def eqlp(this: Any) -> TypeGuard[SEql]:
	return isinstance(this, SEql)
