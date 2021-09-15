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
"""
[0-3] Advancement tracker

__init__ 3
__str__ 3
create 3
unit 3
zero 3
annihilator 3
same_combination 3
typep 3
inhabited_down 3
disjoint_down 2
subtypep 0
canonicalize_once 3
compute_cnf 3
"""

from genus.s_combination import SCombination
from genus.s_empty import SEmpty
from genus.s_top import STop
from genus.utils import find_first
from genus.utils import uniquify
from genus.simple_type_d import SimpleTypeD
from typing import List, Literal, TypeVar, Callable

T = TypeVar('T')      # Declare type variable

class SOr(SCombination):
    """Union type designator.  The operands are themselves type designators.
    @param tds list, zero or more type designators"""

    def __str__(self):
        return "SOr(" + ", ".join([str(td) for td in self.tds]) + ")"

    def create(self, tds) -> SimpleTypeD:
        return createSOr(tds)

    def unit(self) -> SimpleTypeD:
        return SEmpty

    def zero(self) -> SimpleTypeD:
        return STop

    def annihilator(self, a: SimpleTypeD, b: SimpleTypeD) -> Literal[True, False, None]:
        return b.subtypep(a)

    def dual_combination(self, td: SimpleTypeD) -> bool:
        from genus.s_and import andp
        return andp(td)

    def dual_combinator(self, a: List[T], b: List[T]) -> List[T]:
        return [x for x in a if x in b]

    def combinator(self, a: List[T], b: List[T]) -> List[T]:
        assert isinstance(a, list), f"expecting list, got {type(a)} a={a}"
        assert isinstance(b, list), f"expecting list, got {type(b)} b={b}"
        return uniquify(a + b)

    def combo_filter(self, pred: Callable[[T], bool], xs: List[T]) -> List[T]:
        return filter(lambda x: not pred(x), xs)  # calling filter from Python std library

    def create_dual(self, tds:List[SimpleTypeD]) -> SimpleTypeD:
        from genus.s_and import createSAnd
        return createSAnd(tds)

    def typep(self, a) -> bool:
        return any(td.typep(a) for td in self.tds)

    def inhabited_down(self) -> Literal[True,False,None]:
        if any(td.inhabited() is True for td in self.tds):
            return True
        elif all(td.inhabited() is False for td in self.tds):
            return False
        else:
            return super().inhabited_down()

    def disjoint_down(self, t: SimpleTypeD) -> Literal[True,False,None]:
        if all(td.disjoint(t) is True for td in self.tds):
            return True
        elif any(td.disjoint(t) is False for td in self.tds):
            return False
        else:
            s = super().disjoint_down(t)  # variable s useful for debugging
            return s

    def subtypep_down(self, t: SimpleTypeD) -> Literal[True,False,None]:
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


def orp(this: SimpleTypeD) -> bool:
    return isinstance(this, SOr)
