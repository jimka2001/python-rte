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

from genus.simple_type_d import SimpleTypeD
from typing import List, Tuple, Set


def mdtd(tds: Set[SimpleTypeD]) -> List[Tuple[SimpleTypeD, List[SimpleTypeD], List[SimpleTypeD]]]:
    from genus.s_not import SNot
    from genus.s_top import STop
    from genus.utils import flat_map, generate_lazy_val
    # This algorithm doesn't exactly compute the maximal disjoint type decomposition
    # of its input rather it computes the mdtd of tds unioned with STop, which is
    # what is actually needed at the client side.
    tds = [td for td in tds if td.inhabited() is not False]
    decomposition = [(STop, [], [])]
    for td in tds:
        n = SNot(td)
        nc = generate_lazy_val(lambda: n.canonicalize())

        def f(triple) -> List[Tuple[SimpleTypeD, List[SimpleTypeD], List[SimpleTypeD]]]:
            from genus.s_and import SAnd
            td1, factors, disjoints = triple
            a = generate_lazy_val(lambda: SAnd(td, td1).canonicalize())
            b = generate_lazy_val(lambda: SAnd(nc(), td1).canonicalize())
            # each time td is intersected with td1, either explicitly or implicitly
            #   td is added to factors in the accumulated value.
            # each time SNot(td) is intersected, td is added to disjoints.
            #   the disjoints and factors list makes it much easier for the
            #   Singleton derivative function to determine whether the
            #   type in question is a subtype or a disjoint type, simply
            #   by looking it up in the factors or disjoint list.
            if td.disjoint(td1) is True:
                return [(td1, factors, disjoints + [td])]
            elif nc().disjoint(td1) is True:
                return [(td1, factors + [td], disjoints)]
            elif a().inhabited() is False:
                return [(td1, factors, disjoints + [td])]
            elif b().inhabited() is False:
                return [(td1, factors + [td], disjoints)]
            else:
                return [(a(), factors + [td], disjoints),
                        (b(), factors, disjoints + [td])]

        decomposition = flat_map(f, decomposition)
    return decomposition
