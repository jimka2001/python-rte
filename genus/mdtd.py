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

from genus.utils import flat_map, generate_lazy_val
from genus.s_and import SAnd
from genus.s_not import SNot
from genus.s_empty import SEmpty


def mdtd(tds):
    assert tds, "mdtd does not support empty list as input"
    decomposition = [tds[0]]
    for td in tds[1:]:
        def f(td1):
            n = SNot(td).canonicalize()
            a = generate_lazy_val(lambda: SAnd(td, td1).canonicalize())
            b = generate_lazy_val(lambda: SAnd(n, td1).canonicalize())
            if td.disjoint(td1) is True:
                return [td1]
            elif n.disjoint(td1) is True:
                return [td1]
            elif a().inhabited is False:
                return [td1]
            elif b().inhabited is False:
                return [td1]
            else:
                return [a(), b()]
        decomposition = flat_map(f, decomposition)
    if decomposition:
        return decomposition
    else:
        return [SEmpty]
