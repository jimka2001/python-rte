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

from genus.simple_type_d import SimpleTypeD, TerminalType
from typing import Literal, Any


class SSatisfies(SimpleTypeD, TerminalType):
    """The super type, super type of all types."""

    def __init__(self, f, printable):
        assert callable(f)
        self.f = f
        self.printable = printable
        super().__init__()

    def __eq__(self, that: Any) -> bool:
        return type(self) is type(that) \
               and self.f == that.f \
               and self.printable == that.printable

    def __hash__(self):
        return hash((self.f, self.printable))

    def typep(self, a: Any) -> bool:
        return self.f(a)

    def __str__(self) -> str:
        return str(self.printable) + "?"

    def cmp_to_same_class_obj(self, t: 'SSatisfies') -> Literal[-1, 0, 1]:
        if type(self) != type(t):
            return super().cmp_to_same_class_obj(t)
        elif str(self) < str(t):
            return -1
        else:
            return 1
