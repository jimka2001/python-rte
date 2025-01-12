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
from typing import Literal, Set, Tuple, Callable, List, Optional


class EpsilonImpl (Rte):
    from rte.r_emptyset import EmptySetImpl
    from genus.simple_type_d import SimpleTypeD

    __instance = None

    def __new__(cls, *a, **kw):
        if EpsilonImpl.__instance is None:
            EpsilonImpl.__instance = super(EpsilonImpl, cls).__new__(cls, *a, **kw)
        return EpsilonImpl.__instance

    def __str__(self):
        return "ε"

    def first_types(self) -> Set[SimpleTypeD]:
        return set()  # empty set

    def nullable(self) -> Literal[True]:
        return True

    def derivative_down(self, wrt, factors, disjoints) -> EmptySetImpl:
        from rte.r_emptyset import EmptySet
        return EmptySet

    def constructThompson(self,ini:Callable[[],int],out:Callable[[],int]) \
            -> Tuple[int,int,List[Tuple[int,Optional[SimpleTypeD],int]]]:
        return ini(), out(), [(ini(), None, out())]

Epsilon = EpsilonImpl()
