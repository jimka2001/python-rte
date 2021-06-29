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


class SigmaImpl (Rte):
    __instance = None

    # overriding the __new__ method enables us to implement a singleton
    #   class.  I.e., a class, STopImpl, for which the call STopImpl()
    #   always return the exact same object.  STopImpl() is STopImpl().
    def __new__(cls, *a, **kw):
        if SigmaImpl.__instance is None:
            SigmaImpl.__instance = super(SigmaImpl, cls).__new__(cls, *a, **kw)
        return SigmaImpl.__instance

    def __str__(self):
        return "Sigma"

Sigma = SigmaImpl()
