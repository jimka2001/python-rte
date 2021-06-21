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
#   maybe rewrite the static variable using methods as properties ?

""" test-coverage as (method name, state[0-3] {0 not implemented, 1 implemented, 2 partially tested,  3 fully done})
__or__  0
__and__     0
__unary_not__ 0
__sub__     0
__xor__     0
typep       3
disjoint    2
_inhabited_down     3
inhabited   3
_disjoint_down  3
subtypep
fixed_point 3
debug_find_simplifier   1
find_simplifier     1
_compute_dnf    3
to_dnf  3
_compute_cnf    3
to_cnf  fully done
maybe_dnf   2
maybe_cnf   2
canonicalize_once   3
canonicalize    3
supertypep  1
cmp_to_same_class_obj   3
"""

from genus_types import NormalForm
from abc import ABCMeta, abstractmethod
from utils import generate_lazy_val


#is it useful, though ? all classes are types by default in python
class TerminalType(metaclass=ABCMeta):
    """This class is just here to emulate the TerminalType trait in Scala"""
    @abstractmethod
    def __init__(self):
        super().__init__()

class SimpleTypeD(metaclass=ABCMeta):
    """SimpleTypeD is the abstract class that mothers all of the 
    representations of type in Genus"""
    def __init__(self):
        self.canonicalized_hash = {}

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
        td_disjoint_this = generate_lazy_val(lambda: td._disjoint_down(self))

        #og_name in scala lazy: c1
        self_canonicalized = generate_lazy_val(lambda: self.canonicalize())

        #og_name in scala lazy: c2
        td_canonicalized = generate_lazy_val(lambda: td.canonicalize())

        #og_name in scala lazy: dc12
        canon_self_disjoint_td = generate_lazy_val(lambda: self_canonicalized()._disjoint_down(td_canonicalized))

        #og_name in scala lazy: dc21
        canon_td_disjoint_self = generate_lazy_val(lambda: td_canonicalized()._disjoint_down(self_canonicalized))

        if self == td and self.inhabited() is not None:
            return not self.inhabited()
        
        elif this_disjoint_td is not None:
            return this_disjoint_td

        elif not td_disjoint_this() is None:
            return td_disjoint_this()
        
        elif self_canonicalized() == td_canonicalized() and self_canonicalized().inhabited() is not None:
            return not self_canonicalized().inhabited()
        
        elif canon_self_disjoint_td() is not None:
            return canon_self_disjoint_td()
        else:
            return canon_td_disjoint_self()

    #for performance reasons, do not call directly, rather use the inhabited method as it stores the result
    def _inhabited_down(self):
        return None

    def inhabited(self):
        if not hasattr(self, "hold_inhabited"):
            self.hold_inhabited = self._inhabited_down()
        return self.hold_inhabited

    def _disjoint_down(self, t):
        if(self.inhabited() is False):
            return True
        else:
            return None

    def subtypep(self, t):
        from genus_types import orp, andp, topp
        def or_result():
            return True if orp(t) and any(self.subtypep(a) is True for a in t.tds) \
                else None

        def and_result():
            return True if andp(t) and all(self.subtypep(a) is True for a in t.tds) \
                else None

        if type(self) == type(t) and self == t:
            return True
        elif topp(t.canonicalize()):
            return True
        elif or_result() is True:
            return True
        elif and_result() is True:
            return True
        else:
            return self._subtypep_down(t)

    def _subtypep_down(self,t):
        from genus_types import notp
        if notp(t) and self.disjoint(t.s):
            return True
        elif self.inhabited() is False:
            return True
        elif self.inhabited is True and t.inhabited is False:
            return False
        else:
            return None

    #for performance reasons, do not call directly, rather use the to_dnf method as it stores the result
    def _compute_dnf(self):
        return self

    def to_dnf(self):
        if not hasattr(self, "hold_todnf"):
            self.hold_todnf = self._compute_dnf()
        return self.hold_todnf

    #for performance reasons, do not call directly, rather use the to_dnf method as it stores the result
    def _compute_cnf(self):
        return self

    def to_cnf(self):
        if not hasattr(self, "hold_tocnf"):
            self.hold_tocnf = self._compute_cnf()
        return self.hold_tocnf

    def maybe_dnf(self, nf):
        if NormalForm.DNF is nf:
            return self.to_dnf()
        else:
            return self

    def maybe_cnf(self, nf):
        if NormalForm.CNF is nf:
            return self.to_cnf()
        else:
            return self

    def canonicalize_once(self, nf = None):
        return self

    def canonicalize(self, nf = None):
        from utils import fixed_point

        if nf not in self.canonicalized_hash:
            def processor(td):
                return td.canonicalize_once(nf)

            def good_enough(a,b):
                return type(a) == type(b) and a == b
            
            res = fixed_point(self, processor, good_enough)
            self.canonicalized_hash |= {nf: res}

        #tell the perhaps new object it is already canonicalized (TODO: could I just put this in the if ?)
        self.canonicalized_hash[nf].canonicalized_hash[nf] = self.canonicalized_hash[nf]
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
