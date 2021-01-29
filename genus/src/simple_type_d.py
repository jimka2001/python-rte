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

# TODO:
# 	maybe rewrite the static variable using methods as properties ?

from genus_types import NormalForm
from abc import ABCMeta, abstractmethod

#is it useful, though ? all classes are types by default in python
class TerminalType(metaclass=ABCMeta):
	"""This class is just here to emulate the TerminalType trait in Scala"""
	@abstractmethod
	def __init__(self):
		pass

class SimpleTypeD(metaclass=ABCMeta):
	"""SimpleTypeD is the abstract class that mothers all of the 
	representations of type in Genus"""

	#overloading operators
	def __or__(self, t):
		#implement when SOr is implemented
		raise NotImplementedError

	def __and__(self, t):
		#implement when SAnd is implemented
		raise NotImplementedError

	#unfortunately, this one can't be overloaded
	def unary_not(self):
		#implement when SNot is implemented
		raise NotImplementedError

	def __sub__(self, t):
		#implement when SAnd and SNot are implemented
		raise NotImplementedError

	def __xor__(self, t):
		#implement when SNot, SAnd and SOr are implemented
		raise NotImplementedError

	@abstractmethod
	def typep(self, any):
		"""Returns whether a given object belongs to this type.
		It is a set membership test.
			@param a the object we want to check the type
			@return a Boolean which is true is a is of this type"""

	def disjoint(self, td):
		"""okay, here I am doing some weird magic so I'll explain:
		python does NOT have a lazy keyword, so I need to emulate it
		I thus create utility functions within disjoint and within them,
		I put static attributes. On the first call to those functions, 
		the computations are performed and then cached in said
		static attribute, so that on later calls they are output in O(1)"""
		
		#og_name in scala: d1
		this_disjoint_td = self._disjoint_down(td)
		
		#og_name in scala lazy: d2
		def td_disjoint_this(self, td):
			if not hasattr(td_disjoint_this, "holding"):
				td_disjoint_this.holding = td._disjoint_down(self)
			return td_disjoint_this.holding

		#og_name in scala lazy: c1
		def self_canonicalized(self, td):
			if not hasattr(self_canonicalized, "holding"):
				self_canonicalized.holding = self.canonicalize()
			return self_canonicalized.holding

		#og_name in scala lazy: c2
		def td_canonicalized(self, td):
			if not hasattr(td_canonicalized, "holding"):
				td_canonicalized.holding = td.canonicalize()
			return td_canonicalized.holding

		#og_name in scala lazy: dc12
		def canon_self_disjoint_td(self, td):
			if not hasattr(canon_self_disjoint_td, "holding"):
				canon_self_disjoint_td.holding = self_canonicalized()._disjoint_down(td_canonicalized())
			return canon_self_disjoint_td.holding

		#og_name in scala lazy: dc21
		def canon_td_disjoint_self(self, td):
			if not hasattr(canon_td_disjoint_self, "holding"):
				canon_td_disjoint_self.holding = td_canonicalized()._disjoint_down(self_canonicalized())
			return canon_td_disjoint_self.holding

		#todo: check that "_.nonEmpty" is well translated as "inhabited not none"
		if self == td and self.inhabited() is not None:
			return self.inhabited().map(lambda x: unary_not(x))
		
		elif this_disjoint_td() and this_disjoint_td() is not None:
			return this_disjoint_td()

		elif td_disjoint_this() and td_disjoint_this is not None:
			return td_disjoint_this()
		
		elif self_canonicalized() == td_canonicalized() and self_canonicalized() is not None:
			return self_canonicalized().inhabited().map(lambda x: unary_not(x))
		
		elif canon_self_disjoint_td() is not None:
			return canon_self_disjoint_td()
		
		else:
			canon_td_disjoint_self()

	#for performance reasons, do not call directly, rather use the inhabited method as it stores the result
	def _inhabited_down(self):
		return None

	def inhabited(self):
		if not hasattr(inhabited, "holding"):
			inhabited.holding = self._inhabited_down()
		return inhabited.holding

	def _disjoint_down(self, t):
		if(inhabited() == False):
			return True
		else:
			return None

	def subtypep(self, t):
		#implement when SNot is implemented
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
		if NormalForm.DNF in nf:
			return to_dnf()
		else:
			return self

	def maybe_cnf(self, nf):
		if NormalForm.CNF in nf:
			return to_cnf
		else:
			return self

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

def t_SimpleTypeD():

	#ensuring SimpleTypeD is abstract
	try:
		foo = SimpleTypeD()
		assert(False)
	except:
		pass

	#ensuring typep is an abstract method
	try:
		class ChildSTDNoTypep(SimpleTypeD):
			"""just for testing"""
			def __init__(self):
				super(ChildSTDNoTypep, self).__init__()	
		foo = ChildSTDNoTypep()
		del ChildSTDNoTypep
		assert(False)
	except:
		pass

	class ChildSTD(object):
		"""docstring for ChildSTD"""
		def __init__(self):
			super(ChildSTD, self).__init__()
			
		def typep(a):
			pass

	child = ChildSTD()
	print(str(child))
	print(child.__dict__)

t_SimpleTypeD()


		
					