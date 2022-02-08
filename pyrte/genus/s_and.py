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


from genus.s_combination import SCombination
from genus.s_or import SOr
from genus.s_empty import SEmpty, SEmptyImpl
from genus.s_top import STop, STopImpl
from genus.simple_type_d import SimpleTypeD
from genus.utils import find_first, generate_lazy_val, uniquify
from typing import List, TypeVar, Callable, Iterable, Optional, Any
from typing_extensions import TypeGuard


T = TypeVar('T')  # Declare type variable


# from utils import CallStack
# subtypep_and_callstack = CallStack("subtypep.SAnd")
# inhabited_down_and = CallStack("inhabited_down.SAnd")


class SAnd(SCombination):
    """An intersection type, which is the intersection of zero or more types.
    param tds list, zero or more type designators"""

    def __str__(self) -> str:
        return "SAnd(" + ", ".join([str(td) for td in self.tds]) + ")"

    def create(self, tds: List[SimpleTypeD]) -> SimpleTypeD:
        return createSAnd(tds)

    def unit(self) -> STopImpl:
        return STop

    def zero(self) -> SEmptyImpl:
        return SEmpty

    def annihilator(self, a, b) -> Optional[bool]:
        return a.subtypep(b)

    def dual_combination(self, td) -> TypeGuard[SOr]:
        from genus.s_or import orp
        return orp(td)

    def dual_combinator(self, a: List[T], b: List[T]) -> List[T]:
        return uniquify(a + b)

    def combinator(self, a: Iterable[T], b: Iterable[T]) -> List[T]:
        return [x for x in a if x in b]

    def combo_filter(self, pred: Callable[[T], bool], xs: Iterable[T]) -> List[T]:
        return [x for x in xs if pred(x)]  # cannot use filter from Python std library because of type incompatibility

    def create_dual(self, tds: List[SimpleTypeD]) -> SimpleTypeD:
        from genus.s_or import createSOr
        return createSOr(tds)

    def typep(self, a: Any) -> bool:
        return all(td.typep(a) for td in self.tds)

    def inhabited_down(self) -> Optional[bool]:
        from genus.genus_types import NormalForm
        from genus.s_atomic import atomicp
        from genus.s_not import notp
        from genus.s_member import memberimplp
        dnf = generate_lazy_val(lambda: self.canonicalize(NormalForm.DNF))
        cnf = generate_lazy_val(lambda: self.canonicalize(NormalForm.CNF))

        if any(t.inhabited() is False for t in self.tds):
            return False
        elif len(self.tds) > 1 and all(notp(td) and (atomicp(td.s) or memberimplp(td.s)) for td in self.tds):
            return True
        elif all(atomicp(t) for t in self.tds):
            #   here we would like to check every 2-element subset
            #   if we find a,b such that a and b are disjoint,
            #   then we know self is NOT inhabited
            s = any(self.tds[a].disjoint(self.tds[b]) is True
                    for a in range(len(self.tds))
                    for b in range(a + 1, len(self.tds)))
            return not s
        elif dnf() != self and dnf().inhabited() is not None:
            return dnf().inhabited()
        elif cnf() != self and cnf().inhabited() is not None:
            return cnf().inhabited()
        # in the special case of (and A B) if A and B are NOT disjoint,
        #   then the intersection is inhabited.  This does not generalize
        #   to (and A B C...), because even if not(A||B), not(B||C), and not(A||C),
        #   the intersection might still be empty.
        # E.g., (and (member 1 2) (member 2 3) (member 1 3)) is empty yet no pair is disjoint.
        elif 2 == len(self.tds) and self.tds[0].disjoint(self.tds[1]) is False:
            return True
        else:
            return super().inhabited_down()

    def disjoint_down(self, t: SimpleTypeD) -> Optional[bool]:
        assert isinstance(t, SimpleTypeD)

        if any(t.disjoint(t2) is True for t2 in self.tds):
            return True
        elif t.inhabited() is not True or self.inhabited() is not True:
            return super().disjoint_down(t)
        elif t in self.tds:
            return False
        # this code is commented out because it is simply wrong.
        # elif (any((td.subtypep(t) is True) or (t.subtypep(td) is True)
        #          for td in self.tds)):
        #    return False
        elif (all(td.subtypep(t) is True for td in self.tds) or
              all(t.subtypep(td) is True for td in self.tds)):
            return False
        else:
            return super().disjoint_down(t)

    def subtypep_down(self, t: SimpleTypeD) -> Optional[bool]:
        if not self.tds:
            return STop.subtypep(t)
        elif 1 == len(self.tds):
            return self.tds[0].subtypep(t)
        elif any(t2.subtypep(t) for t2 in self.tds):
            return True
        elif t.inhabited() is not True:
            return super().subtypep_down(t)
        elif self.inhabited() is not True:
            return super().subtypep_down(t)
        elif all(x.disjoint(t) is True for x in self.tds):
            return False
        else:
            return super().subtypep_down(t)

    def conversionD1(self) -> SimpleTypeD:
        # Note this isn't consumed in SCombination:conversion16,
        # conversion16 converts SAnd(SMember(42, 43, 44, "a", "b", "c"), SInt)
        # to SAnd(SMember(42, 43, 44), SInt)
        # while conversionD1() converts it to
        # SMember(42, 43, 44)

        # SAnd(SMember(42, 43, 44), A, B, C)
        # == > SMember(42, 44)
        from genus.s_member import memberimplp, createSMember

        member = find_first(memberimplp, self.tds, None)
        if member is None:
            return self
        else:
            return createSMember([x[1] for x in member.argpairs if self.typep(x[1])])

    def conversionD3(self) -> SimpleTypeD:
        # discover disjoint pair
        for i in range(len(self.tds)):
            for j in range(i + 1, len(self.tds)):
                if self.tds[i].disjoint(self.tds[j]) is True:
                    return SEmpty
        return self

    def compute_dnf(self) -> SimpleTypeD:
        # convert SAnd( x1, x2, SOr(y1,y2,y3), x3, x4)
        #    --> td = SOr(y1,y2,y3)
        # --> SOr(SAnd(x1,x2,  y1,  x3,x4),
        #          SAnd(x1,x2,  y2,  x3,x4),
        #          SAnd(x1,x2,  y3,  x3,x4),
        #     )
        return self.compute_nf()


def createSAnd(tds: Iterable[SimpleTypeD]) -> SimpleTypeD:
    if not tds:
        return STop
    elif len(list(tds)) == 1:
        return list(tds)[0]
    else:
        return SAnd(*tds)


def andp(this: Any) -> bool:
    return isinstance(this, SAnd)
