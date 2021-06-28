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

from simple_type_d import SimpleTypeD, TerminalType
from s_empty import SEmptyImpl

""" test-coverage as (method name, state[0-3] {0 not implemented, 1 implemented, 2 partially tested,  3 fully done})
__str__ 1
typep   1
inhabited_down 1
disjoint_down  1
subtypep    1
cmp_to_same_class_obj   1
"""


class STopImpl(SimpleTypeD, TerminalType):
    """The super type, super type of all types."""
    __instance = None

    # overriding the __new__ method enables us to implement a singleton
    #   class.  I.e., a class, STopImpl, for which the call STopImpl()
    #   always return the exact same object.  STopImpl() is STopImpl().
    def __new__(cls, *a, **kw):
        if STopImpl.__instance is None:
            STopImpl.__instance = super(STopImpl, cls).__new__(cls, *a, **kw)
        return STopImpl.__instance

    def __str__(self):
        return "STop"

    def typep(self, _any):
        return True

    def inhabited_down(self):
        return True

    def disjoint_down(self, t):
        assert isinstance(t, SimpleTypeD)
        return type(t) is SEmptyImpl

    def subtypep_down(self, t):
        from s_not import SNot
        inh = SNot(t).inhabited()
        if inh is None:
            return None
        elif inh is True:
            return False
        else:
            return True

    def cmp_to_same_class_obj(self, t):
        if type(self) != type(t):
            return super().cmp_to_same_class_obj(t)
        else:
            return False


STop = STopImpl()
