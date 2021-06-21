import os
def t_verboseonlyprint(s):
    if 'genusverbose' in os.environ and os.environ['genusverbose'] == str(True):
        print(s)

from genus.s_top import STop
from genus.s_empty import SEmpty
def t_STop():
    t_verboseonlyprint("getting the omega singleton from STop")
    a = STop.get_omega()
    t_verboseonlyprint("success")

    #STop has to be unique
    t_verboseonlyprint("checking unicity of omega")
    assert(id(a) == id(STop.get_omega()))
    t_verboseonlyprint("success")

    #STop has to be unique part 2: ensure the constructor throws an error
    t_verboseonlyprint("ensuring constructor throws an error")
    pred = True
    try:
        b = STop()
        pred = False
        assert(False)
    except Exception as e:
        assert(pred)
    t_verboseonlyprint("success")

    #str(a) has to be "Top"
    t_verboseonlyprint("ensuring str(STop.get_omega()) is Top")
    assert(str(a) == "Top")
    t_verboseonlyprint("success")

    #a.typep(t) indicates whether t is a subtype of a, which is always the case by definition
    t_verboseonlyprint("running tests on typep")
    assert(a.typep(object))
    assert(a.typep(a))
    t_verboseonlyprint("success")

    #obviously, a is inhabited as it contains everything by definition
    t_verboseonlyprint("checking that omega is inhabited")
    assert(a._inhabited_down)
    t_verboseonlyprint("success")

    #a is never disjoint with anything but the empty subtype
    t_verboseonlyprint("checking that omega is disjoint only with the empty subtype")
    assert(not a._disjoint_down(object))
    assert(a._disjoint_down(SEmpty.get_epsilon()))
    t_verboseonlyprint("success")

    #on the contrary, a is never a subtype of any type 
    #since types are sets and top is the set that contains all sets
    t_verboseonlyprint("checking that i is a subtype of nothing")
    assert(not a.subtypep(object))
    assert(not a.subtypep(type(a)))

    #my understanding is that the top type is unique so it can't be positively compared to any object
    t_verboseonlyprint("checking that type is uncomparable")
    assert(not a.cmp_to_same_class_obj(a))
    assert(not a.cmp_to_same_class_obj(object))
    t_verboseonlyprint("success")

t_STop()

from genus.s_custom import SCustom
def t_scustom():
    l_odd = lambda x : x % 2 == 1
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
    assert(guinea_pig.subtypep(type(4)) == None)
t_scustom()

from genus.s_and import SAnd
def t_sand():
    quadruple = SCustom(lambda x: x % 4 == 0, "quadruple")
    triple = SCustom(lambda x: x % 3 == 0, "triple")
    
    t_verboseonlyprint("testing SAnd.__init__")
    tri_n_quad = SAnd([triple, quadruple])
    create_tri_n_quad = SAnd.create([triple, quadruple])
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SAnd.__str__")
    assert(str(tri_n_quad) == "[And triple?,quadruple?,]")
    assert(str(create_tri_n_quad) == "[And triple?,quadruple?,]")
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SAnd.typep")
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
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SAnd.subtypep")
    assert(tri_n_quad.subtypep(STop.get_omega()))
    assert(tri_n_quad.subtypep(triple))
    assert(tri_n_quad.subtypep(quadruple))
    assert(tri_n_quad.subtypep(type(5)) == None)
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SAnd.unit")
    assert(SAnd.unit == STop.get_omega())
    t_verboseonlyprint("success")


    t_verboseonlyprint("testing SAnd.zero")
    assert(SAnd.zero == SEmpty.get_epsilon())
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SAnd.same_combination")
    assert(tri_n_quad.same_combination(create_tri_n_quad))
    assert(tri_n_quad.same_combination(SAnd.create([quadruple, triple])))
    
    assert(not tri_n_quad.same_combination(STop.get_omega()))
    assert(not tri_n_quad.same_combination(SAnd.create([])))
    t_verboseonlyprint("success")
t_sand()

