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


from rte.r_emptyset import EmptySet
from rte.r_epsilon import Epsilon
from rte.r_rte import Rte
from rte.r_sigma import Sigma
from typing_extensions import TypeGuard


class Star(Rte):
    __instances = {}

    def __new__(cls, operand, *a, **kw):
        if operand in Star.__instances:
            return Star.__instances[operand]
        elif operand in [EmptySet, Epsilon, Sigma]:
            s = super(Star, cls).__new__(cls, *a, **kw)
            Star.__instances[operand] = s
            return s
        else:
            return super(Star, cls).__new__(cls, *a, **kw)

    def __init__(self, operand):
        super(Star, self).__init__()
        assert isinstance(operand, Rte), \
            f"expecting Rte: got {operand} of type {type(operand)}"
        self.operand = operand

    def __str__(self):
        return "Star(" + str(self.operand) + ")"

    def __eq__(self, that):
        return type(self) is type(that) and \
               self.operand == that.operand

    def __hash__(self):
        return hash(self.operand)

    def cmp_to_same_class_obj(self, t):
        from genus.utils import cmp_objects
        return cmp_objects(self.operand, t.operand)

    def first_types(self):
        return self.operand.first_types()

    def nullable(self):
        return True

    def conversion1(self):
        from rte.r_epsilon import Epsilon
        if self.operand is Epsilon:
            return Epsilon
        elif self.operand is EmptySet:
            return Epsilon
        elif starp(self.operand):
            return self.operand
        else:
            return self

    def conversion2(self):
        from rte.r_cat import catp, Cat
        if not catp(self.operand):
            return self
        c: Cat = self.operand
        if len(c.operands) != 2 and len(c.operands) != 3:
            return self
        # Star(Cat(x,Star(x))) -> Star(x)
        elif len(c.operands) == 2 and Star(c.operands[0]) == c.operands[1]:
            return c.operands[1]
        # Star(Cat(Star(x),x)) -> Star(x)
        elif len(c.operands) == 2 and c.operands[0] == Star(c.operands[1]):
            return c.operands[0]
        # Star(Cat(Star(x),x,Star(x))) -> Star(x)
        elif len(c.operands) == 3 and c.operands[0] == c.operands[2] and c.operands[0] == Star(c.operands[1]):
            return c.operands[0]
        else:
            return self

    def conversion3(self):
        from rte.r_cat import catp, Cat
        if not catp(self.operand):
            return self
        c: Cat = self.operand
        # Star(Cat(X, Y, Z, Star(Cat(X, Y, Z))))
        #    -->    Star(Cat(X, Y, Z))
        right = c.operands[-1]
        left = c.operands[0:-1]
        if c.operands == left + [Star(Cat(*left))]:
            return right

        # Star(Cat(Star(Cat(X, Y, Z)), X, Y, Z))
        #    -->    Star(Cat(X, Y, Z))
        left = c.operands[0]
        right = c.operands[1:]
        if c.operands == [Star(Cat(*right))] + right:
            return left

        # Star(Cat(Star(Cat(X, Y, Z)), X, Y, Z, Star(Cat(X, Y, Z)))
        #    -->    Star(Cat(X, Y, Z))
        if len(c.operands) < 3:
            return self
        else:
            left = c.operands[0]
            middle = c.operands[1:-1]
            sc = [Star(Cat(*middle))]
            if c.operands == sc + middle + sc:
                return left
            else:
                return self

    def conversion99(self):
        return Star(self.operand.canonicalize_once())

    def canonicalize_once(self):
        from genus.utils import find_simplifier
        return find_simplifier(self, [lambda: self.conversion1(),
                                      lambda: self.conversion2(),
                                      lambda: self.conversion3(),
                                      lambda: self.conversion99()])

    def derivative_down(self, wrt, factors, disjoints):
        from rte.r_cat import Cat
        return Cat(self.operand.derivative(wrt, factors, disjoints), self)


def starp(rte) -> TypeGuard[Star]:
    return isinstance(rte, Star)


def Plus(r):
    from rte.r_cat import Cat
    assert isinstance(r, Rte)
    return Cat(r, Star(r))


def plusp(rte) -> TypeGuard['Cat']:
    from rte.r_cat import catp
    return catp(rte) \
           and 2 == len(rte.operands) \
           and ((starp(rte.operands[1]) and rte.operands[1].operand == rte.operands[0])
                or (starp(rte.operands[0]) and rte.operands[0].operand == rte.operands[1]))
