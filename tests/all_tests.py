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
    assert fixed_point(0, (lambda x: x // 2), (lambda x, y: x == y)) == 0


def t_STop():
    from s_empty import SEmptyImpl
    from s_top import STopImpl

    a = STop

    # STop has to be unique
    assert (id(a) == id(STopImpl.get_omega()))

    # STop has to be unique part 2: ensure the constructor throws an error
    pred = True
    try:
        _b = STop()
        pred = False
        assert False
    except Exception as _e:
        assert pred

    # str(a) has to be "Top"
    assert (str(a) == "STop")

    # a.typep(t) indicates whether t is a subtype of a, which is always the case by definition
    assert (a.typep(SAtomic(object)))
    assert (a.typep(a))

    # obviously, a is inhabited as it contains everything by definition
    assert (a.inhabited() is True)

    # a is never disjoint with anything but the empty subtype
    assert a.disjoint(SAtomic(object)) is False
    assert a.disjoint(SEmptyImpl.get_epsilon()) is True

    # on the contrary, a is never a subtype of any type
    # since types are sets and top is the set that contains all sets
    assert (a.subtypep(SAtomic(object)) is True)
    assert a.subtypep(a) is True


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
    assert (not guinea_pig.typep("hello"))
    assert (guinea_pig.subtypep(SAtomic(type(4))) is None)


def t_sand1():
    from genus_types import createSAnd
    quadruple = SCustom((lambda x: x % 4 == 0), "quadruple")

    triple = SCustom(lambda x: isinstance(x, int) and (x % 3 == 0), "triple")

    tri_n_quad = SAnd(triple, quadruple)
    create_tri_n_quad = createSAnd([triple, quadruple])

    assert (str(tri_n_quad) == "[SAnd triple?,quadruple?]")
    assert (str(create_tri_n_quad) == "[SAnd triple?,quadruple?]")

    assert (tri_n_quad.typep(12))
    assert (create_tri_n_quad.typep(12))
    assert (not tri_n_quad.typep(6))
    assert (not create_tri_n_quad.typep(6))
    assert (not tri_n_quad.typep(3))
    assert (not create_tri_n_quad.typep(3))
    assert (tri_n_quad.typep(0))
    assert (create_tri_n_quad.typep(0))
    assert (not tri_n_quad.typep("hello"))
    assert (not create_tri_n_quad.typep("hello"))


def t_sand2():
    from genus_types import createSAnd
    quadruple = SCustom((lambda x: x % 4 == 0), "quadruple")

    triple = SCustom(lambda x: isinstance(x, int) and (x % 3 == 0), "triple")

    tri_n_quad = SAnd(triple, quadruple)
    create_tri_n_quad = createSAnd([triple, quadruple])
    assert (tri_n_quad.subtypep(STop))
    assert (tri_n_quad.subtypep(triple))

    assert (tri_n_quad.subtypep(quadruple))
    assert tri_n_quad.subtypep(SAtomic(type(5))) is None, "%s != None" % tri_n_quad.subtypep(SAtomic(type(5)))

    assert (SAnd().unit() == STop)
    assert (SAnd().zero() == SEmpty)

    assert (tri_n_quad.same_combination(create_tri_n_quad))
    assert (tri_n_quad.same_combination(createSAnd([quadruple, triple])))

    assert (not tri_n_quad.same_combination(STop))
    assert (not tri_n_quad.same_combination(createSAnd([])))


def t_sor():
    from genus_types import createSOr
    quadruple = SCustom(lambda x: isinstance(x, int) and x % 4 == 0, "quadruple")
    triple = SCustom(lambda x: isinstance(x, int) and x % 3 == 0, "triple")

    tri_o_quad = SOr(triple, quadruple)
    create_tri_o_quad = createSOr([triple, quadruple])

    assert (str(tri_o_quad) == "[SOr triple?,quadruple?]")
    assert (str(create_tri_o_quad) == "[SOr triple?,quadruple?]")

    assert (tri_o_quad.typep(12))
    assert (create_tri_o_quad.typep(12))

    assert (tri_o_quad.typep(6))
    assert (create_tri_o_quad.typep(6))

    assert (tri_o_quad.typep(3))
    assert (create_tri_o_quad.typep(3))

    assert (tri_o_quad.typep(0))
    assert (create_tri_o_quad.typep(0))

    assert (not tri_o_quad.typep(5))
    assert (not create_tri_o_quad.typep(5))

    assert (not tri_o_quad.typep("hello"))
    assert (not create_tri_o_quad.typep("hello"))

    assert (SOr().unit() == SEmpty.get_epsilon())

    assert (SOr().zero() == STop.get_omega())

    assert (tri_o_quad.subtypep(STop.get_omega()))
    assert (tri_o_quad.subtypep(SAtomic(type(5))) is None)

    assert (tri_o_quad.same_combination(create_tri_o_quad))
    assert (tri_o_quad.same_combination(createSOr([quadruple, triple])))

    assert (not tri_o_quad.same_combination(STop))
    assert (not tri_o_quad.same_combination(createSOr([])))


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

    assert (str(npair) == "[SNot pair?]")

    assert (npair.typep(5))
    assert (npair.typep("hello"))
    assert (not npair.typep(4))
    assert (not npair.typep(0))


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
    assert str(STop) == "STop"

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
    assert str(SEmpty) == "SEmpty"

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
    assert tdc == SEmpty, f"expecting td={td} to canonicalize to SEmpty, got {tdc}"

    td = SOr(SEql("a"), SAtomic(int))
    tdc = td.canonicalize()
    assert tdc != SAtomic(int)


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
                    f"v={v} membership\n     of type   td={td} is {td.typep(v)}\n" + \
                    f" but of type tdc1={tdc1} is {tdc1.typep(v)}"
                assert td.typep(v) == tdc2.typep(v), \
                    f"v={v} membership\n     of type   td={td} is {td.typep(v)}\n" + \
                    f" but of type tdc2={tdc2} is {tdc2.typep(v)}"
                assert td.typep(v) == tdc3.typep(v), \
                    f"v={v} membership\n     of type   td={td} is {td.typep(v)}\n" + \
                    f" but of type tdc3={tdc3} is {tdc3.typep(v)}"


def t_combo_conversion1():
    assert SAnd().conversion1() == STop
    assert SOr().conversion1() == SEmpty
    assert SAnd(SEql(1)).conversion1() == SEql(1)
    assert SOr(SEql(1)).conversion1() == SEql(1)


def t_combo_conversion2():
    # (and A B SEmpty C D) -> SEmpty,  unit=STop,   zero=SEmpty
    # (or A B STop C D) -> STop,     unit=SEmpty,   zero=STop
    a = SEql("a")
    b = SEql("b")
    c = SEql("c")
    d = SEql("d")
    assert SAnd(a, b, SEmpty, c, d).conversion2() == SEmpty
    assert SOr(a, b, SEmpty, c, d).conversion2() == SOr(a, b, SEmpty, c, d)
    assert SAnd(a, b, STop, c, d).conversion2() == SAnd(a, b, STop, c, d)
    assert SOr(a, b, STop, c, d).conversion2() == STop


def t_combo_conversion3():
    # (and A (not A)) --> SEmpty,  unit=STop,   zero=SEmpty
    # (or A (not A)) --> STop,     unit=SEmpty, zero=STop
    a = SEql("a")
    assert SAnd(a, SNot(a)).conversion3() == SEmpty
    assert SOr(a, SNot(a)).conversion3() == STop


def t_combo_conversion4():
    # SAnd(A,STop,B) ==> SAnd(A,B),  unit=STop,   zero=SEmpty
    # SOr(A,SEmpty,B) ==> SOr(A,B),  unit=SEmpty, zero=STop
    a = SEql("a")
    b = SEql("b")
    assert SAnd(a, STop, b).conversion4() == SAnd(a, b)
    assert SOr(a, STop, b).conversion4() == SOr(a, STop, b)
    assert SAnd(a, SEmpty, b).conversion4() == SAnd(a, SEmpty, b)
    assert SOr(a, SEmpty, b).conversion4() == SOr(a, b)


def t_combo_conversion5():
    # (and A B A C) -> (and A B C)
    # (or A B A C) -> (or A B C)
    a = SEql("a")
    b = SEql("b")
    c = SEql("c")
    assert SAnd(a, b, a, c).conversion5() == SAnd(b, a, c)
    assert SOr(a, b, a, c).conversion5() == SOr(b, a, c)


def t_combo_conversion6():
    # (and A ( and B C) D) --> (and A B C D)
    # (or A ( or B C) D) --> (or A B C D)
    a = SEql("a")
    b = SEql("b")
    c = SEql("c")
    d = SEql("d")
    assert SAnd(a, SAnd(b, c), d).conversion6() == SAnd(a, b, c, d)
    assert SOr(a, SAnd(b, c), d).conversion6() == SOr(a, SAnd(b, c), d)
    assert SOr(a, SAnd(b, c), d).conversion6() == SOr(a, SAnd(b, c), d)
    assert SOr(a, SOr(b, c), d).conversion6() == SOr(a, b, c, d)


def t_combo_conversion7():
    a = SEql("a")
    b = SEql("b")
    c = SEql("c")
    d = SEql("d")
    assert SAnd(b, c, a, d).conversion7(None) == SAnd(a, b, c, d), f"got {SAnd(b, c, a, d).conversion7(None)}"
    assert SOr(b, c, a, d).conversion7(None) == SOr(a, b, c, d)


def t_combo_conversion8():
    # (or A ( not B)) --> STop if B is subtype of A, zero = STop
    # (and A ( not B)) --> SEmpty if B is supertype of A, zero = SEmpty
    a = SEql("a")
    ab = SMember("a", "b")
    c = SEql("c")
    assert a.subtypep(ab) is True
    assert ab.supertypep(a) is True

    assert SAnd(a, SNot(ab), c).conversion8() == SEmpty
    assert SAnd(SNot(a), ab, c).conversion8() == SAnd(SNot(a), ab, c)

    assert SOr(a, SNot(ab), c).conversion8() == SOr(a, SNot(ab), c)
    assert SOr(SNot(a), ab, c).conversion8() == STop


def t_combo_conversion9():
    # (A + B + C)(A + !B + C)(X) -> (A + B + C)(A + C)(X)
    # (A + B +!C)(A +!B + C)(A +!B+!C) -> (A + B +!C)(A + !B + C)(A + !C)
    # (A + B +!C)(A +!B + C)(A +!B+!C) -> does not reduce to(A + B + !C)(A +!B+C)(A)
    a = SEql("a")
    b = SEql("b")
    c = SEql("c")
    x = SEql("x")
    assert SAnd(SOr(a, b, c),
                SOr(a, SNot(b), c),
                x).conversion9() == SAnd(SOr(a, b, c),
                                         SOr(a, c),
                                         x)
    assert SAnd(SOr(a, b, SNot(c)),
                SOr(a, SNot(b), c),
                SOr(a, SNot(b), SNot(c))).conversion9() == SAnd(SOr(a, b, SNot(c)),
                                                                SOr(a, SNot(b), c),
                                                                SOr(a, SNot(c)))
    assert SAnd(SOr(a, b, SNot(c)),
                SOr(a, SNot(b), c),
                SOr(a, SNot(b), SNot(c))).conversion9() == \
           SAnd(SOr(a, b, SNot(c)),
                SOr(a, SNot(b), c),
                SOr(a, SNot(c)))

    assert SOr(SAnd(a, b, c), SAnd(a, SNot(b), c), x).conversion9() == SOr(SAnd(a, b, c), SAnd(a, c), x)
    assert SOr(SAnd(a, b, SNot(c)),
               SAnd(a, SNot(b), c),
               SAnd(a, SNot(b), SNot(c))).conversion9() == \
           SOr(SAnd(a, b, SNot(c)), SAnd(a, SNot(b), c), SAnd(a, SNot(c)))
    assert SOr(SAnd(a, b, SNot(c)),
               SAnd(a, SNot(b), c),
               SAnd(a, SNot(b), SNot(c))).conversion9() == \
           SOr(SAnd(a, b, SNot(c)), SAnd(a, SNot(b), c), SAnd(a, SNot(c)))


def t_combo_conversion10():
    # (and A B C) --> (and A C) if A is subtype of B
    # (or A B C) -->  (or B C) if A is subtype of B
    a = SEql("a")
    ab = SMember("a", "b")
    c = SEql("c")
    assert a.subtypep(ab) is True
    assert ab.supertypep(a) is True
    assert SAnd(a, ab, c).conversion10() == SAnd(a, c)
    assert SOr(a, ab, c).conversion10() == SOr(ab, c)


def t_combo_conversion11():
    # A + A! B -> A + B
    # A + A! BX + Y = (A + BX + Y)
    # A + ABX + Y = (A + Y)
    a = SEql("a")
    b = SEql("b")
    x = SEql("x")
    y = SEql("y")
    assert SOr(a, SAnd(SNot(a), b)).conversion11() == SOr(a, b)
    assert SOr(a, SAnd(SNot(a), b, x), y).conversion11() == SOr(a, SAnd(b, x), y)
    assert SOr(a, SAnd(a, b, x), y).conversion11() == SOr(a, y)

    assert SAnd(a, SOr(SNot(a), b)).conversion11() == SAnd(a, b)
    assert SAnd(a, SOr(SNot(a), b, x), y).conversion11() == SAnd(a, SOr(b, x), y)
    assert SAnd(a, SOr(a, b, x), y).conversion11() == SAnd(a, y)


def t_combo_conversion12():
    # AXBC + !X = ABC + !X
    a = SEql("a")
    b = SEql("b")
    c = SEql("c")
    x = SEql("x")
    assert SOr(SAnd(a, x, b, c), SNot(x)).conversion12() == SOr(SAnd(a, b, c), SNot(x))
    assert SAnd(SOr(a, x, b, c), SNot(x)).conversion12() == SAnd(SOr(a, b, c), SNot(x))


def t_combo_conversion13():
    # multiple !member
    # SOr(x,!{-1, 1},!{1, 2, 3, 4})
    # --> SOr(x,!{1}) // intersection of non-member
    # SAnd(x,!{-1, 1},!{1, 2, 3, 4})
    # --> SOr(x,!{-1, 1, 2, 3, 4}) // union of non-member
    x = SAtomic(int)

    assert SOr(x,
               SNot(SMember(-1, 1)),
               SNot(SMember(1, 2, 3, 4))).conversion13() == SOr(x,
                                                                SNot(SEql(1)))
    assert SAnd(x,
                SNot(SMember(-1, 1)),
                SNot(SMember(1, 2, 3, 4))).conversion13() == SAnd(x,
                                                                  SNot(SMember(-1, 1, 2, 3, 4)))


def t_combo_conversion14():
    # multiple member
    # (or (member 1 2 3) (member 2 3 4 5)) --> (member 1 2 3 4 5)
    # (and (member 1 2 3) (member 2 3 4 5)) --> (member 2 3)
    x = SAtomic(int)
    assert SOr(x, SMember(1, 2, 3), SMember(2, 3, 4, 5)).conversion14() == SOr(x, SMember(1, 2, 3, 4, 5))
    assert SAnd(x, SMember(1, 2, 3), SMember(2, 3, 4, 5)).conversion14() == SAnd(x, SMember(2, 3))


def t_combo_conversion15():
    x = SAtomic(int)
    assert SOr(x, SMember(0, 1, 2, 3), SNot(SMember(2, 3, 4, 5))).conversion15() == SOr(x, SNot(SMember(4, 5)))
    assert SAnd(x, SMember(0, 1, 2, 3), SNot(SMember(2, 3, 4, 5))).conversion15() == SAnd(x, SMember(0, 1))


def t_combo_conversion16():
    assert SAnd(SEql("a"), SAtomic(int)).conversion16() == SAnd(SEmpty, SAtomic(int))
    assert SOr(SEql("a"), SAtomic(int)).conversion16() == SOr(SEql("a"), SAtomic(int))


def t_combo_conversionD1():
    # SOr(SNot(SMember(42, 43, 44, "a","b")), String)
    # == > SNot(SMember(42, 43, 44))
    assert SOr(SNot(SMember(1, 2, 3, "a", "b", "c")), SAtomic(int)).conversionD1() == SNot(SMember("a", "b", "c"))
    
    # to SAnd(SMember(42, 43, 44), SInt)
    # while conversionA1() converts it to
    # SMember(42, 43, 44)
    assert SAnd(SMember(1, 2, 3, "a", "b", "c"), SAtomic(int)).conversionD1() == SMember(1, 2, 3)


def t_combo_conversionD3():
    # find disjoint pair
    assert SAnd(SMember(1, 2), SMember(3, 4)).conversionD3() == SEmpty
    assert SAnd(SMember("a", "b"), SAtomic(int)).conversionD3() == SEmpty
    assert SAnd(SMember(1, 2, "a", "b"), SAtomic(int)).conversionD3() == SAnd(SMember(1, 2, "a", "b"), SAtomic(int))

    assert SOr(SNot(SMember(1, 2)), SNot(SMember(3, 4))).conversionD3() == STop
    assert SOr(SNot(SMember("a", "b")), SNot(SAtomic(int))).conversionD3() == STop
    assert SOr(SNot(SMember(1, 2, "a", "b")), SNot(SAtomic(int))).conversionD3() == \
           SOr(SNot(SMember(1, 2, "a", "b")), SNot(SAtomic(int)))


def t_discovered_cases3():
    class Test1:
        pass

    assert SNot(SAtomic(Test1)).subtypep(SAtomic(int)) is False
    assert SAtomic(int).subtypep(SAtomic(Test1)) is False
    assert SAtomic(Test1).subtypep(SAtomic(int)) is False
    assert SAtomic(int).subtypep(SNot(SAtomic(Test1))) is True
    assert SAtomic(Test1).subtypep(SNot(SAtomic(int))) is True
    assert SNot(SAtomic(int)).subtypep(SAtomic(Test1)) is False
    assert SAnd(SAtomic(int), SNot(SAtomic(Test1))).canonicalize() == SAtomic(int)
    assert SOr(SAtomic(int), SNot(SAtomic(Test1))).canonicalize() == SNot(SAtomic(Test1))


def t_depth_generator():
    from depth_generator import depth_generator
    rand_lambda = depth_generator(2).rand_lambda_str_generator()
    for i in range(10):
        rand_lambda[0](i)
    depth_generator(5).generate_tree()


def t_discovered_cases4():
    assert SNot(SEmpty).canonicalize() == STop
    assert SAtomic(float).disjoint(SEmpty) is True
    assert SAtomic(float).inhabited() is True
    assert SNot(SEmpty).inhabited() is True
    assert SAtomic(float).subtypep(SEmpty) is False
    assert SAtomic(float).disjoint(SNot(SEmpty)) is not True
    assert SAnd(SAtomic(float), SNot(SEmpty)).canonicalize() == SAtomic(float)


def t_canonicalize_cache():
    a = SEql("a")
    td = SOr(a, a, a)
    assert td.canonicalized_hash == {}
    tdc = td.canonicalize()
    assert td.canonicalized_hash[None] == tdc
    assert tdc.canonicalized_hash[None] == tdc

    from genus_types import NormalForm
    tdc2 = td.canonicalize(NormalForm.DNF)
    assert td.canonicalized_hash[NormalForm.DNF] == tdc2
    assert tdc2.canonicalized_hash[NormalForm.DNF] == tdc2

    tdc3 = td.canonicalize(NormalForm.CNF)
    assert td.canonicalized_hash[NormalForm.CNF] == tdc3
    assert tdc3.canonicalized_hash[NormalForm.CNF] == tdc3


#   calling the test functions

t_canonicalize_cache()
t_depth_generator()
t_combo_conversion1()
t_combo_conversionD1()
t_combo_conversionD3()
t_combo_conversion2()
t_combo_conversion3()
t_combo_conversion4()
t_combo_conversion5()
t_combo_conversion6()
t_combo_conversion7()
t_combo_conversion8()
t_combo_conversion9()
t_combo_conversion10()
t_combo_conversion11()
t_combo_conversion12()
t_combo_conversion13()
t_combo_conversion14()
t_combo_conversion15()
t_combo_conversion16()
t_discovered_cases2()
t_discovered_cases3()
t_discovered_cases4()
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

