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
inhabited_down 0
disjoint_down 1
subtypep 1
canonicalize_once 3
compute_dnf 3
"""

from genus.genus_types import NormalForm, createSAnd
from genus.genus_types import atomicp
from genus.genus_types import createSOr
from genus.genus_types import memberimplp, createSMember
from genus.genus_types import orp
from genus.s_combination import SCombination
from genus.s_empty import SEmpty
from genus.s_top import STop
from genus.simple_type_d import SimpleTypeD
from genus.utils import find_first
from genus.utils import generate_lazy_val
from genus.utils import uniquify


# from utils import CallStack
# subtypep_and_callstack = CallStack("subtypep.SAnd")
# inhabited_down_and = CallStack("inhabited_down.SAnd")


class SAnd(SCombination):
    """An intersection type, which is the intersection of zero or more types.
    @param tds list, zero or more type designators"""

    def __str__(self):
        return "SAnd(" + ", ".join([str(td) for td in self.tds]) + ")"

    def create(self, tds):
        return createSAnd(tds)

    def unit(self):
        return STop

    def zero(self):
        return SEmpty

    def annihilator(self, a, b):
        return a.subtypep(b)

    def dual_combination(self, td):
        return orp(td)

    def dual_combinator(self, a, b):
        return uniquify(a + b)

    def combinator(self, a, b):
        return [x for x in a if x in b]

    def combo_filter(self, pred, xs):
        return filter(pred, xs)  # calling filter from Python std library

    def create_dual(self, tds):
        return createSOr(tds)

    def typep(self, a):
        return all(td.typep(a) for td in self.tds)

    def inhabited_down(self):
        dnf = generate_lazy_val(lambda: self.canonicalize(NormalForm.DNF))
        cnf = generate_lazy_val(lambda: self.canonicalize(NormalForm.CNF))

        inhabited_dnf = generate_lazy_val(lambda: dnf().inhabited())
        inhabited_cnf = generate_lazy_val(lambda: cnf().inhabited())

        if any(t.inhabited() is False for t in self.tds):
            return False
        elif all(atomicp(t) for t in self.tds):
            #   here we would like to check every 2-element subset
            #   if we find a,b such that a and b are disjoint,
            #   then we know self is NOT inhabited
            s = any(self.tds[a].disjoint(self.tds[b]) is True
                    for a in range(len(self.tds))
                    for b in range(a+1, len(self.tds)))
            return not s
        elif dnf() != self and inhabited_dnf() is not None:
            return inhabited_dnf()
        elif cnf() != self and inhabited_cnf() is not None:
            return inhabited_cnf()
        else:
            return super().inhabited_down()

    def disjoint_down(self, t):
        assert isinstance(t, SimpleTypeD)
        inhabited_t = generate_lazy_val(lambda: t.inhabited())
        inhabited_self = generate_lazy_val(lambda: self.inhabited())

        if any(t.disjoint(t2) is True for t2 in self.tds):
            return True
        elif t in self.tds and inhabited_t() is True and inhabited_self() is True:
            return False
        elif inhabited_t() \
                and inhabited_self() \
                and any(x.subtypep(t) is True
                        or t.subtypep(x) is True
                        for x in self.tds):
            return False
        else:
            return super().disjoint_down(t)

    def subtypep_down(self, t):
        if not self.tds:
            return STop.subtypep(t)
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

    def conversionD1(self):
        # Note this isn't this consumed in SCombination:conversion16,
        # conversion16 converts SAnd(SMember(42, 43, 44, "a", "b", "c"), SInt)
        # to SAnd(SMember(42, 43, 44), SInt)
        # while conversionA1() converts it to
        # SMember(42, 43, 44)

        # SAnd(SMember(42, 43, 44), A, B, C)
        # == > SMember(42, 44)
        member = find_first(memberimplp, self.tds, None)
        if member is None:
            return self
        else:
            return createSMember([x for x in member.arglist if self.typep(x)])

    def conversionD3(self):
        # discover disjoint pair
        for i in range(len(self.tds)):
            for j in range(i+1, len(self.tds)):
                if self.tds[i].disjoint(self.tds[j]) is True:
                    return SEmpty
        return self

    def compute_dnf(self):
        # convert SAnd( x1, x2, SOr(y1,y2,y3), x3, x4)
        #    --> td = SOr(y1,y2,y3)
        # --> SOr(SAnd(x1,x2,  y1,  x3,x4),
        #          SAnd(x1,x2,  y2,  x3,x4),
        #          SAnd(x1,x2,  y3,  x3,x4),
        #     )
        return self.compute_nf()