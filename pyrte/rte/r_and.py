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


class And (Combination):
    def __str__(self):
        return "And(" + ", ".join([str(td) for td in self.operands]) + ")"

    def nullable(self):
        return all(r.nullable() for r in self.operands)

    def zero(self):
        from rte.r_emptyset import EmptySet
        return EmptySet

    def one(self):
        from rte.r_constants import sigmaStar
        return sigmaStar

    def same_combination(self,r):
        return andp(r)

    def dual_combination(self,r):
        from rte.r_or import orp
        return orp(r)

    def set_operation(self, a, b):
        # intersection
        return [x for x in a if x in b]

    def set_dual_operation(self, a, b):
        # union
        return a + [x for x in b if x not in a]

    def annihilator(self, a, b):
        return a.subtypep(b)

    def createTypeD(self, operands):
        from genus.s_and import createSAnd
        createSAnd(operands)

    def orInvert(self, x):
        return x

    def canonicalize_once(self):
        from genus.utils import find_simplifier
        return find_simplifier(self, [lambda: self.conversion1(),
                                      lambda: self.conversion3(),
                                      lambda: self.conversion4(),
                                      lambda: self.conversion4(),
                                      lambda: self.conversion6(),
                                      lambda: self.conversion7(),
                                      lambda: self.conversionC7(),
                                      lambda: self.conversion8(),
                                      lambda: self.conversion9(),
                                      lambda: self.conversion10(),
                                      lambda: self.conversionC11(),
                                      lambda: self.conversion12(),
                                      lambda: self.conversionC12(),
                                      lambda: self.conversion13(),
                                      lambda: self.conversion21(),
                                      lambda: self.conversionC15(),
                                      lambda: self.conversionC16(),
                                      lambda: self.conversionC16b(),
                                      lambda: self.conversion17(),
                                      lambda: self.conversion17a(),
                                      lambda: self.conversion17b(),
                                      lambda: self.conversion17c(),
                                      lambda: self.conversion18(),
                                      lambda: self.conversion19(),
                                      lambda: self.conversionC17(),
                                      lambda: self.conversion99(),
                                      lambda: self.conversion5(),
                                      lambda: super(And, self).canonicalize_once()])


def createAnd(operands):
    from rte.r_star import Star
    from rte.r_sigma import Sigma

    if not operands:
        return Star(Sigma)
    elif len(operands) == 1:
        return operands[0]
    else:
        return And(*operands)


def andp(op):
    return isinstance(op, And)
