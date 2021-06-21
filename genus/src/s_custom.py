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
typep 3
__str__ 3
_disjoint_down 1
_inhabited_down 1
subtypep 1
cmp_to_same_class_obj 1
apply 1
"""

from simple_type_d import SimpleTypeD, TerminalType

class SCustom(SimpleTypeD):
    """The super type, super type of all types."""
    def __init__(self, f, printable):
    	self.f = f
    	self.printable = printable

    def typep(self, a):
    	return self.f(a)

    def __str__(self):
    	return self.printable + "?"

    def _disjoint_down(self, t):
    	return super().disjointDown(t)

    def _inhabited_down(self):
    	return super()._inhabited_down()

    def subtypep(t):
    	return super().subtypep(t)

    def cmp_to_same_class_obj(self, t):
    	return str(self) < str(t)

    @staticmethod
    def apply(f):
    	return SCustom(f, str(f))

def t_scustom():
	l_odd = lambda x : x % 2 == 1
	guinea_pig = SCustom(l_odd, "[odd numbers]")
	assert(guinea_pig.f == l_odd)
	assert(guinea_pig.printable == "[odd numbers]")
	assert( str(guinea_pig) == "[odd numbers]?")
	for x in range(-100,100):
		if x % 2 == 1:
			assert(guinea_pig.typep(x))
		else:
			assert(not guinea_pig.typep(x))

t_scustom()