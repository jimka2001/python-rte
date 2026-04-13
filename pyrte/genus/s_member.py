# Copyright (©) 2021,22 EPITA Research and Development Laboratory
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
from genus.s_empty import SEmptyImpl
from typing import Literal, Union, TypeGuard


class SMemberImpl(SimpleTypeD):
    """docstring for SMemberImpl"""

    def __init__(self, *arglist):
        from genus.s_atomic import SAtomic
        super(SMemberImpl, self).__init__()
        self.argpairs = [(SAtomic(type(x)), x) if type(x) != tuple else (SAtomic(type(x[1])), x[1]) for x in arglist]

    def __str__(self):
        return "SMember(" + ", ".join([str(x) for x in self.argpairs]) + ")"

    def __eq__(self, that):
        return type(self) is type(that) and \
               self.argpairs == that.argpairs

    def __hash__(self):
        return hash(tuple(self.argpairs))

    def typep(self, a):
        from genus.s_atomic import SAtomic
        return (SAtomic(type(a)), a) in self.argpairs

    def inhabited_down(self):
        return [] != self.argpairs

    def disjoint_down(self, t2):
        assert isinstance(t2, SimpleTypeD)
        return not any(t2.typep(a) for (t, a) in self.argpairs)

    def subtypep_down(self, t2):
        return all(t2.typep(a) for (t, a) in self.argpairs)

    def canonicalize_once(self, _nf=None):
        from genus.utils import uniquify
        # Sort by type then by value so the equality of to list can show by index
        # In this implementation we have chosen this order.
        return createSMember([a for _, a in sorted(uniquify(self.argpairs), key=lambda s: (type(s[1]).__name__, s[1]))])

    def cmp_to_same_class_obj(self, t: 'SMemberImpl') -> Literal[-1, 0, 1]:
        if type(self) != type(t):
            return super().cmp_to_same_class_obj(t)
        else:
            a = self.argpairs
            b = t.argpairs

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


def createSMember(items) -> Union[SEmptyImpl, SMemberImpl]:
    from genus.s_empty import SEmpty
    from genus.s_eql import SEql
    # items is a list of object like : {1, 2, 3}
    #     not a pairs like : ((SAtomic(int), 1), (SAtomic(int), 2), (SAtomic(int), 3))
    assert type(items) is list
    # TODO, the following check is not really correct.
    #   it is attempting to trigger an error if someone called
    #   createSMember with arguments coming from obj.arglists which is of the form
    #   [(SimpleTypeD, obj), (...)]
    #   The reason this is not really correct is that you could theoretically
    #   use SMember to check for these literal pairs, but that would be very
    #   unusual and is in fact something that happens/happened often accidentally
    #   after a recent refactoring.
    for item in items:
        if type(item) is tuple and len(item) == 2:
            td, obj = item
            assert not isinstance(td, SimpleTypeD), \
                f"createSMember called with list of pairs, expecting list of objects: {items}"
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
