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


class SEql(SMemberImpl):
	"""The equal type, a type that is equal to a given object.
	It has holds an "a" which is the object defining the type
	"""
	def __init__(self, a):
		super(SEql, self).__init__()
		self.a = a
	
	def __str__(self):
		return "[= " + self.a + "]"

	def typep(self, b):
		return a == b;

	def _inhabited_down(self):
		return True

	def _disjoint_down(self, t):
		return not t.typep(self.a)

	def subtypep(self, t):
		return t.typep(self.a)

	def cmp_to_same_class_obj(self, t):
		if self == t:
			return False
		elif type(t) == SEql:
			if not type(self.a) == type(t.a):
				return str(self.a) <= str(t.a)
			elif not str(self.a) == str(self.b):
				return str(a) <= str(b)
			else:
				raise TypeError('cannot compare(',str(self),') and (', str(t),') because they have different types but those types\' str are the same')
		else:
			return super.cmp_to_same_class_obj(t)