from genus.s_or import SOr
def t_sor():
    quadruple = SCustom(lambda x: x % 4 == 0, "quadruple")
    triple = SCustom(lambda x: x % 3 == 0, "triple")
    
    t_verboseonlyprint("testing SOr.__init__")
    tri_o_quad = SOr([triple, quadruple])
    create_tri_o_quad = SOr.create([triple, quadruple])
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SOr.__str__")
    assert(str(tri_o_quad) == "[Or triple?,quadruple?,]")
    assert(str(create_tri_o_quad) == "[Or triple?,quadruple?,]")
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SOr.typep")
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
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SOr.unit")
    assert(SOr.unit == SEmpty.get_epsilon())
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SOr.zero")
    assert(SOr.zero == STop.get_omega())
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SAnd.subtypep")
    assert(tri_o_quad.subtypep(STop.get_omega()))
    assert(tri_o_quad.subtypep(type(5)) == None)
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SOr.same_combination")
    assert(tri_o_quad.same_combination(create_tri_o_quad))
    assert(tri_o_quad.same_combination(SOr.create([quadruple, triple])))

    assert(not tri_o_quad.same_combination(STop.get_omega()))
    assert(not tri_o_quad.same_combination(SOr.create([])))
    t_verboseonlyprint("success")
t_sor()

from genus.s_not import SNot
def t_snot():
    pair = SCustom(lambda x: x & 1 == 0, "pair")
    
    t_verboseonlyprint("SNot: ensuring constructor throws an error")
    pred = True
    try:
        b = SNot([])
        pred = False
        assert(False)
    except Exception as e:
        assert(pred)
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SNot.create")
    npair = SNot.create(pair)
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing that not not foo == foo")
    assert(SNot.create(SNot.create(pair)) == pair)
    t_verboseonlyprint("success")

    t_verboseonlyprint("testing SNot.__str__")
    assert(str(npair) == "[Not pair?]")
    t_verboseonlyprint("success")
    
    t_verboseonlyprint("testing SNot.typep")
    assert(npair.typep(5))
    assert(npair.typep("hello"))
    assert(not npair.typep(4))
    assert(not npair.typep(0))
    t_verboseonlyprint("success")
t_snot()


def t_SimpleTypeD():
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

    child = ChildSTD()

    # _inhabited_down is None to indicate that we actually don't know
    # whether it is as this is the generic version
    assert (child.inhabited() is None)

    # this one is weird. How come we can't detect that it is the same set?
    # anyway, this is how the scala code seems to behave
    # as a reminder: True means yes, False means no, None means maybe
    assert (child._disjoint_down(child) is None)
    assert (child.disjoint(child) is None)

    assert (child == child.to_dnf())
    assert (child == child.to_cnf())

    nf = [NormalForm.DNF, NormalForm.CNF]
    assert (child == child.maybe_dnf(nf))
    assert (child == child.maybe_cnf(nf))

    # fixed_point is just a way to incrementally apply a function on a value
    # until another function deem the delta between two consecutive values to be negligible
    increment = lambda x: x;
    evaluator = lambda x, y: x == y;
    assert (SimpleTypeD.fixed_point(5, increment, evaluator) == 5)
    assert (SimpleTypeD.fixed_point(5, lambda x: x + 1, lambda x, y: x == 6 and y == 7) == 6)

    assert (child == child.canonicalize_once())
    assert (child == child.canonicalize() and child.canonicalized_hash == {None: child})
    # the second time is to make sure it isn't adding the same twice
    assert (child == child.canonicalize() and child.canonicalized_hash == {None: child})

    # ensuring cmp_to_same_class_obj() throws an error
    try:
        child.cmp_to_same_class_obj(child)
        pred = False
        assert (False)
    except:
        assert (pred)


t_SimpleTypeD()


# TODO: move the tests in their own files once this is packaged:
def t_STop():
    a = STop.get_omega()

    # STop has to be unique
    assert (id(a) == id(STop.get_omega()))

    # STop has to be unique part 2: ensure the constructor throws an error
    pred = True
    try:
        b = STop()
        pred = False
        assert (False)
    except Exception as e:
        assert (pred)

    # str(a) has to be "Top"
    assert (str(a) == "Top")

    # a.typep(t) indicates whether t is a subtype of a, which is always the case by definition
    assert (a.typep(object))
    assert (a.typep(a))

    # obviously, a is inhabited as it contains everything by definition
    assert (a._inhabited_down)

    # a is never disjoint with anything but the empty subtype
    assert (not a._disjoint_down(object))
    assert (a._disjoint_down(SEmpty()))

    # on the contrary, a is never a subtype of any type
    # since types are sets and top is the set that contains all sets
    assert (not a.subtypep(object))
    assert (not a.subtypep(type(a)))

    # my understanding is that the top type is unique so it can't be positively compared to any object
    assert (not a.cmp_to_same_class_obj(a))
    assert (not a.cmp_to_same_class_obj(object))


t_STop()
