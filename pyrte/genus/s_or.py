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
from genus.s_and import SAnd
from genus.s_empty import SEmpty
from genus.s_top import STop
from genus.utils import find_first
from genus.utils import uniquify
from genus.simple_type_d import SimpleTypeD
from typing import List, TypeVar, Callable, Optional, Iterable, Collection
from typing_extensions import TypeGuard

T = TypeVar('T')      # Declare type variable


class SOr(SCombination):
    """Union type designator.  The operands are themselves type designators.
    param tds list, zero or more type designators"""

    def __str__(self):
        return "SOr(" + ", ".join([str(td) for td in self.tds]) + ")"

    def create(self, tds) -> SimpleTypeD:
        return createSOr(tds)

    def unit(self) -> SimpleTypeD:
        return SEmpty

    def zero(self) -> SimpleTypeD:
        return STop

    def annihilator(self, a: SimpleTypeD, b: SimpleTypeD) -> Optional[bool]:
        return b.subtypep(a)

    def dual_combination(self, td: SimpleTypeD) -> TypeGuard[SAnd]:
        from genus.s_and import andp
        return andp(td)

    def dual_combinator(self, a: Iterable[T], b: Collection[T]) -> List[T]:
        return [x for x in a if x in b]

    def combinator(self, a: Iterable[T], b: Iterable[T]) -> List[T]:
        assert isinstance(a, list), f"expecting list, got {type(a)} a={a}"
        assert isinstance(b, list), f"expecting list, got {type(b)} b={b}"
        return uniquify(a + b)

    def combo_filter(self, pred: Callable[[T], bool], xs: Iterable[T]) -> List[T]:
        return [x for x in xs if not pred(x)]

    def create_dual(self, tds: Iterable[SimpleTypeD]) -> SimpleTypeD:
        from genus.s_and import createSAnd
        return createSAnd(tds)

    def typep(self, a) -> bool:
        return any(td.typep(a) for td in self.tds)

    def inhabited_down(self) -> Optional[bool]:
        if any(td.inhabited() is True for td in self.tds):
            return True
        elif all(td.inhabited() is False for td in self.tds):
            return False
        else:
            return super().inhabited_down()

    def disjoint_down(self, t: SimpleTypeD) -> Optional[bool]:
        if all(td.disjoint(t) is True for td in self.tds):
            return True
        elif any(td.disjoint(t) is False for td in self.tds):
            return False
        else:
            s = super().disjoint_down(t)  # variable s useful for debugging
            return s

    def subtypep_down(self, t: SimpleTypeD) -> Optional[bool]:
        if not self.tds:
            return STop.subtypep(t)
        elif 1 == len(self.tds):
            return self.tds[0].subtypep(t)
        elif all(td.subtypep(t) is True for td in self.tds):
            return True
        elif any(td.subtypep(t) is False for td in self.tds):
            return False
        else:
            return super().subtypep_down(t)

    def conversionD1(self) -> SimpleTypeD:
        from genus.s_not import SNot, notp
        from genus.s_member import memberimplp, createSMember
        # Dual of SAnd.conversionA1

        # SOr(SNot(SMember(42, 43, 44, "a","b")), String)
        # == > SNot(SMember(42, 43, 44))
        # find all x in {42, 43, 44, "a","b"} which are not self.typep(x)
        not_member = find_first(lambda td: notp(td) and memberimplp(td.s), self.tds, None)
        if not_member is None:
            return self
        else:
            return SNot(createSMember([x for x in not_member.s.arglist if not self.typep(x)]))

    def conversionD3(self) -> SimpleTypeD:
        from genus.s_not import notp
        # dual of  disjoint pair
        # SOr(SNot(A), SNot(B)) -> STop if A and B are disjoint

        nots = [td.s for td in self.tds if notp(td)]

        for i in range(len(nots)):
            for j in range(i + 1, len(nots)):
                if nots[i].disjoint(nots[j]) is True:
                    return STop
        return self

    def compute_cnf(self) -> SimpleTypeD:
        # convert SOr( x1, x2, SAnd(y1,y2,y3), x3, x4)
        #    --> td = SAnd(y1,y2,y3)
        # --> SAnd(SOr(x1,x2,  y1,  x3,x4),
        #          SOr(x1,x2,  y2,  x3,x4),
        #          SOr(x1,x2,  y3,  x3,x4),
        #     )
        return self.compute_nf()


def createSOr(tds: List[SimpleTypeD]) -> SimpleTypeD:
    if not tds:
        return SEmpty
    elif len(tds) == 1:
        return tds[0]
    else:
        return SOr(*tds)


def orp(this: SimpleTypeD) -> TypeGuard[SOr]:
    return isinstance(this, SOr)
