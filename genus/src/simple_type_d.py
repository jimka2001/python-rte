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

class SimpleTypeD(metaclass=ABCMeta):
	"""SimpleTypeD is the abstract class that mothers all of the 
	representations of type in Genus"""

	#overloading operators
	def __or__(self, t):
		raise NotImplementedError

	def __and__(self, t):
		raise NotImplementedError

	#unfortunately, this one can't be overloaded
	def unary_not(self, t):
		raise NotImplementedError

	def __sub__(self, t):
		raise NotImplementedError

	def __xor__(self, t):
		raise NotImplementedError

	@abstractmethod
	def typep(self, any):
		"""Returns whether a given object belongs to this type.
		It is a set membership test.
			@param a the object we want to check the type
			@return a Boolean which is true is a is of this type"""

	def disjoint(self, td):
		raise NotImplementedError

	#for performance reasons, do not call directly, rather use the inhabited method as it stores the result
	def _inhabited_down(self):
		return None

	def inhabited(self):
		if not hasattr(inhabited, "holding"):
			inhabited.holding = self._inhabited_down()
		return inhabited.holding

	def _disjoint_down(self, t):
		if(inhabited()):
			return None
		else:
			return True

	def subtypep(self, t):
		raise NotImplementedError

	@staticmethod
	def fixed_point(w, f, good_enough):
		v = w
		history = []

		while(True):
			v2 = f(v)
			if good_enough(v, v2):
				return v	
			if v2 in history:
				for debug_v2 in history:
					print(debug_v2)
				raise AssertionError("Failed: fixedPoint encountered the same value twice:", v2)
			else:
				history.append(v)
				v = v2
		return v

	def debug_find_simplifier(tag, t, simplifiers):
		"""this debug version displays the simplification step tag went through"""
		print(tag, "starting with", t)
		found = find_simplifier(simplifiers)
		if found == t:
			print(tag, "remained", found)
		else:
			print(tag)
			print("changed to")
			print(found)

	def find_simplifier(self, simplifiers):
		"""simplifiers is a list of 0-ary functions.   
		Calling such a function either returns `this` or something else.  
		We call all the functions in turn, as long as they return `this`.  
		As soon as such a function returns something other than `this`, 
		then that new value is returned from find_simplifier.
		As a last resort, `this` is returned."""

		if simplifiers is None:
			return self

		for s in simplifiers:
			out = s()
			if self == t2:
				continue
			return out
	
	#for performance reasons, do not call directly, rather use the to_dnf method as it stores the result
	def _compute_dnf(self):
		return self

	def to_dnf(self):
		if not hasattr(to_dnf, "holding"):
			to_dnf.holding = self._compute_dnf()
		return to_dnf.holding

	#for performance reasons, do not call directly, rather use the to_dnf method as it stores the result
	def _compute_cnf(self):
		return self

	def to_cnf(self):
		if not hasattr(to_cnf, "holding"):
			to_cnf.holding = self._compute_cnf()
		return to_cnf.holding

	def maybe_dnf(self, nf):
		raise NotImplementedError

	def maybe_cnf(self, nf):
		raise NotImplementedError

	def canonicalize_once(self, nf):
		return self

	canonicalized_hash = {}

	def canonicalize(self, nf):
		if not nf in self.canonicalized_hash:
			#we're in the case were the result isn't memoized,
			#so we compute it
			processor = lambda t: t.canonicalize_once(nf)
			good_enough = lambda a, b: type(a) == type(b) and a == b
			
			res = fixed_point(self, processor, good_enough)
			
			self.canonicalized_hash |= {nf: res}

		#tell the perhaps new object it is already canonicalized (TODO: could I just put this in the if ?)
		self.canonicalized_hash[nf].canonicalized_hash[nf] = canonicalized_hash[nf]
		return self.canonicalized_hash[nf]

	def supertypep(self, t):
		""" Returns whether this type is a recognizable supertype of another given type.
		  It is a superset test. This might be undecidable.
		 
		  @param t the type we want to check the inclusion in this type
		  @return an optional Boolean which is true if this type is a supertype of t
		"""
		return t.subtypep(self)

	def cmp_to_same_class_obj(self, t):
		raise TypeError('cannot compare type designators', type(self), 'vs', type(t))