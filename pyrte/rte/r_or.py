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


class Or(Combination):
    def __str__(self):
        return "Or(" + ", ".join([str(td) for td in self.operands]) + ")"

    def create(self, operands):
        return createOr(operands)

    def create_dual(self, operands):
        from rte.r_and import createAnd
        return createAnd(operands)

    def nullable(self):
        return any(r.nullable() for r in self.operands)

    def zero(self):
        from rte.r_constants import sigmaStar
        return sigmaStar

    def one(self):
        from rte.r_emptyset import EmptySet
        return EmptySet

    def same_combination(self, r):
        return orp(r)

    def dual_combination(self, r):
        from rte.r_and import andp
        return andp(r)

    def set_dual_operation(self, a, b):
        # intersection
        return [x for x in a if x in b]

    def set_operation(self, a, b):
        # union
        return a + [x for x in b if x not in a]

    def annihilator(self, a, b):
        return a.supertypep(b)

    def createTypeD(self, operands):
        from genus.s_or import createSOr
        return createSOr(operands)

    def orInvert(self, x):
        return not x

    def conversionO8(self):
        # (:or A :epsilon B (:cat X (:* X)) C)
        #   --> (:or A :epsilon B (:* X) C )
        # (:or :epsilon (:cat X (:* X)))
        #   --> (:or :epsilon (:* X))
        # (:or (:* Y) (:cat X (:* X)))
        #   --> (:or (:* Y) (:* X))
        from rte.r_star import plusp, starp
        from rte.r_cat import catp
        if any(op.nullable() for op in self.operands) and any(plusp(op) for op in self.operands):
            def f(op):
                if not catp(op):
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

    def conversionO9(self):
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

    def conversionO10(self):
        from rte.r_epsilon import Epsilon
        from genus.utils import remove_element
        # (: or A :epsilon B (: * X) C)
        # --> (: or A B (: * X) C)
        if Epsilon in self.operands and any(r is not Epsilon and r.nullable() for r in self.operands):
            return self.create(remove_element(self.operands, Epsilon))
        else:
            return self

    def conversionO11b(self):
        # if Sigma is in the operands, then filter out all singletons
        # Or(Singleton(A),Sigma,...) -> Or(Sigma,...)
        from rte.r_sigma import Sigma
        from rte.r_singleton import singletonp
        if Sigma in self.operands:
            return self.create([r for r in self.operands if not singletonp(r)])
        else:
            return self

    def conversionO15(self):
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

    def conversionD16b(self):
        # Or(A, x, Not(y)) --> And(A, Not(x)) if x, y disjoint
        from rte.r_singleton import singletonp
        from rte.r_not import notp
        from genus.utils import flat_map
        # collect all td for each Not(Singleton(td))
        nss = [r.operand.operand for r in self.operands if notp(r) and singletonp(r.operand)]

        def f(r):
            if singletonp(r) and any(r.operand.disjoint(d) for d in nss):
                return []
            else:
                return [r]

        return self.create(flat_map(f, self.operands))

    def canonicalize_once(self):
        from genus.utils import find_simplifier
        return find_simplifier(self, [lambda: self.conversionC1(),
                                      lambda: self.conversionC3(),
                                      lambda: self.conversionC4(),
                                      lambda: self.conversionC6(),
                                      lambda: self.conversionC7(),
                                      lambda: self.conversionO8(),
                                      lambda: self.conversionO9(),
                                      lambda: self.conversionO10(),
                                      lambda: self.conversionC11(),
                                      lambda: self.conversionC14(),
                                      lambda: self.conversionO11b(),
                                      lambda: self.conversionC16(),
                                      lambda: self.conversionD16b(),
                                      lambda: self.conversionC12(),
                                      lambda: self.conversionO15(),
                                      lambda: self.conversionC21(),
                                      lambda: self.conversionC15(),
                                      lambda: self.conversionC17(),
                                      lambda: self.conversionC99(),
                                      lambda: self.conversionC5(),
                                      lambda: super(Or, self).canonicalize_once()])


def createOr(operands):
    from rte.r_emptyset import EmptySet

    if not operands:
        return EmptySet
    elif len(operands) == 1:
        return operands[0]
    else:
        return Or(*operands)


def orp(op):
    return isinstance(op, Or)
