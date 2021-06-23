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

from collections.abc import Iterable


def generate_lazy_val(func):
    saved_value = None
    called = False

    def lazy_holder():
        nonlocal called, saved_value
        if called:
            return saved_value
        else:
            saved_value = func()
            called = True
            return saved_value

    return lazy_holder


def fixed_point(v, f, good_enough):
    history = []
    while True:
        v2 = f(v)
        if good_enough(v, v2):
            return v
        if v2 in history:
            for debug_v2 in history:
                print(debug_v2)
            raise AssertionError("Failed: fixedPoint encountered the same value twice:", v2)
        else:
            history.append(v)
            v = v2


def find_simplifier(self, simplifiers):
    """simplifiers is a list of 0-ary functions.
    Calling such a function either returns `this` or something else.
    We call all the functions in turn, as long as they return `this`.
    As soon as such a function returns something other than `this`,
    then that new value is returned from find_simplifier.
    As a last resort, `this` is returned."""

    for s in simplifiers:
        out = s()
        if self != out:
            return out
    return self


def uniquify(seq):
    """remove duplicates from a list, but preserve the order.
    If duplicates occur in the given list, then left-most occurrences
    are removed, so that the right-most occurrence remains.
    E.g., uniquify([1,2,3,2]) --> [1,3,2]"""
    from collections import OrderedDict

    return list(reversed(list(OrderedDict.fromkeys(reversed(seq)))))


def flat_map(f, xs):
    from collections.abc import Iterable
    assert isinstance(xs, Iterable), f"expecting Iterable not {xs}"

    return [y for z in xs for y in f(z)]


def search_replace_splice(xs, search, replace):
    assert isinstance(xs, Iterable)

    def select(x):
        if x == search:
            return replace
        else:
            return [x]
    return flat_map(select, xs)


def search_replace(xs, search, replace):
    assert isinstance(xs, Iterable)

    return search_replace_splice(xs, search, [replace])


def remove_element(xs, search):
    assert isinstance(xs, Iterable)

    return search_replace_splice(xs, search, [])


# find first element of list which makes the predicate true
# if no such element is found, return the given default or None
def find_first(pred, xs, default=None):
    assert isinstance(xs, Iterable)

    return next(filter(pred, xs), default)


def compare_sequence(xs, ys):
    from genus_types import cmp_type_designators

    def comp(us, vs):
        if not us and not vs:
            # we have reached the end of what we thought were different sequences
            raise ValueError(f"expecting different sequences {xs} vs {ys}")
        elif not us:
            return True
        elif not vs:
            return False
        elif us[0] == vs[0]:
            # TODO this is a poor approach, using tail recursion on arrays.
            # need to refactor
            return comp(us[1:-1], vs[1:-1])
        else:
            return cmp_type_designators(us[0], vs[0]) < 0
    return comp(xs, ys)


# this class can be used to monitor recursive calls to detect infinite recursion.
#   To use the class, declare/bind an instance of CallStack("some-name").
#   You may then use obj.push(...) and obj.(pop)
#   If you ever push the same object twice without popping it, you'll get
#   a run-time exception.
class CallStack:
    def __init__(self, name):
        self.stack = []
        self.name = name

    def push(self, value):
        if value in self.stack:
            self.stack.append(value)
            for i in range(len(self.stack)):
                print(f"  {self.name}:{i}: {self.stack[i]}")
            raise Exception(f"loop detected: {value}")
        else:
            self.stack.append(value)

    def pop(self):
        self.stack.pop()
