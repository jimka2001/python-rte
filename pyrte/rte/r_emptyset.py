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
from typing import Set, Literal, Callable, Tuple, List, Optional


class EmptySetImpl (Rte):
    __instance = None
    from genus.simple_type_d import SimpleTypeD

    def __new__(cls, *a, **kw):
        if EmptySetImpl.__instance is None:
            EmptySetImpl.__instance = super(EmptySetImpl, cls).__new__(cls, *a, **kw)
        return EmptySetImpl.__instance

    def __str__(self):
        return "∅"

    def first_types(self) -> Set[SimpleTypeD]:
        return set()  # empty set

    def nullable(self) -> Literal[False]:
        return False

    def derivative_down(self, wrt, factors, disjoints) -> 'EmptySetImpl':
        return EmptySet

    def constructThompson(self, ini: Callable[[], int], out: Callable[[], int]) \
            -> Tuple[int, int, List[Tuple[int, Optional[SimpleTypeD], int]]]:
        return ini(), out(), []


EmptySet = EmptySetImpl()
