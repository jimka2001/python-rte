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
from s_top import STopImpl

"""
[0-3] Advancement tracker
__init__ 1
__str__ 1
typep 1
inhabited_down 1 
disjoint_down 0
subtypep 0 
canonicalize_once 1 
cmp_to_same_class_obj 1
apply 1
"""


class SAtomic(SimpleTypeD, TerminalType):
	"""The atoms of our type system: a simple type built from a native python type."""
	# reminder: the types are:
	# numerical: "int", "float", "complex"
	# sequential: "list", "tuple", "range" (+ * binary sequences + * text sequences)
	# binary sequential: "bytes", "bytearray", "memoryview"
	# text sequential: "str"
	# in addition, all classes are types and all types are classes

	def __init__(self, wrapped_class):
		import inspect
		super(SAtomic, self).__init__()
		assert inspect.isclass(wrapped_class)
		self.wrapped_class = wrapped_class

	def __str__(self):
		return "SAtomic(" + self.wrapped_class.__name__ + ")"

	def __eq__(self, that):
		return isinstance(that, SAtomic) \
			and self.wrapped_class is that.wrapped_class

	def __hash__(self):
		return hash(self.wrapped_class)
	
	def typep(self, a):
		# check that this does what we want (looks like it does but eh)
		return isinstance(a, self.wrapped_class)

	def _inhabited_down(self):
		try:
			return not issubclass(self.wrapped_class, type(None))
		except Exception as _e:
			# the try block may only fail if self.wrapped_class is not a class, in which case it is a value and contains nothing
			return False 
		
	@staticmethod
	def is_final():
		"""Okay, so, python does not per say handle final classes,
		however since python3.8, the community added a @final
		decorator and it got added to the language. 
		
		At the same time, for back compatibility reasons, many
		people still use various hacks like making a final
		class to hijack the __new__ and raise an exception
		on subclassing.

		Even Guido used a hack (through the C API) to make
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


	def _subtypep_down(self, s):
		from s_empty import SEmptyImpl, SEmpty
		from s_member import SMemberImpl
		from s_not import SNot
		from s_or import SOr
		from s_and import SAnd
		from s_custom import SCustom

		if self.inhabited() is False:
			return True
		elif isinstance(s, SEmptyImpl):
			# here we know self.inhabited() is either None or True
			return None if self.inhabited() is None else True
		elif isinstance(s, STopImpl):
			return True
		elif isinstance(s, SAtomic):
			if s.inhabited() is False:
				return self.subtypep(SEmpty)
			elif s.inhabited() is None:
				return None
			elif self.inhabited() is None and s.inhabited() is True:
				return None
			elif self.inhabited() is True and s.inhabited() is True:
				return issubclass(self.wrapped_class, s.wrapped_class)
			else:
				raise NotImplementedError
		elif isinstance(s, SMemberImpl):
			return False  # no finite list exhausts all elements of a class
		elif isinstance(s, SNot):
			return super()._subtypep_down(s)
		elif isinstance(s, SOr):
			if any(self.subtypep(td) is True for td in s.tds):
				return True
			elif all(self.disjoint(td) is True for td in s.tds):
				return False
			else:
				return super()._subtypep_down(s)
		elif isinstance(s, SAnd):
			if all(self.subtypep(td) is True for td in s.tds):
				return True
			elif all(self.disjoint(td) is True for td in s.tds):
				return False
			else:
				return super()._subtypep_down(s)
		elif isinstance(s, SCustom):
			return super()._subtypep_down(s)
		else:
			return super()._subtypep_down(s)

	def canonicalize_once(self, nf=None):
		return SAtomic(self.wrapped_class)

	def cmp_to_same_class_obj(self, td):
		if type(self) != type(td):
			return super().cmp_to_same_class_obj(td)
		elif self == td:
			return False
		else:
			return self.wrapped_class.__name__ < td.wrapped_class.__name__
    def _disjoint_down(self, t):
        assert isinstance(t, SimpleTypeD)
        from s_empty import SEmptyImpl
        ct = self.wrapped_class

        if isinstance(t, SEmptyImpl):
            return True
        elif isinstance(t, STopImpl):
            return False
        elif isinstance(t, SAtomic):
            from utils import get_all_subclasses
            tp = t.wrapped_class
            if self.inhabited() is False:
                return True
            elif tp == ct:
                return False
            elif issubclass(tp, ct) or issubclass(ct, tp):
                # is either a subclass of the other
                return False
            else:
                # if they have a common subclass, they are not disjoint

                # return not any(c for c in get_all_subclasses(ct)
                # 	               if c in tp_subclasses)

                # 2 linear searches should be faster than one n^2 search
                # by iterating over both lists of subclasses and asking whether the
                #  other is a superclass of it?
                return not (any(issubclass(c, tp) for c in get_all_subclasses(ct))
                            or any(issubclass(c, ct) for c in get_all_subclasses(tp)))
        else:
            return super()._disjoint_down(t)
