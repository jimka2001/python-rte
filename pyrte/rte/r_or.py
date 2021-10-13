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


from rte.r_combination import Combination
from typing import List, Any, Optional, TypeGuard
from rte.r_rte import Rte
from genus.simple_type_d import SimpleTypeD

verbose = False


class Or(Combination):
    from rte.r_and import And

    def __str__(self):
        return "Or(" + ", ".join([str(td) for td in self.operands]) + ")"

    def create(self, operands: List[Rte]) -> Rte:
        return createOr(operands)

    def create_dual(self, operands: List[Rte]) -> Rte:
        from rte.r_and import createAnd
        if verbose:
            assert self
        return createAnd(operands)

    def nullable(self) -> bool:
        return any(r.nullable() for r in self.operands)

    def zero(self) -> Rte:
        from rte.r_constants import sigmaStar
        return sigmaStar

    def one(self) -> Rte:
        from rte.r_emptyset import EmptySet
        return EmptySet

    def same_combination(self, r: Combination) -> TypeGuard['Or']:
        return orp(r)

    def dual_combination(self, r: Combination) -> TypeGuard[And]:
        from rte.r_and import andp
        return andp(r)

    def set_dual_operation(self, a: List[Any], b: List[Any]) -> List[Any]:
        # intersection
        return [x for x in a if x in b]

    def set_operation(self, a: List[Any], b: List[Any]) -> List[Any]:
        # union
        return a + [x for x in b if x not in a]

    def annihilator(self, a, b) -> Optional[bool]:
        return a.supertypep(b)

    def createTypeD(self, operands) -> SimpleTypeD:
        from genus.s_or import createSOr
        return createSOr(operands)

    def orInvert(self, x: bool) -> bool:
        return not x

    def conversionO8(self) -> Rte:
        # (:or A :epsilon B (:cat X (:* X)) C)
        #   --> (:or A :epsilon B (:* X) C )
        # (:or :epsilon (:cat X (:* X)))
        #   --> (:or :epsilon (:* X))
        # (:or (:* Y) (:cat X (:* X)))
        #   --> (:or (:* Y) (:* X))
        # BUT NOT
        # (:or :epsilon (:cat X (:* X) ANYTHING))
        from rte.r_star import plusp, starp
        from rte.r_cat import catp
        if any(op.nullable() for op in self.operands) and any(plusp(op) for op in self.operands):
            def f(op):
                if not catp(op):
                    return op
                elif not plusp(op):
                    return op
                elif starp(op.operands[1]) and op.operands[0] == op.operands[1].operand:  # Cat(x,Star(x)) -> Star(x)
                    return op.operands[1]
                elif starp(op.operands[0]) and op.operands[1] == op.operands[0].operand:  # Cat(Star(x),x) -> Star(x)
                    return op.operands[0]
                else:
                    return op

            return self.create([f(op) for op in self.operands])
        else:
            return self

    def conversionO9(self) -> Rte:
        from rte.r_cat import catxyp
        # (:or A :epsilon B (:cat X Y Z (:* (:cat X Y Z))) C)
        #   --> (:or A :epsilon B (:* (:cat X Y Z)) C )
        # (:or :epsilon (:cat X Y Z (:* (:cat X Y Z))))
        #   --> (:or :epsilon (:* (:cat X Y Z)))
        if any(op.nullable() for op in self.operands) and any(catxyp(op) for op in self.operands):
            def f(r):
                if catxyp(r):
                    return r.operands[-1]
                else:
                    return r

            return self.create([f(r) for r in self.operands])
        else:
            return self

    def conversionO10(self) -> Rte:
        from rte.r_epsilon import Epsilon
        from genus.utils import remove_element
        # (: or A :epsilon B (: * X) C)
        # --> (: or A B (: * X) C)
        if Epsilon in self.operands and any(r is not Epsilon and r.nullable() for r in self.operands):
            return self.create(remove_element(self.operands, Epsilon))
        else:
            return self

    def conversionO11b(self) -> Rte:
        # if Sigma is in the operands, then filter out all singletons
        # Or(Singleton(A),Sigma,...) -> Or(Sigma,...)
        from rte.r_sigma import Sigma
        from rte.r_singleton import singletonp
        if Sigma in self.operands:
            return self.create([r for r in self.operands if not singletonp(r)])
        else:
            return self

    def conversionO15(self) -> Rte:
        # Or(Not(A),B*,C) = Or(Not(A),C) if A and B  disjoint,
        #   i.e. remove all B* where B is disjoint from A
        from rte.r_not import notp
        from rte.r_singleton import singletonp
        from rte.r_star import starp
        from genus.utils import generate_lazy_val
        tds = [r.operand.operand for r in self.operands if notp(r) and singletonp(r.operand)]
        stars = generate_lazy_val(lambda: [r for r in self.operands
                                           if starp(r)
                                           and singletonp(r.operand)
                                           and any(a.disjoint(r.operand.operand) is True
                                                   for a in tds)])
        if not tds:
            return self
        elif not stars():
            return self
        else:
            return self.create([r for r in self.operands if r not in stars()])

    def conversionD16b(self) -> Rte:
        # Or(A, x, Not(y)) --> And(A, Not(x)) if x, y disjoint
        from rte.r_singleton import singletonp
        from rte.r_not import notp
        from genus.utils import flat_map
        # collect all td for each Not(Singleton(td))
        nss = [r.operand.operand for r in self.operands if notp(r) and singletonp(r.operand)]

        def f(r):
            if singletonp(r) and any(r.operand.disjoint(d) is True for d in nss):
                return []
            else:
                return [r]

        return self.create(flat_map(f, self.operands))

    # the naming convention of the conversion functions is as follows:
    #   conversionC... -- a method on Combination
    #   conversionA... -- a method on And
    #   conversionO... -- a method on Or
    #   conversionD... -- a method declared in Combination but implemented in And and Or in a dual way
    #                          I.e. the And and Or methods of this name implement dual operations.

    def canonicalize_once(self) -> Rte:
        from genus.utils import find_simplifier
        return find_simplifier(self, [self.conversionC1,
                                      self.conversionC3,
                                      self.conversionC4,
                                      self.conversionC6,
                                      self.conversionC7,
                                      self.conversionO8,
                                      self.conversionO9,
                                      self.conversionO10,
                                      self.conversionC11,
                                      self.conversionC14,
                                      self.conversionO11b,
                                      self.conversionC16,
                                      self.conversionD16b,
                                      self.conversionC12,
                                      self.conversionO15,
                                      self.conversionC21,
                                      self.conversionC15,
                                      self.conversionC17,
                                      self.conversionC99,
                                      self.conversionC5,
                                      lambda: super(Or, self).canonicalize_once()])


def createOr(operands) -> Rte:
    from rte.r_emptyset import EmptySet

    if not operands:
        return EmptySet
    elif len(operands) == 1:
        return operands[0]
    else:
        return Or(*operands)


def orp(op: Rte) -> TypeGuard[Or]:
    return isinstance(op, Or)


def Xor(td1: Rte, td2: Rte) -> Rte:
    from rte.r_and import And
    from rte.r_not import Not
    return Or(And(td1, Not(td2)),
              And(Not(td1), td2))
