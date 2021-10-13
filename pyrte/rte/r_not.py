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
from typing import Literal, Set
from typing_extensions import TypeGuard


class Not(Rte):
    from genus.simple_type_d import SimpleTypeD

    def __init__(self, operand):
        super(Not, self).__init__()
        assert isinstance(operand, Rte), \
            f"expecting object of type Rte got {type(operand)}: {operand}"
        self.operand = operand

    def __str__(self):
        return "Not(" + str(self.operand) + ")"

    def __eq__(self, that):
        return type(self) is type(that) and \
               self.operand == that.operand

    def __hash__(self):
        return hash(self.operand)

    def cmp_to_same_class_obj(self, t) -> Literal[-1, 0, 1]:
        from genus.utils import cmp_objects
        return cmp_objects(self.operand, t.operand)

    def first_types(self) -> Set[SimpleTypeD]:
        return self.operand.first_types()

    def nullable(self) -> bool:
        return not self.operand.nullable()

    def conversion1(self) -> Rte:
        from rte.r_sigma import Sigma
        from rte.r_emptyset import EmptySet
        from rte.r_epsilon import Epsilon
        from rte.r_constants import notSigma, singletonSTop, sigmaStar, notEpsilon, singletonSEmpty
        if self.operand == Sigma:
            return notSigma
        elif self.operand == singletonSTop:
            return notSigma
        elif self.operand == sigmaStar:
            return EmptySet
        elif self.operand == Epsilon:
            return notEpsilon
        elif self.operand == EmptySet:
            return sigmaStar
        elif self.operand == singletonSEmpty:
            return sigmaStar
        else:
            return self

    def conversion2(self) -> Rte:
        if notp(self.operand):
            # Not(Not(op)) --> op
            return self.operand.operand
        else:
            return self

    def conversion3(self) -> Rte:
        from rte.r_and import andp, createAnd
        from rte.r_or import createOr, orp
        if andp(self.operand):
            # Not(And(a, b)) -> Or(Not(a), Not(b))
            return createOr([Not(x) for x in self.operand.operands])
        elif orp(self.operand):
            # Not(And(a, b)) -> Or(Not(a), Not(b))
            return createAnd([Not(x) for x in self.operand.operands])
        else:
            return self

    def conversion99(self) -> Rte:
        return Not(self.operand.canonicalize_once())

    def canonicalize_once(self) -> Rte:
        from genus.utils import find_simplifier
        return find_simplifier(self, [self.conversion1,
                                      self.conversion2,
                                      self.conversion3,
                                      self.conversion99])

    def derivative_down(self, wrt, factors, disjoints) -> 'Not':
        return Not(self.operand.derivative(wrt, factors, disjoints))


def notp(op: Rte) -> TypeGuard[Not]:
    return isinstance(op, Not)


def createNot(operand: Rte) -> Rte:
    if notp(operand):
        return operand.operand
    else:
        return Not(operand)
