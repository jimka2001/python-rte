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


from rte.r_rte import Rte
from genus.simple_type_d import SimpleTypeD
from typing import Literal, Set, Optional, List
from typing_extensions import TypeGuard


class Singleton(Rte):
    def __init__(self, operand):
        super(Singleton, self).__init__()
        assert isinstance(operand, SimpleTypeD)
        self.operand = operand

    def __str__(self):
        return "Singleton(" + str(self.operand) + ")"

    def __eq__(self, that):
        return type(self) is type(that) and \
               self.operand == that.operand

    def __hash__(self):
        return hash(self.operand)

    def cmp_to_same_class_obj(self, t) -> Literal[-1, 0, 1]:
        from genus.utils import cmp_objects
        return cmp_objects(self.operand, t.operand)

    def first_types(self) -> Set[SimpleTypeD]:
        return {self.operand}

    def nullable(self) -> Literal[False]:
        return False

    def canonicalize_once(self) -> Rte:
        from genus.s_top import STop
        from genus.s_empty import SEmpty
        from genus.s_and import andp
        from genus.s_or import orp
        from genus.s_not import notp
        from rte.r_sigma import Sigma
        from rte.r_emptyset import EmptySet
        from rte.r_and import createAnd, And
        from rte.r_or import createOr
        from rte.r_not import Not
        td = self.operand.canonicalize()
        if td == STop:
            return Sigma
        elif td == SEmpty:
            return EmptySet
        elif andp(td):
            return createAnd([Singleton(td1) for td1 in td.tds])
        elif orp(td):
            return createOr([Singleton(td1) for td1 in td.tds])
        elif notp(td):
            return And(Not(Singleton(td.s)), Sigma)
        else:
            return Singleton(td)

    def derivative(self,
                   wrt: Optional[SimpleTypeD],
                   factors: List[SimpleTypeD],
                   disjoints: List[SimpleTypeD]) -> Rte:
        from genus.s_empty import SEmpty
        from genus.s_top import STop
        from rte.r_emptyset import EmptySet
        from rte.r_sigma import Sigma
        td = self.operand
        if td is SEmpty:
            return EmptySet.derivative(wrt, factors, disjoints)
        elif td is STop:
            return Sigma.derivative(wrt, factors, disjoints)
        elif wrt is None:
            return self
        elif td.inhabited() is False:
            return EmptySet.derivative(wrt, factors, disjoints)
        # elif td.inhabited() is None:
        #    raise Exception(f"cannot compute derivative of {td} because its habitation is unknown")
        else:
            return super().derivative(wrt, factors, disjoints)

    def derivative_down(self,
                        wrt: Optional[SimpleTypeD],
                        factors: List[SimpleTypeD],
                        disjoints: List[SimpleTypeD]) -> Rte:
        from rte.r_epsilon import Epsilon
        from rte.r_emptyset import EmptySet
        from genus.s_top import STop
        from genus.s_and import SAnd
        from genus.s_not import SNot
        from rte.r_rte import CannotComputeDerivative
        td = self.operand  # SimpleTypeD
        if wrt == td and td.inhabited() is True:
            return Epsilon
        elif wrt == STop and td.inhabited() is True:
            return Epsilon
        elif td in factors:
            return Epsilon
        elif td in disjoints:
            return EmptySet
        elif isinstance(wrt, SimpleTypeD) and wrt.disjoint(td) is True:
            return EmptySet
        elif isinstance(wrt, SimpleTypeD) and wrt.subtypep(td) is True:
            return Epsilon
        elif isinstance(wrt, SAnd) and SNot(td) in wrt.tds:
            return EmptySet
        elif isinstance(wrt, SAnd) and td in wrt.tds and wrt.inhabited() is True:
            return Epsilon
        else:
            raise CannotComputeDerivative(
                msg="\n".join([f"Singleton.derivative_down cannot compute derivative of {self}",
                               f"  wrt={wrt}",
                               f"  disjoint={wrt.disjoint(td)}",
                               f"  subtypep={wrt.subtypep(td)}",
                               f"  factors={factors}",
                               f"  disjoints={disjoints}"]),
                rte=self,
                wrt=wrt,
                factors=factors,
                disjoints=disjoints)


def singletonp(op: Rte) -> TypeGuard[Singleton]:
    return isinstance(op, Singleton)
