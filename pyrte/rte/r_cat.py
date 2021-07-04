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


class Cat (Rte):
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


def catp(op):
    return isinstance(op, Cat)


def createCat(operands):
    from rte.r_epsilon import Epsilon

    if not operands:
        return Epsilon
    elif len(operands) == 1:
        return operands[0]
    else:
        return Cat(*operands)
