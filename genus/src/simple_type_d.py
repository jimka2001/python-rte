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
inhabited_down     3
inhabited   3
disjoint_down  3
subtypep
fixed_point 3
debug_find_simplifier   1
find_simplifier     1
compute_dnf    3
to_dnf  3
compute_cnf    3
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


# is it useful, though ? all classes are types by default in python
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

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def typep(self, a):
        """Returns whether a given object belongs to this type.
        It is a set membership test.
            @param a the object we want to check the type
            @return a Boolean which is true is a is of this type"""

    def disjoint(self, td):
        assert isinstance(td, SimpleTypeD)

        # these somewhat cryptic names were chosen to match the original Scala code
        d1 = generate_lazy_val(lambda: self.disjoint_down(td))
        d2 = generate_lazy_val(lambda: td.disjoint_down(self))
        c1 = generate_lazy_val(lambda: self.canonicalize())
        c2 = generate_lazy_val(lambda: td.canonicalize())
        dc12 = generate_lazy_val(lambda: c1().disjoint_down(c2()))
        dc21 = generate_lazy_val(lambda: c2().disjoint_down(c1()))

        if self == td and self.inhabited() is not None:
            return not self.inhabited()
        elif d1() is not None:
            return d1()
        elif d2() is not None:
            return d2()
        elif c1() == self and c2() == td:
            # no need to continue searching if canonicalization failed to produce simpler forms
            return None
        elif c1() == c2() and c1().inhabited() is not None:
            return not c1().inhabited()
        elif dc12() is not None:
            return dc12()
        elif dc21() is not None:
            return dc21()
        else:
            return None

    # for performance reasons, do not call directly, rather use the inhabited method as it stores the result
    def inhabited_down(self):
        return None

    def inhabited(self):
        if not hasattr(self, "hold_inhabited"):
            self.hold_inhabited = self.inhabited_down()
        return self.hold_inhabited

    def disjoint_down(self, t):
        assert isinstance(t, SimpleTypeD)
        if self.inhabited() is False:
            return True
        else:
            return None

    # Returns whether this type is a recognizable subtype of another given type. It is a subset test.
    # This might be undecidable.
    # Params:
    #   t – the type we want to check whether this type is included in
    # Returns:
    #   an optional Boolean (True/False/None) which is true if self is a subtype of t
    def subtypep(self, t):
        assert isinstance(t, SimpleTypeD)
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
            return self.subtypep_down(t)

    def subtypep_down(self, t):
        from genus_types import notp
        if notp(t) and self.disjoint(t.s) is True:
            return True
        elif self.inhabited() is False:
            return True
        elif self.inhabited() is True and t.inhabited() is False:
            return False
        else:
            return None

    # for performance reasons, do not call directly, rather use the to_dnf method as it stores the result
    def compute_dnf(self):
        return self

    def to_dnf(self):
        if not hasattr(self, "hold_todnf"):
            self.hold_todnf = self.compute_dnf()
        return self.hold_todnf

    # for performance reasons, do not call directly, rather use the to_dnf method as it stores the result
    def compute_cnf(self):
        return self

    def to_cnf(self):
        if not hasattr(self, "hold_tocnf"):
            self.hold_tocnf = self.compute_cnf()
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

    def canonicalize_once(self, nf=None):
        return self

    def canonicalize(self, nf=None):
        from utils import fixed_point

        if nf not in self.canonicalized_hash:
            def processor(td):
                return td.canonicalize_once(nf)

            def good_enough(a, b):
                return type(a) == type(b) and a == b
            
            res = fixed_point(self, processor, good_enough)
            self.canonicalized_hash |= {nf: res}
            # tell the perhaps new object it is already canonicalized
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
        assert type(self) == type(t), f"expecting same type {self} is {type(self)}, while {t} is {type(t)}"
        raise TypeError(f"cannot compare type designators of type {type(self)}")
