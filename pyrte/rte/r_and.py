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


from rte.r_combination import Combination
from typing import Literal, List, Any, Optional
from typing_extensions import TypeGuard


class And(Combination):
    from rte.r_rte import Rte
    from genus.simple_type_d import SimpleTypeD

    def __str__(self):
        return "And(" + ", ".join([str(td) for td in self.operands]) + ")"

    def create(self, operands) -> Rte:
        return createAnd(operands)

    def create_dual(self, operands) -> Rte:
        from rte.r_or import createOr
        return createOr(operands)

    def nullable(self) -> bool:
        return all(r.nullable() for r in self.operands)

    def zero(self) -> Literal['EmptySet']:
        from rte.r_emptyset import EmptySet
        return EmptySet

    def one(self) -> Rte:
        from rte.r_constants import sigmaStar
        return sigmaStar

    def same_combination(self, r: Combination) -> TypeGuard['And']:
        return andp(r)

    def dual_combination(self, r: Combination) -> TypeGuard['Or']:
        from rte.r_or import orp
        return orp(r)

    def set_operation(self, a: List[Any], b: List[Any]) -> List[Any]:
        # intersection
        return [x for x in a if x in b]

    def set_dual_operation(self, a: List[Any], b: List[Any]) -> List[Any]:
        # union
        return a + [x for x in b if x not in a]

    def annihilator(self, a: SimpleTypeD, b: SimpleTypeD) -> Optional[bool]:
        return a.subtypep(b)

    def createTypeD(self, operands: List[SimpleTypeD]) -> SimpleTypeD:
        from genus.s_and import createSAnd
        return createSAnd(operands)

    def orInvert(self, x: bool) -> bool:
        return x

    def conversionA7(self) -> Rte:
        from rte.r_epsilon import Epsilon
        from rte.r_emptyset import EmptySet
        if Epsilon in self.operands and self.matches_only_singletons():
            return EmptySet
        else:
            return self

    def matches_only_singletons(self):
        from rte.r_sigma import Sigma
        from rte.r_singleton import singletonp
        return Sigma in self.operands or any(singletonp(r) for r in self.operands)

    def conversionA8(self) -> Rte:
        # if operands contains EmptyWord, then the intersection is either EmptyWord or EmptySet
        from rte.r_epsilon import Epsilon
        from rte.r_emptyset import EmptySet
        if Epsilon not in self.operands:
            return self
        elif all(r.nullable() for r in self.operands):
            return Epsilon
        else:
            return EmptySet

    def conversionA9(self) -> Rte:
        # if x matches only singleton then And(x,y*) -> And(x,y)
        from rte.r_star import starp
        if self.matches_only_singletons() and any(starp(r) for r in self.operands):
            return self.create([rt.operand if starp(rt) else rt for rt in self.operands])
        else:
            return self

    def conversionA10(self) -> Rte:
        # And(A,B,Or(X,Y,Z),C,D)
        # --> Or(And(A,B,   X,   C, D)),
        #        And(A,B,   Y,   C, D)),
        #        And(A,B,   Z,   C, D)))
        from genus.utils import find_first, search_replace
        from rte.r_or import createOr, orp
        ror = find_first(orp, self.operands)
        if ror is None:
            return self
        else:
            return createOr([createAnd(search_replace(self.operands, ror, r)) for r in ror.operands])

    def conversionA13(self) -> Rte:
        # if there is an explicit Sigma and also a singleton which is inhabited, then
        #  we can simply remove the sigma.
        from rte.r_sigma import Sigma
        from rte.r_singleton import singletonp
        from genus.utils import remove_element
        if Sigma in self.operands \
                and any(r.operand.inhabited() is True for r in self.operands if singletonp(r)):
            return self.create(remove_element(self.operands, Sigma))
        else:
            return self

    def conversionD16b(self) -> Rte:
        from rte.r_singleton import singletonp
        from rte.r_not import notp
        from genus.utils import flat_map
        from genus.simple_type_d import SimpleTypeD
        ss: List[SimpleTypeD] = [r.operand for r in self.operands if singletonp(r)]

        def f(r):
            # And(A, x, Not(y)) --> And(A, x) if x, y disjoint
            if notp(r) and singletonp(r.operand) and any(r.operand.operand.disjoint(d) for d in ss):
                return []
            else:
                return [r]

        return self.create(flat_map(f, self.operands))

    def conversionA17(self) -> Rte:
        # if And(...) contains a Cat(...) with at least 2 non-nullable components,
        #    then this Cat matches only sequences of length 2 or more.
        # If And(...) contains a singleton, then it matches only sequences
        #    of length 1, perhaps an empty set of such sequences if the singleton type
        #    is empty.
        # If both are true, then the And() matches EmptySet
        from genus.utils import generate_lazy_val, find_first
        from rte.r_singleton import singletonp
        from rte.r_cat import catp
        from rte.r_sigma import Sigma
        from rte.r_emptyset import EmptySet

        tds = generate_lazy_val(lambda: [r.operand for r in self.operands if singletonp(r)])

        def count_non_nullable(c):
            return sum(1 for r in c.operands if not r.nullable())

        long_cat = generate_lazy_val(lambda: find_first((lambda c: catp(c) and count_non_nullable(c) > 1),
                                                        self.operands,
                                                        False))

        if (Sigma in self.operands or tds()) and long_cat():
            return EmptySet
        else:
            return self

    def conversionA17a(self) -> Rte:
        # if And(...) has more than one Cat(...) which has no nullable operand,
        #    then the number of non-nullables must be the same, else EmptySet.
        from rte.r_cat import catp
        from rte.r_emptyset import EmptySet
        # build a list of cat operands which contain no nullables
        cats = [c.operands
                for c in self.operands
                if catp(c)
                and all(not td.nullable() for td in c.operands)]
        if not cats:
            return self
        elif 1 == len(cats):
            return self
        elif any(len(cats[0]) != len(cats[i]) for i in range(1, len(cats))):
            # we found two Cat(...) of necessarily different lengths
            return EmptySet
        else:
            return self

    def conversionA17a2(self) -> Rte:
        # if And(...) has more than one Cat(...) which has no nullable operand,
        #    We also replace the several Cat(...) (having no nullables)
        #    with a single Cat(...) with intersections of operands.
        #    And(Cat(a,b,c),Cat(x,y,z) ...)
        #    --> And(Cat(And(a,x),And(b,y),And(c,z),...)
        from rte.r_cat import catp, createCat
        from genus.utils import uniquify
        # build a list of cat operands which contain no nullables
        cats = [c.operands
                for c in self.operands
                if catp(c)
                and all(not td.nullable() for td in c.operands)]
        if not cats:
            return self
        elif 1 == len(cats):
            return self
        elif any(len(cats[0]) != len(cats[i]) for i in range(1, len(cats))):
            # we found two Cat(...) of necessarily different lengths
            return self
        else:
            invert = [[c[i] for c in cats] for i in range(0, len(cats[0]))]
            cat = createCat([self.create(r) for r in invert])
            return self.create(uniquify([cat if catp(r) and r.operands in cats else r for r in self.operands]))

    def conversionA17b(self) -> Rte:
        # after 17a we know that if there are multiple Cats(...) without a nullable,
        #   then all such Cats(...) without a nullable have same number of operands
        #   have been merged into one Cat(...)
        #   So assure that all other Cats have no more non-nullable operands.
        from rte.r_cat import catp
        from rte.r_emptyset import EmptySet
        from genus.utils import find_first
        cats = [r for r in self.operands if catp(r)]
        non_nullable_cat = find_first(lambda c: all(not o.nullable() for o in c.operands),
                                      cats,
                                      None)
        if non_nullable_cat is None:
            return self
        else:
            num_non_nullable = len(non_nullable_cat.operands)

            def count_non_nullable(c):
                return sum(1 for o in c.operands if not o.nullable())

            for c in cats:
                if count_non_nullable(c) > num_non_nullable:
                    return EmptySet
            return self

    def conversionA17c(self) -> Rte:
        # if And(...) contains a Cat with no nullables, (or explicit Sigma or Singleton)
        #  then remove the nullables from ever other Cat with that many non-nullables,
        # Since 7b has run, there should be no cat with more than this many non-nullables
        # find a Cat(...) with no nullables, there should be at most one because
        #    conversion17a as run.
        from rte.r_cat import catp, createCat
        from rte.r_sigma import Sigma
        from rte.r_singleton import singletonp
        from genus.utils import generate_lazy_val, find_first

        def count_non_nullable(c):
            return sum(1 for r in c.operands if not r.nullable())

        cat_non_nullable = generate_lazy_val(lambda: next((c for c in self.operands
                                                           if catp(c)
                                                           and all(not o.nullable() for o in c.operands)),
                                                          None))
        if find_first(catp, self.operands, None) is None:
            return self
        if Sigma in self.operands:
            num_non_nullables = 1
        elif any(singletonp(r) for r in self.operands):
            num_non_nullables = 1
        elif cat_non_nullable() is not None:
            num_non_nullables = len(cat_non_nullable().operands)
        else:
            return self

        def f(c):
            if not catp(c):
                return c
            elif count_non_nullable(c) == num_non_nullables:
                # remove nullables.
                return createCat([o for o in c.operands if not o.nullable()])
            else:
                return c

        return self.create([f(r) for r in self.operands])

    def conversionA18(self) -> Rte:
        # if there is a singleton which is not inhabited
        from rte.r_singleton import singletonp
        from rte.r_emptyset import EmptySet
        if any(r.operand.inhabited() is False for r in self.operands if singletonp(r)):
            return EmptySet
        else:
            return self

    def conversionA19(self) -> Rte:
        # if there is at least one singleton and zero or more Not(x) where x is a singleton
        #   then build a SimpleTypeD and ask whether it is inhabited.
        #   if it is not inhabited, then self converts to EmptySet
        from genus.s_and import createSAnd
        from genus.s_not import SNot
        from genus.genus_types import NormalForm
        from rte.r_singleton import singletonp
        from rte.r_not import notp
        from rte.r_emptyset import EmptySet
        singletons = [r.operand for r in self.operands if singletonp(r)]
        if not singletons:
            return self
        else:
            not_singletons = [SNot(r.operand.operand) for r in self.operands if notp(r) and singletonp(r.operand)]
            canonicalized_singletons = createSAnd(singletons + not_singletons).canonicalize(NormalForm.DNF)
            if canonicalized_singletons.inhabited() is False:
                return EmptySet
            else:
                return self

    # the naming convention of the conversion functions is as follows:
    #   conversionC... -- a method on Combination
    #   conversionA... -- a method on And
    #   conversionO... -- a method on Or
    #   conversionD... -- a method declared in Combination but implemented in And and Or in a dual way
    #                          I.e. the And and Or methods of this name implement dual operations.

    def canonicalize_once(self) -> Rte:
        from genus.utils import find_simplifier
        return find_simplifier(self, [self.conversionC1,
                                      self.conversionC3,
                                      self.conversionC4,
                                      self.conversionC6,
                                      self.conversionA7,
                                      self.conversionC7,
                                      self.conversionA8,
                                      self.conversionA9,
                                      self.conversionA10,
                                      self.conversionC11,
                                      self.conversionC14,
                                      self.conversionA18,
                                      self.conversionC12,
                                      self.conversionA13,
                                      self.conversionC21,
                                      self.conversionC15,
                                      self.conversionC16,
                                      self.conversionD16b,
                                      self.conversionA17,
                                      self.conversionA17a,
                                      self.conversionA17a2,
                                      self.conversionA17b,
                                      self.conversionA17c,
                                      self.conversionA19,
                                      self.conversionC17,
                                      self.conversionC99,
                                      self.conversionC5,
                                      lambda: super(And, self).canonicalize_once()])


def createAnd(operands: List['Rte']) -> 'Rte':
    from rte.r_constants import sigmaStar

    if not operands:
        return sigmaStar
    elif len(operands) == 1:
        return operands[0]
    else:
        return And(*operands)


def andp(op: 'Rte') -> TypeGuard[And]:
    return isinstance(op, And)
