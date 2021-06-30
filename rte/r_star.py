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
from rte.r_sigma import Sigma
from rte.r_epsilon import Epsilon
from rte.r_emptyset import EmptySet


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
        assert isinstance(operand, Rte)
        self.operand = operand

    def __str__(self):
        return "Star(" + str(self.operand) + ")"

    def __eq__(self, that):
        return type(self) is type(that) and \
               self.operand == that.operand

    def __hash__(self):
        return hash(self.operand)