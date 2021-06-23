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


import os

from s_not import SNot
from s_or import SOr
from s_top import STop
from s_empty import SEmpty
from simple_type_d import SimpleTypeD
from s_atomic import SAtomic
from s_custom import SCustom
from s_and import SAnd
from s_eql import SEql
from s_member import SMember


def t_verboseonlyprint(s):
    if 'genusverbose' in os.environ and os.environ['genusverbose'] == str(True):
        print(s)


def t_fixed_point():
    from utils import fixed_point
    assert fixed_point(0, (lambda x: x), (lambda x, y: x == y)) == 0
    assert fixed_point(0, (lambda x: x//2), (lambda x, y: x == y)) == 0


def t_STop():
    from s_empty import SEmptyImpl
    from s_top import STopImpl

    a = STop

    # STop has to be unique
    assert(id(a) == id(STopImpl.get_omega()))

    # STop has to be unique part 2: ensure the constructor throws an error
    pred = True
    try:
        _b = STop()
        pred = False
        assert False
    except Exception as _e:
        assert pred

    # str(a) has to be "Top"
    assert(str(a) == "Top")

    # a.typep(t) indicates whether t is a subtype of a, which is always the case by definition
    assert(a.typep(SAtomic(object)))
    assert(a.typep(a))

    # obviously, a is inhabited as it contains everything by definition
    assert(a.inhabited() is True)

    # a is never disjoint with anything but the empty subtype
    assert a.disjoint(SAtomic(object)) is False
    assert a.disjoint(SEmptyImpl.get_epsilon()) is True

    # on the contrary, a is never a subtype of any type
    # since types are sets and top is the set that contains all sets
    assert(a.subtypep(SAtomic(object)) is True)
    assert a.subtypep(a) is True

    # my understanding is that the top type is unique so it can't be positively compared to any object
    assert(not a.cmp_to_same_class_obj(a))
    assert(not a.cmp_to_same_class_obj(object))


def t_scustom():
    def l_odd(n):
        return isinstance(n, int) and n % 2 == 1

    guinea_pig = SCustom(l_odd, "[odd numbers]")
    assert guinea_pig.f == l_odd
    assert guinea_pig.printable == "[odd numbers]"
    assert str(guinea_pig) == "[odd numbers]?"
    for x in range(-100, 100):
        if x % 2 == 1:
            assert guinea_pig.typep(x)
        else:
            assert not guinea_pig.typep(x)
    assert(not guinea_pig.typep("hello"))
    assert(guinea_pig.subtypep(SAtomic(type(4))) is None)


def t_sand1():
    from genus_types import createSAnd
    quadruple = SCustom((lambda x: x % 4 == 0), "quadruple")

    triple = SCustom(lambda x: isinstance(x, int) and (x % 3 == 0), "triple")
    
    tri_n_quad = SAnd(triple, quadruple)
    create_tri_n_quad = createSAnd([triple, quadruple])

    assert(str(tri_n_quad) == "[SAnd triple?,quadruple?]")
    assert(str(create_tri_n_quad) == "[SAnd triple?,quadruple?]")

    assert(tri_n_quad.typep(12))
    assert(create_tri_n_quad.typep(12))
    assert(not tri_n_quad.typep(6))
    assert(not create_tri_n_quad.typep(6))
    assert(not tri_n_quad.typep(3))
    assert(not create_tri_n_quad.typep(3))
    assert(tri_n_quad.typep(0))
    assert(create_tri_n_quad.typep(0))
    assert(not tri_n_quad.typep("hello"))
    assert(not create_tri_n_quad.typep("hello"))


def t_sand2():
    from genus_types import createSAnd
    quadruple = SCustom((lambda x: x % 4 == 0), "quadruple")

    triple = SCustom(lambda x: isinstance(x, int) and (x % 3 == 0), "triple")

    tri_n_quad = SAnd(triple, quadruple)
    create_tri_n_quad = createSAnd([triple, quadruple])
    assert(tri_n_quad.subtypep(STop))
    assert(tri_n_quad.subtypep(triple))

    assert(tri_n_quad.subtypep(quadruple))
    assert tri_n_quad.subtypep(SAtomic(type(5))) is None, "%s != None" % tri_n_quad.subtypep(SAtomic(type(5)))

    assert(SAnd().unit() == STop)
    assert(SAnd().zero() == SEmpty)

    assert(tri_n_quad.same_combination(create_tri_n_quad))
    assert(tri_n_quad.same_combination(createSAnd([quadruple, triple])))

    assert(not tri_n_quad.same_combination(STop))
    assert(not tri_n_quad.same_combination(createSAnd([])))


def t_sor():
    from genus_types import createSOr
    quadruple = SCustom(lambda x: isinstance(x, int) and x % 4 == 0, "quadruple")
    triple = SCustom(lambda x: isinstance(x, int) and x % 3 == 0, "triple")
    
    tri_o_quad = SOr(triple, quadruple)
    create_tri_o_quad = createSOr([triple, quadruple])

    assert(str(tri_o_quad) == "[SOr triple?,quadruple?]")
    assert(str(create_tri_o_quad) == "[SOr triple?,quadruple?]")

    assert(tri_o_quad.typep(12))
    assert(create_tri_o_quad.typep(12))
    
    assert(tri_o_quad.typep(6))
    assert(create_tri_o_quad.typep(6))
    
    assert(tri_o_quad.typep(3))
    assert(create_tri_o_quad.typep(3))
    
    assert(tri_o_quad.typep(0))
    assert(create_tri_o_quad.typep(0))

    assert(not tri_o_quad.typep(5))
    assert(not create_tri_o_quad.typep(5))
    
    assert(not tri_o_quad.typep("hello"))
    assert(not create_tri_o_quad.typep("hello"))

    assert(SOr().unit() == SEmpty.get_epsilon())

    assert(SOr().zero() == STop.get_omega())

    assert(tri_o_quad.subtypep(STop.get_omega()))
    assert(tri_o_quad.subtypep(SAtomic(type(5))) is None)

    assert(tri_o_quad.same_combination(create_tri_o_quad))
    assert(tri_o_quad.same_combination(createSOr([quadruple, triple])))

    assert(not tri_o_quad.same_combination(STop))
    assert(not tri_o_quad.same_combination(createSOr([])))


def t_snot():
    pair = SCustom(lambda x: isinstance(x, int) and x & 1 == 0, "pair")
    
    pred = True
    try:
        _b = SNot([])
        pred = False
        assert False
    except Exception as _e:
        assert pred

    npair = SNot(pair)

    assert SNot(SNot(pair)).canonicalize() == pair

    assert(str(npair) == "[SNot pair?]")

    assert(npair.typep(5))
    assert(npair.typep("hello"))
    assert(not npair.typep(4))
    assert(not npair.typep(0))


def t_SimpleTypeD():
    from simple_type_d import NormalForm
    from utils import fixed_point

    # ensuring SimpleTypeD is abstract
    pred = True
    try:
        _foo = SimpleTypeD()
        pred = False
        assert False
    except Exception:
        assert pred

    # ensuring typep is an abstract method
    try:
        class ChildSTDNoTypep(SimpleTypeD):
            """just for testing"""

            def __init__(self):
                super(ChildSTDNoTypep, self).__init__()

        _ = ChildSTDNoTypep()
        del ChildSTDNoTypep
        pred = False
        assert False
    except Exception:
        assert pred

    class ChildSTD(SimpleTypeD):
        """docstring for ChildSTD"""

        def __init__(self):
            super(ChildSTD, self).__init__()

        def typep(self, a):
            pass

    child = SAtomic(ChildSTD)

    # _inhabited_down is None to indicate that we actually don't know
    # whether it is as this is the generic version
    assert (child.inhabited() is True)

    # this one is weird. How come we can't detect that it is the same set?
    # anyway, this is how the scala code seems to behave
    # as a reminder: True means yes, False means no, None means maybe
    assert (child.disjoint(child) is False)

    assert (child == child.to_dnf())
    assert (child == child.to_cnf())

    nf = [NormalForm.DNF, NormalForm.CNF]
    assert (child == child.maybe_dnf(nf))
    assert (child == child.maybe_cnf(nf))

    # fixed_point is just a way to incrementally apply a function on a value
    # until another function deem the delta between two consecutive values to be negligible
    def increment(x):
        return x

    def evaluator(x, y):
        return x == y

    assert (fixed_point(5, increment, evaluator) == 5)
    assert (fixed_point(5, lambda x: x + 1, lambda x, y: x == 6 and y == 7) == 6)

    assert (child == child.canonicalize_once())
    assert (child == child.canonicalize() and child.canonicalized_hash == {None: child})
    # the second time is to make sure it isn't adding the same twice
    assert (child == child.canonicalize() and child.canonicalized_hash == {None: child})

    # ensuring cmp_to_same_class_obj() throws no error
    assert child.cmp_to_same_class_obj(child) is False


# TODO: move the tests in their own files once this is packaged:
def t_STop2():
    from s_top import STopImpl
    # STop has to be unique
    assert id(STop) == id(STopImpl.get_omega())

    # STop has to be unique part 2: ensure the constructor throws an error
    pred = True
    try:
        _ = STop()
        pred = False
        assert False
    except Exception as _:
        assert pred

    # str(a) has to be "Top"
    assert str(STop) == "Top"

    # a.subtypep(t) indicates whether t is a subtype of a, which is always the case by definition
    assert STop.subtypep(SAtomic(object)) is True
    assert STop.subtypep(STop) is True

    # obviously, a is inhabited as it contains everything by definition
    assert STop.inhabited() is True

    # a is never disjoint with anything but the empty subtype
    assert STop.disjoint(SAtomic(object)) is False
    assert STop.disjoint(SEmpty) is True

    # on the contrary, a is never a subtype of any type
    # since types are sets and top is the set that contains all sets
    assert (STop.subtypep(SAtomic(object)) is not False)
    assert (STop.subtypep(STop) is True)

    # my understanding is that the top type is unique so it can't be positively compared to any object
    assert (not STop.cmp_to_same_class_obj(STop))
    assert (not STop.cmp_to_same_class_obj(SAtomic(object)))


# TODO: move the tests in their own files once this is packaged:
def t_SEmpty():
    from s_empty import SEmptyImpl
    # SEmpty has to be unique
    assert (id(SEmpty) == id(SEmptyImpl.get_epsilon()))

    # SEmpty has to be unique part 2: ensure the constructor throws an error
    pred = True
    try:
        _ = SEmpty()
        pred = False
        assert False
    except Exception as _e:
        assert pred

    # str(a) has to be "Empty"
    assert str(SEmpty) == "Empty"

    # a.typep(t) indicates whether t is a subtype of a, which is never the case
    assert SEmpty.typep(3) is False
    assert SEmpty.subtypep(SEmpty) is True

    # obviously, a is not inhabited as it is by definition empty
    assert SEmpty.inhabited() is False

    # a is disjoint with anything as it is empty
    assert SEmpty.disjoint(SAtomic(object)) is True

    # on the contrary, a is always a subtype of any type
    # since types are sets and the empty set is a subset of all sets
    assert SEmpty.subtypep(SAtomic(object)) is True
    assert SEmpty.subtypep(SEmpty) is True

    # my understanding is that the empty type is unique so it can't be positively compared to any object
    assert (not SEmpty.cmp_to_same_class_obj(SEmpty))
    assert (not SEmpty.cmp_to_same_class_obj(SAtomic(object)))


def t_scustom2():
    def l_odd(n):
        return isinstance(n, int) and n % 2 == 1
    guinea_pig = SCustom(l_odd, "[odd numbers]")
    assert guinea_pig.f == l_odd
    assert guinea_pig.printable == "[odd numbers]"
    assert str(guinea_pig) == "[odd numbers]?"
    for x in range(-100, 100):
        if x % 2 == 1:
            assert guinea_pig.typep(x)
        else:
            assert not guinea_pig.typep(x)


def t_subtypep1():
    from depth_generator import random_type_designator
    for depth in range(0, 4):
        for _ in range(1000):
            td1 = random_type_designator(depth)
            td2 = random_type_designator(depth)
            assert td1.subtypep(td1) is True
            assert SAnd(td1, td2).subtypep(td1) is not False
            assert td1.subtypep(SOr(td1, td2)) is not False
            assert SAnd(td1, td2).subtypep(SAnd(td2, td1)) is not False
            assert SOr(td1, td2).subtypep(SOr(td2, td2)) is not False
            assert SAnd(td1, td2).subtypep(SOr(td1, td2)) is not False
            assert SAnd(SNot(td1), SNot(td2)).subtypep(SNot(SOr(td1, td2))) is not False
            assert SOr(SNot(td1), SNot(td2)).subtypep(SNot(SAnd(td1, td2))) is not False
            assert SNot(SOr(td1, td2)).subtypep(SAnd(SNot(td1), SNot(td2))) is not False
            assert SNot(SAnd(td1, td2)).subtypep(SOr(SNot(td1), SNot(td2))) is not False


def t_subtypep2():
    from depth_generator import random_type_designator
    from genus_types import NormalForm
    for depth in range(0, 4):
        for _ in range(1000):
            td = random_type_designator(depth)
            tdc1 = td.canonicalize()
            tdc2 = td.canonicalize(NormalForm.DNF)
            tdc3 = td.canonicalize(NormalForm.CNF)

            assert td.subtypep(tdc1) is not False
            assert td.subtypep(tdc2) is not False
            assert td.subtypep(tdc2) is not False
            assert tdc1.subtypep(td) is not False, \
                f"expecting tdc1={tdc1} subtype of {td} got {tdc1.subtypep(td)}"
            assert tdc2.subtypep(td) is not False, \
                f"expecting tdc2={tdc2} subtype of {td} got {tdc2.subtypep(td)}"
            assert tdc3.subtypep(td) is not False, \
                f"expecting tdc3={tdc3} subtype of {td} got {tdc3.subtypep(td)}"


def t_uniquify():
    from utils import uniquify
    assert uniquify([]) == []
    assert uniquify([1]) == [1]
    assert uniquify([5, 4, 3, 2, 1]) == [5, 4, 3, 2, 1]
    assert uniquify([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]
    assert uniquify([1, 1, 1, 1, 1]) == [1]
    assert uniquify([1, 2, 1, 2]) == [1, 2]
    assert uniquify([1, 2, 1]) == [2, 1]


def t_lazy():
    from utils import generate_lazy_val

    c = 0

    def g():
        nonlocal c
        c = c + 1
        return c

    assert c == 0
    assert g() == 1
    assert c == 1

    f = generate_lazy_val(lambda: g())
    assert c == 1
    assert f() == 2
    assert c == 2
    assert f() == 2
    assert c == 2


def t_discovered_cases():
    def f(_a):
        return False

    assert SNot(SAtomic(int)).subtypep(SNot(SCustom(f, "f"))) is None
    assert SAtomic(int).disjoint(SCustom(f, "f")) is None
    assert SAtomic(int).disjoint(SNot(SCustom(f, "f"))) is None
    assert SNot(SAtomic(int)).disjoint(SCustom(f, "f")) is None
    assert SNot(SAtomic(int)).disjoint(SNot(SCustom(f, "f"))) is None

    assert SAtomic(int).subtypep(SCustom(f, "f")) is None
    assert SAtomic(int).subtypep(SNot(SCustom(f, "f"))) is None
    assert SNot(SAtomic(int)).subtypep(SCustom(f, "f")) is None


def t_or():
    assert len(SOr(SEql(1), SEql(2)).tds) == 2
    assert SOr().tds == []


def t_member():
    assert SMember(1, 2, 3).arglist == [1, 2, 3]
    assert SMember().arglist == []


def t_eql():
    assert SEql(1).a == 1
    assert SEql(1).arglist == [1], f"expecting arglist=[1], got {SEql(1).arglist}"


def t_discovered_cases2():
    td = SAnd(SEql(3.14), SMember("a", "b", "c"))
    tdc = td.canonicalize()
    assert tdc == SEmpty, f"expecting {td} to canonicalize to SEmpty, got {tdc}"

def t_membership():
    from depth_generator import random_type_designator, test_values
    from genus_types import NormalForm
    for depth in range(0, 4):
        for _ in range(1000):
            td = random_type_designator(depth)
            tdc1 = td.canonicalize()
            tdc2 = td.canonicalize(NormalForm.DNF)
            tdc3 = td.canonicalize(NormalForm.CNF)
            for v in test_values:
                assert td.typep(v) == tdc1.typep(v), \
                    f"v={v} is membership of type td={td} is {td.typep(v)} but of type tdc1={tdc1} is {tdc1.typep(v)}"
                assert td.typep(v) == tdc2.typep(v), \
                    f"v={v} is membership of type td={td} is {td.typep(v)} but of type tdc2={tdc2} is {tdc2.typep(v)}"
                assert td.typep(v) == tdc3.typep(v), \
                    f"v={v} is membership of type td={td} is {td.typep(v)} but of type tdc3={tdc3} is {tdc3.typep(v)}"


#   calling the test functions

t_discovered_cases2()
t_or()
t_member()
t_eql()
t_discovered_cases()
t_lazy()
t_uniquify()
t_fixed_point()
t_scustom()
t_scustom2()
t_sand1()
t_sand2()
t_sor()
t_snot()
t_STop()
t_STop2()
t_SEmpty()
t_SimpleTypeD()
t_membership()
t_subtypep1()
t_subtypep2()
