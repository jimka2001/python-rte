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


class Or (Combination):
    def __str__(self):
        return "Or(" + ", ".join([str(td) for td in self.operands]) + ")"

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
        createSOr(operands)

    def orInvert(self, x):
        return not x

    def canonicalize_once(self):
        from genus.utils import find_simplifier
        return find_simplifier(self, [lambda: self.conversion1(),
                                      lambda: self.conversion3(),
                                      lambda: self.conversion4(),
                                      lambda: self.conversion4(),
                                      lambda: self.conversion6(),
                                      lambda: self.conversionC7(),
                                      lambda: self.conversion8(),
                                      lambda: self.conversion9(),
                                      lambda: self.conversion10(),
                                      lambda: self.conversionC11(),
                                      lambda: self.conversion11b(),
                                      lambda: self.conversionC16(),
                                      lambda: self.conversionC16b(),
                                      lambda: self.conversion12(),
                                      lambda: self.conversion13(),
                                      lambda: self.conversion14(),
                                      lambda: self.conversion15(),
                                      lambda: self.conversion21(),
                                      lambda: self.conversionC15(),
                                      lambda: self.conversionC17(),
                                      lambda: self.conversion99(),
                                      lambda: self.conversion5(),
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
