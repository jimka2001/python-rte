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

from collections import OrderedDict
from collections.abc import Iterable
from functools import reduce  # import needed for python3; builtin in python2
from collections import defaultdict
from typing import TypeVar, Callable, List, Literal, Union, Dict, Tuple, Optional

T = TypeVar('T')  # Declare type variable
S = TypeVar('S')  # Declare type variable
V = TypeVar('V')  # Declare type variable
L = TypeVar('L')  # Declare type variable


def generate_lazy_val(func: Callable[[], T]) -> Callable[[], T]:
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


def fixed_point(v: T,
                f: Callable[[T], T],
                good_enough: Callable[[T, T], bool],
                invariant: Union[None, Callable[[T], bool]] = None) -> T:
    # if invariant is given, it should be a function we can call on the
    #   input v, and also on the computed result, f(v)
    #   if the invariant fails to return True, the an exception will be thrown
    history = []
    if invariant:
        assert invariant(v), f"invariant failed on initial value v={v}"
    while True:
        v2 = f(v)
        if invariant:
            assert invariant(v2), f"invariant failed on computed value\n  starting v={v}\n computed v2={v2}"
        if good_enough(v, v2):
            return v
        if v2 in history:
            for debug_v2 in history:
                print(debug_v2)
            raise AssertionError("Failed: fixedPoint encountered the same value twice:", v2)
        else:
            history.append(v)
            v = v2


def find_simplifier(self: S, simplifiers: List[Callable[[], S]],
                    verbose: bool = False) -> S:
    """simplifiers is a list of 0-ary functions.
    Calling such a function either returns `this` or something else.
    We call all the functions in turn, as long as they return `this`.
    As soon as such a function returns something other than `this`,
    then that new value is returned from find_simplifier.
    As a last resort, `this` is returned."""
    a = 0
    for s in simplifiers:
        out = s()
        if self != out:
            if verbose:
                # a variable index the function used from 0
                print(f"a = {a}  Simplifier: {stack_depth()}")
                print(f" {s}\n      {self}\n  --> {out}")
            return out
        a += 1
    return self


def uniquify(seq: List[T]) -> List[T]:
    """remove duplicates from a list, but preserve the order.
    If duplicates occur in the given list, then left-most occurrences
    are removed, so that the right-most occurrence remains.
    E.g., uniquify([1,2,3,2]) --> [1,3,2]"""

    return list(reversed(list(OrderedDict.fromkeys(reversed(seq)))))


def flat_map(f: Callable[[T], List[T]],
             xs: Iterable[T]) -> List[T]:
    return [y for z in xs for y in f(z)]


def search_replace_splice(xs: Iterable[T],
                          search: T,
                          replace: Iterable[T]) -> List[T]:
    def select(x):
        if x == search:
            return replace
        else:
            return [x]

    return flat_map(select, xs)


def search_replace(xs: Iterable[T],
                   search: T,
                   replace: T) -> List[T]:
    return search_replace_splice(xs, search, [replace])


# remove a given element from a list every time it occurs
def remove_element(xs: Iterable[T],
                   search: T) -> List[T]:
    return search_replace_splice(xs, search, [])


# find first element of list which makes the predicate true
# if no such element is found, return the given default or None
def find_first(pred: Callable[[T], bool],
               xs: Iterable[T],
               default: S = None) -> Union[T, S]:
    return next(filter(pred, xs), default)


# return 0 if a == b
#        -1 if a < b
#        1 if a > b
def cmp_objects(a: T, b: S) -> Literal[-1, 0, 1]:
    if type(a) == type(b) and a == b:
        return 0
    elif type(a) == type(b):
        return a.cmp_to_same_class_obj(b)
    elif type(a).__name__ < type(b).__name__:
        return -1
    else:
        return 1


def compare_sequence(xs: List[T],
                     ys: List[T]) -> Literal[-1, 0, 1]:
    def comp(i):
        if i >= len(xs) and i >= len(ys):
            return 0
        elif i >= len(xs):
            return -1
        elif i >= len(ys):
            return 1
        elif xs[i] == ys[i]:
            return comp(i + 1)
        else:
            return cmp_objects(xs[i], ys[i])

    return comp(0)


# this class can be used to monitor recursive calls to detect infinite recursion.
#   To use the class, declare/bind an instance of CallStack("some-name").
#   You may then use obj.push(...) and obj.(pop)
#   If you ever push the same object twice without popping it, you'll get
#   a run-time exception.
class CallStack:
    def __init__(self, name, trace):
        self.stack = []
        self.name = name
        self.trace = trace

    def push(self, value):
        if value in self.stack:
            self.stack.append(value)
            for i in range(len(self.stack)):
                print(f"  {self.name}:{i}: {self.stack[i]}")
            raise Exception(f"loop detected: {value}")
        else:
            self.stack.append(value)
            if self.trace:
                print(f"[{len(self.stack)}: {self.name} {value}")

    def pop(self, comment=None):
        if self.trace:
            c2 = "" if comment is None else comment
            print(f" {len(self.stack)}] {self.name} {c2}")
        self.stack.pop()


