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
def t_verboseonlyprint(s):
    if 'genusverbose' in os.environ and os.environ['genusverbose'] == str(True):
        print(s)


from s_not import SNot
from s_or import SOr
from s_top import STop
from s_empty import SEmpty
from simple_type_d import SimpleTypeD
from s_atomic import SAtomic
from s_custom import SCustom
from s_and import SAnd

def t_fixed_point():
    from utils import fixed_point
    assert fixed_point(0, (lambda x: x), (lambda x,y: x == y)) == 0
    assert fixed_point(0, (lambda x: x//2), (lambda x,y: x == y)) == 0

def t_STop():
    from s_empty import SEmptyImpl
    from s_top import STopImpl

    a = STop

    #STop has to be unique
    assert(id(a) == id(STopImpl.get_omega()))

    #STop has to be unique part 2: ensure the constructor throws an error
    pred = True
    try:
        b = STop()
        pred = False
        assert(False)
    except Exception as e:
        assert(pred)

    #str(a) has to be "Top"
    assert(str(a) == "Top")

    #a.typep(t) indicates whether t is a subtype of a, which is always the case by definition
    assert(a.typep(SAtomic(object)))
    assert(a.typep(a))

    #obviously, a is inhabited as it contains everything by definition
    assert(a._inhabited_down)

    #a is never disjoint with anything but the empty subtype
    assert(not a._disjoint_down(SAtomic(object)))
    assert(a._disjoint_down(SEmptyImpl.get_epsilon()))

    #on the contrary, a is never a subtype of any type 
    #since types are sets and top is the set that contains all sets
    assert(a.subtypep(SAtomic(object)) is True)
    assert( a.subtypep(a) is True)

    #my understanding is that the top type is unique so it can't be positively compared to any object
    assert(not a.cmp_to_same_class_obj(a))
    assert(not a.cmp_to_same_class_obj(object))


def t_scustom():
    l_odd = lambda x : isinstance(x,int) and x % 2 == 1
    guinea_pig = SCustom(l_odd, "[odd numbers]")
    assert(guinea_pig.f == l_odd)
    assert(guinea_pig.printable == "[odd numbers]")
    assert( str(guinea_pig) == "[odd numbers]?")
    for x in range(-100,100):
        if x % 2 == 1:
            assert(guinea_pig.typep(x))
        else:
            assert(not guinea_pig.typep(x))
    assert(not guinea_pig.typep("hello"))
    assert(guinea_pig.subtypep(SAtomic(type(4))) is None)

def t_sand1():
    from genus_types import createSAnd
    quadruple = SCustom((lambda x: x % 4 == 0), "quadruple")

    triple = SCustom(lambda x: isinstance(x,int) and (x % 3 == 0), "triple")
    
    tri_n_quad = SAnd([triple, quadruple])
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

    tri_n_quad = SAnd([triple, quadruple])
    create_tri_n_quad = createSAnd([triple, quadruple])
    assert(tri_n_quad.subtypep(STop))
    assert(tri_n_quad.subtypep(triple))

    assert(tri_n_quad.subtypep(quadruple))
    assert tri_n_quad.subtypep(SAtomic(type(5))) == None, "%s != None" % tri_n_quad.subtypep(SAtomic(type(5)))

    assert(SAnd.unit == STop)
    assert(SAnd.zero == SEmpty)

    assert(tri_n_quad.same_combination(create_tri_n_quad))
    assert(tri_n_quad.same_combination(createSAnd([quadruple, triple])))

    assert(not tri_n_quad.same_combination(STop))
    assert(not tri_n_quad.same_combination(createSAnd([])))

def t_sor():
    from genus_types import createSOr
    quadruple = SCustom(lambda x: isinstance(x,int) and x % 4 == 0, "quadruple")
    triple = SCustom(lambda x: isinstance(x,int) and x % 3 == 0, "triple")
    
    tri_o_quad = SOr([triple, quadruple])
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

    assert(SOr.unit == SEmpty.get_epsilon())

    assert(SOr.zero == STop.get_omega())

    assert(tri_o_quad.subtypep(STop.get_omega()))
    assert(tri_o_quad.subtypep(SAtomic(type(5))) == None)

    assert(tri_o_quad.same_combination(create_tri_o_quad))
    assert(tri_o_quad.same_combination(createSOr([quadruple, triple])))

    assert(not tri_o_quad.same_combination(STop.get_omega()))
    assert(not tri_o_quad.same_combination(createSOr([])))

def t_snot():
    pair = SCustom(lambda x: isinstance(x,int) and x & 1 == 0, "pair")
    
    pred = True
    try:
        b = SNot([])
        pred = False
        assert(False)
    except Exception as e:
        assert(pred)

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
        foo = SimpleTypeD()
        pred = False
        assert (False)
    except:
        assert (pred)

    # ensuring typep is an abstract method
    try:
        class ChildSTDNoTypep(SimpleTypeD):
            """just for testing"""

            def __init__(self):
                super(ChildSTDNoTypep, self).__init__()

        foo = ChildSTDNoTypep()
        del ChildSTDNoTypep
        pred = False
        assert (False)
    except:
        assert (pred)

    class ChildSTD(SimpleTypeD):
        """docstring for ChildSTD"""

        def __init__(self):
            super(ChildSTD, self).__init__()

        def typep(a):
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
    increment = lambda x: x
    evaluator = lambda x, y: x == y
    assert (fixed_point(5, increment, evaluator) == 5)
    assert (fixed_point(5, lambda x: x + 1, lambda x, y: x == 6 and y == 7) == 6)

    assert (child == child.canonicalize_once())
    assert (child == child.canonicalize() and child.canonicalized_hash == {None: child})
    # the second time is to make sure it isn't adding the same twice
    assert (child == child.canonicalize() and child.canonicalized_hash == {None: child})

    # ensuring cmp_to_same_class_obj() throws no error
    assert child.cmp_to_same_class_obj(child) == False


# TODO: move the tests in their own files once this is packaged:
def t_STop2():
    from s_top import STopImpl
    # STop has to be unique
    assert (id(STop) == id(STopImpl.get_omega()))

    # STop has to be unique part 2: ensure the constructor throws an error
    pred = True
    try:
        b = STop()
        pred = False
        assert (False)
    except Exception as e:
        assert (pred)

    # str(a) has to be "Top"
    assert (str(STop) == "Top")

    # a.subtypep(t) indicates whether t is a subtype of a, which is always the case by definition
    assert (STop.subtypep(SAtomic(object)))
    assert (STop.subtypep(STop))

    # obviously, a is inhabited as it contains everything by definition
    assert (STop._inhabited_down)

    # a is never disjoint with anything but the empty subtype
    assert (not STop._disjoint_down(SAtomic(object)))
    assert (STop._disjoint_down(SEmpty))

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
        b = SEmpty()
        pred = False
        assert (False)
    except Exception as e:
        assert (pred)

    # str(a) has to be "Empty"
    assert (str(SEmpty) == "Empty")

    # a.typep(t) indicates whether t is a subtype of a, which is never the case
    assert (not SEmpty.typep(SAtomic(object)))
    assert (SEmpty.subtypep(SEmpty))

    # obviously, a is not inhabited as it is by definition empty
    assert (not SEmpty._inhabited_down())

    # a is disjoint with anything as it is empty
    assert (SEmpty._disjoint_down(SAtomic(object)))

    # on the contrary, a is always a subtype of any type
    # since types are sets and the empty set is a subset of all sets
    assert (SEmpty.subtypep(SAtomic(object)) is True)
    assert (SEmpty.subtypep(SEmpty) is True)

    # my understanding is that the empty type is unique so it can't be positively compared to any object
    assert (not SEmpty.cmp_to_same_class_obj(SEmpty))
    assert (not SEmpty.cmp_to_same_class_obj(SAtomic(object)))


def t_scustom2():
    def l_odd(x):
        return isinstance(x,int) and x % 2 == 1
    guinea_pig = SCustom(l_odd, "[odd numbers]")
    assert(guinea_pig.f == l_odd)
    assert(guinea_pig.printable == "[odd numbers]")
    assert( str(guinea_pig) == "[odd numbers]?")
    for x in range(-100,100):
        if x % 2 == 1:
            assert guinea_pig.typep(x)
        else:
            assert not guinea_pig.typep(x)



#   calling the test functions

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

