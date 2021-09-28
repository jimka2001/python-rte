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
from typing import Literal
from typing_extensions import TypeGuard

class SMemberImpl(SimpleTypeD):
    """docstring for SMemberImpl"""

    def __init__(self, *arglist):
        super(SMemberImpl, self).__init__()
        self.arglist = list(arglist)

    def __str__(self):
        return "SMember(" + ", ".join([str(x) for x in self.arglist]) + ")"

    def __eq__(self, that):
        return type(self) is type(that) and \
               self.arglist == that.arglist

    def __hash__(self):
        return hash(tuple(self.arglist))

    def typep(self, a):
        return a in self.arglist

    def inhabited_down(self):
        return [] != self.arglist

    def disjoint_down(self, t2):
        assert isinstance(t2, SimpleTypeD)
        return not any(t2.typep(a) for a in self.arglist)

    def subtypep_down(self, t2):
        return all(t2.typep(a) for a in self.arglist)

    def canonicalize_once(self, _nf=None):
        from genus.utils import uniquify
        return createSMember(sorted(uniquify(self.arglist), key=lambda s: (type(s).__name__, s)))

    def cmp_to_same_class_obj(self, t: 'SMemberImpl') -> Literal[-1, 0, 1]:
        if type(self) != type(t):
            return super().cmp_to_same_class_obj(t)
        else:
            a = self.arglist
            b = t.arglist

            def comp(i):
                if i >= len(a) and i >= len(b):
                    return 0
                elif i >= len(a):
                    return -1  # short list < long list
                elif i >= len(b):
                    return 1
                elif a[i] == b[i]:
                    return comp(i + 1)
                elif str(a[i]) < str(b[i]):
                    return -1
                elif str(a[i]) > str(b[i]):
                    return 1
                else:
                    raise Exception(f"{self} and {t} contain different values which print the same {a[i]} vs {b[i]}")

            return comp(0)


class SMember(SMemberImpl, TerminalType):
    pass


def createSMember(items):
    from genus.s_empty import SEmpty
    from genus.s_eql import SEql

    if not items:
        return SEmpty
    elif len(items) == 1:
        return SEql(items[0])
    else:
        return SMember(*items)


def memberimplp(this) -> TypeGuard[SMemberImpl]:
    return isinstance(this, SMemberImpl)


def memberp(this) -> TypeGuard[SMember]:
    return isinstance(this, SMember)
