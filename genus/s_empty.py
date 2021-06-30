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


"""
[0-3] Advancement tracker
__str__ 3
typep 3
inhabited 3
disjoint_down 3
subtypep 3
cmp_to_same_class_obj 3
"""
from genus import *


class SEmptyImpl(SimpleTypeD, TerminalType):
    """The empty type, subtype of all types."""
    __instance = None

    # overriding the __new__ method enables us to implement a singleton
    #   class.  I.e., a class, STopImpl, for which the call STopImpl()
    #   always return the exact same object.  STopImpl() is STopImpl().
    def __new__(cls, *a, **kw):
        if SEmptyImpl.__instance is None:
            SEmptyImpl.__instance = super(SEmptyImpl, cls).__new__(cls, *a, **kw)
        return SEmptyImpl.__instance

    def __str__(self):
        return "SEmpty"

    def typep(self, _any):
        return False

    def inhabited(self):
        return False

    def disjoint_down(self, t):
        assert isinstance(t, SimpleTypeD)
        return True

    def subtypep(self, t):
        return True

    def cmp_to_same_class_obj(self, t):
        if type(self) != type(t):
            return super().cmp_to_same_class_obj(t)
        else:
            return 0


SEmpty = SEmptyImpl()
