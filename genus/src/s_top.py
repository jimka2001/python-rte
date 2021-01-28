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

from simple_type_d import SimpleTypeD 

class STop(SimpleTypeD):
	"""The super type, super type of all types."""
	def __init__(self):
		super(STop, self).__init__()

	def __str__(self):
		return "Top"

	def typep(self, any):
		return True

	def _inhabited_down(self):
		return True

	def _disjoint_down(self, t):
		return type(t) is SEmpty

	def subtypep(self, t):
		return type(t) == STop

	def cmp_to_same_class_obj(self, t):
		return False

#TODO: move the tests in their own files once this is packaged:
def t_STop():
	a = STop() #TODO: make this class uninstantiable and provide one single instance
	
	#str(a) has to be "Top"
	assert(str(a) == "Top")

	#a.typep(t) indicates whether t is a subtype of a, which is always the case by definition
	assert(a.typep(object))
	assert(a.typep(a))

	#obviously, a is inhabited as it contains everything by definition
	assert(a._inhabited_down)

	#a is never disjoint with anything but the empty subtype
	assert(not a._disjoint_down(object))
	assert(a._disjoint_down(SEmpty()))

	#on the contrary, a is never a subtype of any type 
	#since types are sets and top is the set that contains all sets
	assert(not a.subtypep(object))
	assert(not a.subtypep(type(a)))

	#my understanding is that the top type is unique so it can't be positively compared to any object
	assert(not a.cmp_to_same_class_obj(a))
	assert(not a.cmp_to_same_class_obj(object))