# compute a list of all the subclasses of a given class.
# this code comes from
#   https://www.studytonight.com/python-howtos/how-to-find-all-the-subclasses-of-a-class-given-its-name
def get_all_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def trace_graph(v0: V,
                edges: Callable[[V], List[Tuple[L, V]]]) -> Tuple[List[V],
                                                                  List[List[Tuple[L, int]]]]:
    # v0 type V
    # edges V => List[(L,V)]
    # if V is te type of vertex
    # and L is the type of label

    current_state_id = 0  # int
    next_available_state = 1  # int
    es = edges(v0)  # List[(L,V)]
    int_to_v = [v0]  # List[V]
    v_to_int = {v0: 0}  # Map[V -> int]
    m = [[]]  # List[List[int]]
    esi = 0  # index into es[...]
    while True:
        if esi == len(es):
            nxt = current_state_id + 1
            if nxt < next_available_state:
                v2 = int_to_v[nxt]
                current_state_id = nxt
                es = edges(v2)
                esi = 0
                m.append([])
                continue
            else:
                return int_to_v, m
        else:
            label, v1 = es[esi]
            if v1 not in v_to_int:
                v_to_int[v1] = next_available_state
                next_available_state = next_available_state + 1
                int_to_v = int_to_v + [v1]
                continue
            else:
                # non-destructively update the list held at m[current_state_id]
                #   by adding a new pair at the end (label,v_to_int[v1])
                m[current_state_id] = m[current_state_id] + [(label, v_to_int[v1])]
                esi = esi + 1
                continue


def stringify(vec: List[T],
              tabs: int) -> str:
    return "[" + ("\n" + " " * (1 + tabs)).join([str(i) + ": " + str(vec[i]) for i in range(len(vec))]) + "]"


def dot_view(dot_string: str,
             verbose: bool = False,
             title: str = "no-name"):
    import platform
    import subprocess
    import tempfile
    png_file_name = tempfile.mkstemp(prefix=title + "-", suffix=".png")[1]

    cmd = ["/usr/local/bin/dot", "-Tpng", "-o", png_file_name]
    exit_status = subprocess.run(cmd, input=str.encode(dot_string))
    if verbose:
        print(f"dot_view: {png_file_name}")
    if exit_status.returncode != 0:
        print("exit_status={exit_status}")
        return None
    if "Darwin" == platform.system():
        return subprocess.run(["open", "-g", "-a", "Preview", png_file_name])
    return None


def stack_depth() -> int:
    import inspect
    return len(inspect.stack(0))


# this implementation comes directly from stackoverflow
#   https://stackoverflow.com/users/1056941/ronen
# thanks to ronen user:1056941 for the code sample
def group_by(key: Callable[[T], S],
             seq: Iterable[T]) -> Dict[S, List[T]]:
    return reduce(lambda grp, val: grp[key(val)].append(val) or grp, seq, defaultdict(list))


# build a Dict which maps keys to value.
# for each element of the input sequence, we call the key function on
#   the element.  That gives us the key for the dictionary.
#   The value is a list of values, one for each element of the input sequence
#   for which key returns that key.  The values in the list are not necessarily
#   the value from the sequence, but return value of the store function.
#  E.g., to transform [(1,"a"), (2, "b"), (1, "c"), (3, "d")]
#    to { 1: [(1,"a"), (1, "c")],
#         2: [(2, "b")],
#         3: [(3, "d")]}
#  use group_by, group_by(lambda x: x[0],
#                         sequence)
#
#  but to transform [(1,"a"), (2, "b"), (1, "c"), (3, "d")]
#    to { 1: ["a" "c"],
#         2: ["b"],
#         3: ["d"]}
# use group_map(lambda x: x[0],
#               sequence,
#               lambda x: x[1])
def group_map(key: Callable[[T], S],
              seq: Iterable[T],
              store: Callable[[T], V]
              ) -> Dict[S, List[V]]:
    grouped = {}
    for q in seq:
        k = key(q)
        if k in grouped:
            grouped[k].append(store(q))
        else:
            grouped[k] = [store(q)]
    return grouped


def split_eqv_class(objects: Tuple[T, ...],
                    f: Callable[[T], S]) -> List[Tuple[T, ...]]:
    if len(objects) == 1:
        return [objects]
    else:
        grouped = group_by(f, objects)
        return [tuple(grouped[k]) for k in grouped]


def find_eqv_class(partition: Iterable[Tuple[T, ...]],
                   target: T) -> Optional[Tuple[T, ...]]:
    # given partition, a list of mutually disjoint lists
    # return the list which contains target, or None if not found
    for eqv_class in partition:
        if target in eqv_class:
            return eqv_class
    return None


def pip_install(package):
    # running pip install from the shell will install libraries according to the
    # unix environment, which might be different than the particular python
    # being used.   using something like pip_install('typing_extensions') from
    # the python console seems to install the the *correct* place so it can
    # be referenced by the python being run.
    import pip

    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])
