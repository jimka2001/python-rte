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

from genus.s_and import SAnd
from genus.s_satisfies import SSatisfies
from genus.s_empty import SEmptyImpl, SEmpty
from genus.s_member import SMemberImpl
from genus.s_or import SOr
from genus.s_top import STopImpl
from genus.simple_type_d import SimpleTypeD, TerminalType
from genus.utils import get_all_subclasses
from genus.genus_types import NormalForm
from typing import Literal, Any, Optional
from typing_extensions import TypeGuard


class SAtomic(SimpleTypeD, TerminalType):
    """The atoms of our type system: a simple type built from a native python type."""
    __instances = {}

    # reminder: the types are:
    # numerical: "int", "float", "complex"
    # sequential: "list", "tuple", "range" (+ * binary sequences + * text sequences)
    # binary sequential: "bytes", "bytearray", "memoryview"
    # text sequential: "str"
    # in addition, all classes are types and all types are classes

    def __new__(cls, wrapped_class, *a, **kw):
        if wrapped_class not in SAtomic.__instances:
            SAtomic.__instances[wrapped_class] = super(SAtomic, cls).__new__(cls, *a, **kw)
        return SAtomic.__instances[wrapped_class]

    def __init__(self, wrapped_class):
        import inspect
        super(SAtomic, self).__init__()
        assert inspect.isclass(wrapped_class), \
            f"wrapped_class={wrapped_class} is not a class, its type is {type(wrapped_class)}"
        self.wrapped_class = wrapped_class

    def __str__(self) -> str:
        return "SAtomic(" + self.wrapped_class.__name__ + ")"

    def __eq__(self, that: Any) -> bool:
        return isinstance(that, SAtomic) \
               and self.wrapped_class is that.wrapped_class

    def __hash__(self):
        return hash(self.wrapped_class)

    def typep(self, a: Any) -> bool:
        # check that this does what we want (looks like it does but eh)
        return isinstance(a, self.wrapped_class)

    def inhabited_down(self) -> Optional[bool]:
        # consider all SAtomic types as being inhabited.
        # as far as I know Python does not support an empty type.
        return True

    def disjoint_down(self, t: SimpleTypeD) -> Optional[bool]:
        ct = self.wrapped_class

        if isinstance(t, SEmptyImpl):
            return True
        elif isinstance(t, STopImpl):
            return False
        elif isinstance(t, SAtomic):
            tp = t.wrapped_class
            if self.inhabited() is False:
                return True
            elif tp == ct:
                return False
            elif issubclass(tp, ct) or issubclass(ct, tp):
                # is either a subclass of the other
                return False
            else:
                # if they have a common subclass, they are not disjoint

                # return not any(c for c in get_all_subclasses(ct)
                # 	               if c in tp_subclasses)

                # 2 n log n searches should be faster than one n^2 search
                # by iterating over both lists of subclasses and asking whether the
                #  other is a superclass of it?
                # return not (any(issubclass(c, tp) for c in get_all_subclasses(ct))
                #            or any(issubclass(c, ct) for c in get_all_subclasses(tp)))

                # 1 n log n should find the same boolean value
                return not any(issubclass(c, tp) for c in get_all_subclasses(ct))

        else:
            return super().disjoint_down(t)

    def subtypep_down(self, s: SimpleTypeD) -> Optional[bool]:
        from genus.s_not import SNot
        if self.inhabited() is False:
            return True
        elif isinstance(s, SEmptyImpl):
            # here we know self.inhabited() is either None or True
            # if self is inhabited then it is _NOT_ a subtype of SEmpty, so return False
            return None if self.inhabited() is None else False
        elif isinstance(s, STopImpl):
            return True
        elif isinstance(s, SAtomic):
            if s.inhabited() is False:
                return self.subtypep(SEmpty)
            elif s.inhabited() is None:
                return None
            elif self.inhabited() is None and s.inhabited() is True:
                return None
            elif self.inhabited() is True and s.inhabited() is True:
                return issubclass(self.wrapped_class, s.wrapped_class)
            else:
                raise NotImplementedError
        elif isinstance(s, SMemberImpl):
            return False  # no finite list exhausts all elements of a class
        elif isinstance(s, SNot):
            return super().subtypep_down(s)
        elif isinstance(s, SOr):
            if any(self.subtypep(td) is True for td in s.tds):
                return True
            elif all(self.disjoint(td) is True for td in s.tds):
                return False
            else:
                return super().subtypep_down(s)
        elif isinstance(s, SAnd):
            if all(self.subtypep(td) is True for td in s.tds):
                return True
            elif all(self.disjoint(td) is True for td in s.tds):
                return False
            else:
                return super().subtypep_down(s)
        elif isinstance(s, SSatisfies):
            return super().subtypep_down(s)
        else:
            return super().subtypep_down(s)

    def canonicalize_once(self, nf: Optional[NormalForm] = None) -> SimpleTypeD:
        return SAtomic(self.wrapped_class)

    def cmp_to_same_class_obj(self, td: 'SAtomic') -> Literal[-1, 0, 1]:
        if type(self) != type(td):
            return super().cmp_to_same_class_obj(td)
        elif self == td:
            return 0
        elif self.wrapped_class.__name__ < td.wrapped_class.__name__:
            return -1
        else:
            return 1


def atomicp(this: Any) -> TypeGuard[SAtomic]:
    return isinstance(this, SAtomic)
