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

from pyrte.genus import *


def mdtd(tds):
    # This algorithm doesn't exactly compute the maximal disjoint type decomposition
    # of its input rather it computes the mdtd of tds unioned with STop, which is
    # what is actually needed at the client side.
    tds = [td for td in tds if td.inhabited() is not False]
    decomposition = [STop]
    for td in tds:
        n = SNot(td).canonicalize()

        def f(td1):
            a = generate_lazy_val(lambda: SAnd(td, td1).canonicalize())
            b = generate_lazy_val(lambda: SAnd(n, td1).canonicalize())
            if td.disjoint(td1) is True:
                return [td1]
            elif n.disjoint(td1) is True:
                return [td1]
            elif a().inhabited() is False:
                return [td1]
            elif b().inhabited() is False:
                return [td1]
            else:
                return [a(), b()]
        decomposition = flat_map(f, decomposition)
    return decomposition
