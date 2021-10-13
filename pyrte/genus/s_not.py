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


from genus.simple_type_d import SimpleTypeD
from genus.genus_types import NormalForm
from typing import Optional, Literal, Any, cast, TypeGuard


class SNot(SimpleTypeD):
    """A negation of a type.
    param s the type we want to get the complement"""

    def __init__(self, s):
        super(SNot, self).__init__()
        assert isinstance(s, SimpleTypeD)
        self.s = s

    def __str__(self) -> str:
        return "SNot(" + str(self.s) + ")"

    def __eq__(self, that: Any) -> bool:
        return type(self) is type(that) and \
               self.s == that.s

    def __hash__(self):
        return hash(self.s)

    def typep(self, a: Any) -> bool:
        return not self.s.typep(a)

    def inhabited_down(self) -> Optional[bool]:
        from genus.s_top import topp
        from genus.s_empty import emptyp
        from genus.s_atomic import atomicp
        from genus.s_member import memberimplp
        from genus.s_atomic import SAtomic

        if topp(self.s):
            return False
        elif emptyp(self.s):
            return True
        elif self.s == SAtomic(object):
            return False
        elif atomicp(self.s):
            return True
        elif memberimplp(self.s):
            return True
        elif notp(self.s):
            return self.s.s.inhabited()
        else:
            return None

    def disjoint_down(self, t: SimpleTypeD) -> Optional[bool]:
        from genus.s_atomic import atomicp
        from genus.s_member import memberimplp
        assert isinstance(t, SimpleTypeD)
        # is SNot(s) disjoint with t
        # first we ask whether t is a subtype of s,
        #  t <: s = > not (s) // t
        if t.subtypep(self.s) is True:
            return True
        elif self.s == t:  # if self and t are complements, then they are disjoint
            return True
        elif self.s.disjoint(t) is True and t.inhabited() is True:
            return False
        elif notp(t) and atomicp(self.s) and atomicp(cast(SNot, t).s):
            return False
        # if t2 < t1, then t2 disjoint from (not t1)   (strict subset)
        # (disjoint? '(not (member a b c 1 2 3)) '(member 1 2 3) )
        elif t.subtypep(self.s) is True and self.s.subtypep(t) is False:
            return True
        # (disjoint? '(not (member 1 2 3)) '(member a b c 1 2 3) )
        elif self.s.subtypep(t) is True and t.subtypep(self.s) is False:
            return False
        # (disjoint? SNot(SMember(1,2,3)) SNot(SAtomic(str)))
        elif memberimplp(self.s) \
                and notp(t) \
                and atomicp(t.s):
            return False
        else:
            return super().disjoint_down(t)

    def subtypep_down(self, t: SimpleTypeD) -> Optional[bool]:
        from genus.utils import generate_lazy_val
        from genus.s_atomic import atomicp
        # SNot(a).subtypep(SNot(b)) iff b.subtypep(a)
        #    however b.subtypep(a) might return None
        os = generate_lazy_val(lambda: t.s.subtypep(self.s) if notp(t) else None)

        # SNot(SAtomic(Long)).subtype(SAtomic(Double)) ??

        def h():
            if not atomicp(t):
                return None
            elif not atomicp(self.s):
                return None
            elif self.s.disjoint(t):
                return False
            else:
                return None

        hosted = generate_lazy_val(h)

        if self.s.inhabited() is True and self.s.subtypep(t) is True and SNot(t).inhabited() is True:
            return False
        elif hosted() is not None:
            return hosted()
        elif os() is not None:
            return os()
        else:
            return super().subtypep_down(t)

    def canonicalize_once(self, nf: Optional[NormalForm] = None) -> SimpleTypeD:
        from genus.s_top import topp, STop
        from genus.s_empty import SEmpty, emptyp
        if notp(self.s):
            return self.s.s.canonicalize_once(nf)
        elif topp(self.s):
            return SEmpty
        elif emptyp(self.s):
            return STop
        else:
            return SNot(self.s.canonicalize_once(nf)).to_nf(nf)

    def compute_dnf(self) -> SimpleTypeD:
        from genus.s_combination import combop
        # SNot(SAnd(x1, x2, x3))
        # --> SOr(SNot(x1), SNot(x2), SNot(x3)
        #
        # SNot(SOr(x1, x2, x3))
        # --> SAnd(SNot(x1), SNot(x2), SNot(x3))
        if combop(self.s):
            return self.s.create_dual([SNot(td) for td in self.s.tds])
        else:
            return self

    def compute_cnf(self) -> SimpleTypeD:
        # we convert a not to DNF or CNF the same way, i.e., by pushing down the SNot
        #   and converting SAnd to SOr
        return self.compute_dnf()

    def cmp_to_same_class_obj(self, td: 'SNot') -> Literal[-1, 0, 1]:
        from genus.utils import cmp_objects
        if type(self) != type(td):
            return super().cmp_to_same_class_obj(td)
        elif self == td:
            return 0
        else:
            return cmp_objects(self.s, td.s)

    def replace_down(self, search: SimpleTypeD, replace: SimpleTypeD) -> SimpleTypeD:
        return SNot(self.s.replace(search, replace))

    def find_first_leaf_td(self) -> Optional[SimpleTypeD]:
        return self.s.find_first_leaf_td()


def notp(this: Any) -> TypeGuard[SNot]:
    return isinstance(this, SNot)
