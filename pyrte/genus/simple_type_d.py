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
from typing import Literal, Optional

# from utils import CallStack
# subtypep_callstack = CallStack("subtypep",trace=True)
# canonicalize_callstack = CallStack("canonicalize")
# inhabited_callstack = CallStack("inhabited")

from genus.genus_types import NormalForm
from genus.utils import generate_lazy_val, fixed_point
from typing import NoReturn


# is it useful, though ? all classes are types by default in python
class TerminalType(metaclass=ABCMeta):
    """This class is just here to emulate the TerminalType trait in Scala"""
    pass


class SimpleTypeD:
    """SimpleTypeD is the super class of all the
    representations of type in Genus"""

    def __init__(self):
        self.subtypep_cache = {}
        self.disjoint_cache = {}
        self.canonicalized_hash = {}
        self.lazy_inhabited = generate_lazy_val(lambda: self.inhabited_down())
        self.nf_cache = {}

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def typep(self, a) -> Literal[True, False]:
        """Returns whether a given object belongs to this designated type.
        It is a set membership test.
            @param `a` the object we want to check the type
            @return a Boolean which is true if `a` is of this type"""

    def disjoint(self, td) -> Literal[True, False, None]:
        assert isinstance(td, SimpleTypeD)
        if td in self.disjoint_cache:
            return self.disjoint_cache[td]
        # these somewhat cryptic names were chosen to match the original Scala code
        d1 = generate_lazy_val(lambda: self.disjoint_down(td))
        d2 = generate_lazy_val(lambda: td.disjoint_down(self))
        c1 = generate_lazy_val(lambda: self.canonicalize())
        c2 = generate_lazy_val(lambda: td.canonicalize())
        dc12 = generate_lazy_val(lambda: c1().disjoint_down(c2()))
        dc21 = generate_lazy_val(lambda: c2().disjoint_down(c1()))

        if self == td and self.inhabited() is not None:
            self.disjoint_cache[td] = not self.inhabited()
        elif d1() is not None:
            self.disjoint_cache[td] = d1()
        elif d2() is not None:
            self.disjoint_cache[td] = d2()
        elif c1() == self and c2() == td:
            # no need to continue searching if canonicalization failed to produce simpler forms
            self.disjoint_cache[td] = None
        elif c1() == c2() and c1().inhabited() is not None:
            self.disjoint_cache[td] = not c1().inhabited()
        elif dc12() is not None:
            self.disjoint_cache[td] = dc12()
        elif dc21() is not None:
            self.disjoint_cache[td] = dc21()
        else:
            self.disjoint_cache[td] = None

        return self.disjoint_cache[td]

    # for performance reasons, do not call directly, rather use the inhabited method as it stores the result
    def inhabited_down(self) -> Literal[True, False, None]:
        return None

    def inhabited(self) -> Literal[True, False, None]:
        return self.lazy_inhabited()

    def disjoint_down(self, t) -> Literal[True, False, None]:
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
    def subtypep(self, t: 'SimpleTypeD') -> Optional[bool]:
        from genus.s_or import orp
        from genus.s_and import andp
        from genus.s_top import topp

        assert isinstance(t, SimpleTypeD)
        if t in self.subtypep_cache:
            return self.subtypep_cache[t]

        def or_result():
            return True if orp(t) and any(self.subtypep(a) is True for a in t.tds) \
                else None

        def and_result():
            return True if andp(t) and all(self.subtypep(a) is True for a in t.tds) \
                else None

        if type(self) == type(t) and self == t:
            self.subtypep_cache[t] = True
        elif topp(t.canonicalize()):
            self.subtypep_cache[t] = True
        elif or_result() is True:
            self.subtypep_cache[t] = True
        elif and_result() is True:
            self.subtypep_cache[t] = True
        else:
            self.subtypep_cache[t] = self.subtypep_down(t)

        return self.subtypep_cache[t]

    def subtypep_down(self, t: 'SimpleTypeD') -> Optional[bool]:
        from genus.s_not import notp
        # The s of t.s is a reference to SNot
        if notp(t) and self.disjoint(t.s) is True:
            return True
        elif self.inhabited() is False:
            return True
        elif self.inhabited() is True and t.inhabited() is False:
            return False
        else:
            return None

    # for performance reasons, do not call directly, rather use the to_dnf method as it stores the result
    def compute_dnf(self) -> 'SimpleTypeD':
        return self

    # for performance reasons, do not call directly, rather use the to_dnf method as it stores the result
    def compute_cnf(self) -> 'SimpleTypeD':
        return self

    def to_nf(self, nf: Optional[NormalForm]) -> 'SimpleTypeD':
        if nf in self.nf_cache:
            return self.nf_cache[nf]
        elif NormalForm.CNF is nf:
            self.nf_cache[nf] = self.compute_cnf()
            return self.nf_cache[nf]
        elif NormalForm.DNF is nf:
            self.nf_cache[nf] = self.compute_dnf()
            return self.nf_cache[nf]
        else:
            return self

    def canonicalize_once(self, nf: Optional[NormalForm] = None) -> 'SimpleTypeD':
        return self

    def canonicalize(self, nf: Optional[NormalForm] = None) -> 'SimpleTypeD':
        # td.canonicalize(NormalForm.DNF)
        # td.canonicalize(NormalForm.CNf)
        # td.canonicalize(None)
        if nf not in self.canonicalized_hash:
            def processor(td):
                assert isinstance(td, SimpleTypeD)
                return td.canonicalize_once(nf)

            def good_enough(a, b):
                assert isinstance(a, SimpleTypeD), f"expecting SimpleTypeD not {a}"
                assert isinstance(b, SimpleTypeD), f"expecting SimpleTypeD not {b}"
                return type(a) == type(b) and a == b

            res = fixed_point(self, processor, good_enough)
            self.canonicalized_hash |= {nf: res}
            # tell the perhaps new object it is already canonicalized
            self.canonicalized_hash[nf].canonicalized_hash[nf] = self.canonicalized_hash[nf]

        return self.canonicalized_hash[nf]

    def supertypep(self, t) -> Optional[bool]:
        """ Returns whether this type is a recognizable supertype of another given type.
          It is a superset test. This might be undecidable.
         
          @param t the type we want to check the inclusion in this type
          @return an optional Boolean which is true if this type is a supertype of t
        """
        return t.subtypep(self)

    def cmp_to_same_class_obj(self, t: 'SimpleTypeD') -> NoReturn:
        assert type(self) == type(t), f"expecting same type {self} is {type(self)}, while {t} is {type(t)}"
        raise TypeError(f"cannot compare type designators of type {type(self)}")

    def replace_down(self, _search, _replace) -> 'SimpleTypeD':
        return self

    def replace(self, td_search, td_replace) -> 'SimpleTypeD':
        if self == td_search:
            return td_replace
        else:
            return self.replace_down(td_search, td_replace)

    def find_first_leaf_td(self) -> Optional['SimpleTypeD']:
        return self

    def typeEquivalent(self, t):
        can1 = generate_lazy_val(lambda: self.canonicalize())
        can2 = generate_lazy_val(lambda: t.canonicalize())

        sp1 = self.subtypep(t)
        if sp1 is None or False:
            sp1 = can1().subtypep(t)
            if sp1 is None or False:
                sp1 = can1().subtypep(can2())

        sp2 = t.subtypep(self)
        if sp2 is None or False:
            sp2 = can2().subtypep(self)
            if sp2 is None or False:
                can2().subtypep(can1())

        if sp1 is False or sp2 is False:
            return False
        elif sp1 is True and sp2 is True:
            return True
        return None
