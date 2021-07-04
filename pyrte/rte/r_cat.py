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


class Cat(Rte):
    def __init__(self, *operands):
        self.operands = list(operands)
        assert all(isinstance(operand, Rte) for operand in operands)
        super().__init__()

    def __str__(self):
        return "Cat(" + ", ".join([str(td) for td in self.operands]) + ")"

    def __eq__(self, that):
        return type(self) is type(that) and \
               self.operands == that.operands

    def __hash__(self):
        return hash(tuple(self.operands))

    def create(self, operands):
        return createCat(operands)

    def first_types(self):
        from rte.r_epsilon import Epsilon
        if not self.operands:
            return Epsilon.first_types()
        elif 1 == len(self.operands):
            return self.operands[0].first_types()
        elif self.operands[0].nullable():
            return self.operands[0].first_types().union(createCat(self.operands[1:]))
        else:
            return self.operands[0].first_types()

    def nullable(self):
        return all(r.nullable() for r in self.operands)

    def conversion3(self):
        from rte.r_emptyset import EmptySet
        if EmptySet in self.operands:
            return EmptySet
        else:
            return self

    def conversion4(self):
        # remove  EmptyWord and flatten  Cat(Cat(...)...)
        from genus.utils import flat_map
        from rte.r_epsilon import Epsilon

        def f(rt):
            if rt is Epsilon:
                return []
            elif catp(rt):
                return rt.operands
            else:
                return [rt]
        return self.create(flat_map(f, self.operands))

    def conversion5(self):
        # Cat(..., x*, x, x* ...) --> Cat(..., x*, x, ...)
        from rte.r_star import starp
        for i in range(len(self.operands) - 2):
            if starp(self.operands[i]) \
                    and self.operands[i] == self.operands[i+2] \
                    and self.operands[i].operand == self.operands[i+1]:
                return self.create(self.operands[0:i+2] + self.operands[i+3:] if i-2 < len(self.operands) else [])
        # and Cat(..., x*, x* ...) --> Cat(..., x*, ...)
        for i in range(len(self.operands) - 1):
            if self.operands[i] == self.operands[i+1] and starp(self.operands[i]):
                return self.create(self.operands[0:i] + self.operands[i+1:])
        return self

    def conversion6(self):
        from rte.r_star import starp
        # Cat(A, B, X *, X, C, D) --> Cat(A, B, X, X *, C, D)

        def recur(rts, acc):
            if not rts:
                return acc
            elif starp(rts[0]) and len(rts) >= 2 and rts[0].operand == rts[1]:
                return recur([rts[1], rts[0]] + rts[2:], acc)
            else:
                return recur(rts[1:], acc + [rts[0]])

        return self.create(recur(self.operands, []))

    def conversion1(self):
        return self.create(self.operands)

    def conversion99(self):
        return self.create([rt.canonicalize_once() for rt in self.operands])

    def canonicalize_once(self):
        from genus.utils import find_simplifier
        return find_simplifier(self, [lambda: self.conversion1(),
                                      lambda: self.conversion3(),
                                      lambda: self.conversion4(),
                                      lambda: self.conversion5(),
                                      lambda: self.conversion6(),
                                      lambda: self.conversion99(),
                                      lambda: super(Cat, self).canonicalize_once()])


def catp(op):
    return isinstance(op, Cat)


def createCat(operands):
    from rte.r_epsilon import Epsilon
    assert all(isinstance(op, Rte) for op in operands)

    if not operands:
        return Epsilon
    elif len(operands) == 1:
        return operands[0]
    else:
        return Cat(*operands)
