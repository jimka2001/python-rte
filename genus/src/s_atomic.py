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

from simple_type_d import SimpleTypeD, TerminalType

class SAtomic(SimpleTypeD, TerminalType):
	"""The atoms of our type system: a simple type built from a native python type."""
	# reminder: the types are:
		# numerical: "int", "float", "complex"
		# sequential: "list", "tuple", "range" (+ * binary sequences + * text sequences)
		# binary sequential: "bytes", "bytearray", "memoryview"
		# text sequential: "str"
		# in addition, all classes are types and all types are classes

	def __init__(self, wrapped_class):
		super(SAtomic, self).__init__()
		self.wrapped_class = wrapped_class

	def __str__(self):
		return str(self.wrapped_class)
	
	def typep(self, a):
		#check that this does what we want (looks like it does but eh)
		return isinstance(self.wrapped_class, a)

	def _inhabited_down(self):
		try:
			return not issubclass(self.wrapped_class, type(None))
		except Exception as e:
			#the try block may only fail if self.wrapped_class is not a class, in which case it is a value and contains nothing
			return False 
		
	@static
	def is_final():
		"""Okay, so, python does not per say handle final classes,
		however since python3.8, the community added a @final
		decorator and it got added to the language. 
		
		At the same time, for backcompatibility reasons, many
		people still use various hacks like making a final
		class to hijack the __new__ and raise an exception
		on subclassing.

		Even Guido used a haxx (through the C API) to make
		a few classes (like the bool class) final ! 
		To deal with everything people used, use, or will use,
		my solution is to just make use of the duck typing magic.

		If it looks like a duck and quacks like a duck,
		it is probably a duck. Apply the same to final"""
		try:
			pass
		except Exception as e:
			raise e
		pass

	def _disjoint_down(self, t):
		#TODO: find a way to cmpte isfinal and isInterface if needed
		if isinstance(t, SEmpty):
			return True
		elif isinstance(t, STop):
			return False
		elif isinstance(t, SAtomic):
			if t == self.wrapped_class:
				return False
			elif issubclass(self.wrapped_class, t) or issubclass(t, self.wrapped_class):
				return False
			"""elif is_final(self.wrapped_class) or is_final(t):
				return True
			elif is_interface(self.wrapped_class) or is_interface(t):
				return False # maybe ?"""
			else:
				return True
		else:
			return super._disjoint_down(t)

	def subtypep(self, s):
		if isinstance(s, SEmpty):
			return False
		elif isinstance(s, STop):
			return True
		elif isinstance(s, SAtomic):
			return isinstance(s, self.wrapped_class)
		#TODO: implement when SMember is done
		#TODO: implement when SEql is done
		#TODO: implement when SNot is done
		#TODO: implement when SOr is done
		#TODO: implement when SAnd is done
		#TODO: implement when SCustom is done

	def canonicalize_once(nf = None):
		return SAtomic(self.wrapped_class)

	def cmp_to_same_class_obj(self, td):
		if self == td:
			return False
		elif isinstance(td, SAtomic):
			return str(self.wrapped_class) < str(self.td)
		else:
			super.cmp_to_same_class_obj(td)

#TODO: ask about what object SAtomic is exactly