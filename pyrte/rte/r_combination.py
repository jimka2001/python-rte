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


from rte.r_rte import Rte


class Combination (Rte):
    def __init__(self, *operands):
        self.operands = list(operands)
        assert all(isinstance(operand, Rte) for operand in operands), \
                f"And and Or expect Rtes as arguments, got {[type(o) for o in operands]}"
        super().__init__()

    def __eq__(self, that):
        return type(self) is type(that) and \
               self.operands == that.operands

    def __hash__(self):
        return hash(tuple(self.operands))

    def create(self, operands):
        raise Exception(f"create not implemented for {type(self)}")

    def cmp_to_same_class_obj(self, t):
        from genus.utils import compare_sequence
        return compare_sequence(self.operands, t.operands)

    def first_types(self):
        import functools
        return functools.reduce(lambda acc, tds: acc.union(tds),
                                [td.first_types() for td in self.operands],
                                super().first_types())

    def one(self):
        raise Exception(f"one not implemented for {type(self)}")

    def zero(self):
        raise Exception(f"zero not implemented for {type(self)}")

    def same_combination(self, r):
        raise Exception(f"same_combination not implemented for {type(self)}")

    def dual_combination(self, r):
        raise Exception(f"dual_combination not implemented for {type(self)}")

    def set_operation(self, a, b):
        raise Exception(f"set_operation not implemented for {type(self)}")

    def set_dual_operation(self, a, b):
        raise Exception(f"set_dual_operation not implemented for {type(self)}")

    def annihilator(self, a, b):
        raise Exception(f"annihilator not implemented for {type(self)}")

    def createTypeD(self, operands):
        raise Exception(f"createTypeD not implemented for {type(self)}")

    def orInvert(self, x):
        raise Exception(f"orInvert not implemented for {type(self)}")

    def conversionC1(self):
        return self.create(self.operands)

    def conversionC3(self):
        # Or(... Sigma * ....) -> Sigma *
        # And(... EmptySet....) -> EmptySet
        if self.zero() in self.operands:
            return self.zero()
        else:
            return self

    def conversionC4(self):
        from genus.utils import uniquify
        return self.create(uniquify(self.operands))

    def conversionC5(self):
        from genus.utils import cmp_objects
        import functools

        ordered = sorted(self.operands, key=functools.cmp_to_key(cmp_objects))
        return self.create(ordered)

    def conversionC6(self):
        # remove Sigma * and flatten And(And(...)...)
        # remove EmptySet and flatten Or(Or(...)...)
        from genus.utils import flat_map

        def f(r):
            if r == self.one():
                return []
            elif self.same_combination(r):
                return r.operands
            else:
                return [r]

        return self.create(flat_map(f, self.operands))

    def conversionC7(self):
        # (:or A B (:* B) C)
        # --> (:or A (:* B) C)
        # (:and A B (:* B) C)
        # --> (:and A B C)
        from genus.utils import flat_map
        from rte.r_star import starp, Star
        from rte.r_or import orp
        from rte.r_and import andp
        stars = [op for op in self.operands if starp(op)]
        if not stars:
            return self
        else:
            def f(r):
                if orp(self) and Star(r) in stars:
                    return []
                elif starp(r) and andp(self) and r.operand in self.operands:
                    return []
                else:
                    return [r]

            return self.create(flat_map(f, self.operands))

    def conversionC11(self):
        # And(...,x,Not(x)...) --> EmptySet
        # Or(...x,Not(x)...) --> SigmaStar
        from rte.r_not import notp
        if any(r1 for r1 in self.operands if notp(r1) and r1.operand in self.operands):
            return self.zero()
        else:
            return self

    def conversionC14(self):
        # generalization of conversionC11
        # Or(A,Not(B),X) -> Sigma* if B is subtype of A
        # And(A,Not(B),X) -> EmptySet if A is subtype of B
        from rte.r_not import notp
        from rte.r_singleton import singletonp
        nots = [r.operand.operand for r in self.operands if notp(r) and singletonp(r.operand)]
        singletons = [r.operand for r in self.operands if singletonp(r)]
        if any(self.annihilator(sup, sub) is True for sub in nots for sup in singletons):
            return self.zero()
        else:
            return self

    def conversionC12(self):
        # sigmaSigmaStarSigma = Cat(Sigma, Sigma, sigmaStar)
        # Or(   A, B, ... Cat(Sigma,Sigma,Sigma*) ... Not(Singleton(X)) ...)
        #   --> Or( A, B, ... Not(Singleton(X))
        # This is correct because Cat(Σ,Σ,(Σ)*) is the set of all sequences of length 2 or more
        #    and Not(Singleton(X)) includes the set of all sequences of length 2 or more
        # Similarly, any Cat(...) which contains at least two non-nullables is either the
        #    empty set, or a set of sequences each of length 2 or more.
        #    And Not(Singleton(X)) contains all all sequences of length 2 or more.
        # So se can remove all such sequences.
        # E.g. Or(Singleton(SEql(1)),
        #         Cat(Singleton(SEql(1)),Singleton(SEql(2)),Singleton(SEql(3))),
        #         Not(Singleton(SEql(0))))
        #     we can remove Cat(...) because it contains at least 2 non-nullable items,
        #         and is therefore a subset of Not(Singleton(SEql(0)))
        # If we have  Or rather than And, then we can remove Not(Singleton(SEql(0)))
        #         because it is a superset of Cat(...)
        from genus.utils import generate_lazy_val
        from rte.r_or import orp
        from rte.r_and import andp
        from rte.r_cat import catp
        from rte.r_not import notp
        from rte.r_singleton import singletonp
        cats = generate_lazy_val(lambda: [c for c in self.operands if catp(c)
                                          and sum(1 for op in c.operands if not op.nullable()) > 1])
        not_sing = [n for n in self.operands if notp(n) and singletonp(n.operand)]

        if not not_sing or not cats():
            return self
        elif orp(self):
            return self.create([op for op in self.operands if op not in cats()])
        elif andp(self):
            return self.create([op for op in self.operands if op not in not_sing])
        else:
            raise Exception(f"expecting Or or And, got {self}")

    def conversionC15(self):
        # simplify to maximum of one SMember(...) and maximum of one Not(SMember(...))
        # Or(<{1,2,3,4}>,<{4,5,6,7}>,Not(<{10,11,12,13}>,Not(<{12,13,14,15}>)))
        #   --> Or(<{1,2,3,4,6,7}>,Not(<{12,13}>))
        #
        # And(<{1,2,3,4}>,<{3,4,5,6,7}>,Not(<{10,11,12,13}>,Not(<{12,13,14,15}>)))
        #   --> And(<{3,4}>,Not(<{10,11,12,13,14,15}>))
        from rte.r_singleton import singletonp, Singleton
        from rte.r_not import notp, Not
        from genus.s_member import memberimplp, createSMember
        from genus.utils import uniquify
        import functools
        members = [sm for sm in self.operands if singletonp(sm)
                   and memberimplp(sm.operand)]
        not_members = [nsm for nsm in self.operands if notp(nsm)
                       and singletonp(nsm.operand)
                       and memberimplp(nsm.operand.operand)]
        if len(members) <= 1 and len(not_members) <= 1:
            return self
        # find union/intersection of Singleton(SMember(...))  arglists
        new_member_arglist = functools.reduce(self.set_operation,
                                              [sm.operand.arglist for sm in members],
                                              members[0].operand.arglist) if members else None
        new_member = Singleton(createSMember(new_member_arglist)) if new_member_arglist \
            else self.one()
        # find union/intersection of Not(Singleton(SMember(...))) arglists
        new_not_member_arglist = functools.reduce(self.set_dual_operation,
                                                  [nsm.operand.operand.arglist for nsm in not_members],
                                                  not_members[0].operand.operand.arglist) if not_members else None
        new_not_member = Not(Singleton(createSMember(new_not_member_arglist))) if new_not_member_arglist \
            else self.one()

        def f(op):
            if op in members:
                return new_member
            elif op in not_members:
                return new_not_member
            else:
                return op

        return self.create(uniquify([f(op) for op in self.operands]))

    def conversionC16(self):
        # WARNING, this function assumes there are no repeated elements
        #     according to ==
        #     If there are repeated elements, both will be removed.

        # remove And superclasses
        # remove Or subclasses

        # Must be careful, e.g. if Or(A,B) with A a subset of B and B a subset of A
        #    but A != B, then don't remove both.
        from rte.r_singleton import singletonp
        from genus.utils import flat_map
        ss = [op.operand for op in self.operands if singletonp(op)]

        def f(i):  # index into ss
            td = ss[i]
            right = [td] if any(self.annihilator(ss[j], td) is True for j in range(i + 1, len(ss))) else []
            if right:
                return right
            else:
                left = [ss[j] for j in range(i + 1, len(ss)) if self.annihilator(td, ss[j]) is True]
                return left

        redundant = flat_map(f, range(len(ss)-1))

        def g(op):
            if singletonp(op) and op.operand in redundant:
                return []
            else:
                return [op]

        # And(super,sub,...) --> And(sub,...)
        # Or(super,sub,...) --> Or(super,...)
        filtered = flat_map(g, self.operands)

        return self.create(filtered)

    def conversionD16b(self):
        raise Exception(f"conversionC16b not implemented for {type(self)}")

    def conversionC17(self):
        # And({1,2,3},Singleton(X),Not(Singleton(Y)))
        #  {...} selecting elements, x, for which SAnd(X,SNot(Y)).typep(x) is true
        # --> And({...},Singleton(X),Not(Singleton(Y)))

        # Or({1,2,3},Singleton(X),Not(Singleton(Y)))
        #  {...} deleting elements, x, for which SOr(X,SNot(Y)).typep(x) is true
        # --> Or({...},Singleton(X),Not(Singleton(Y)))
        from genus.utils import find_first, remove_element, flat_map, search_replace
        from genus.s_member import memberimplp, createSMember
        from genus.s_not import SNot
        from rte.r_singleton import singletonp, Singleton
        from rte.r_not import notp
        singleton = find_first(lambda op: singletonp(op) and memberimplp(op.operand),
                               self.operands)
        if singleton is None:
            return self
        member = singleton.operand
        singletons = [r for r in remove_element(self.operands, singleton)
                      if singletonp(r) or (notp(r) and singletonp(r.operand))]

        def f(r):
            if singletonp(r):
                return [r.operand]
            elif notp(r) and singletonp(r.operand):
                return [SNot(r.operand.operand)]
            else:
                return []

        looser = flat_map(f, singletons)

        if not looser:
            return self
        td = self.createTypeD(looser)
        rt = Singleton(createSMember([a for a in member.arglist if self.orInvert(td.typep(a))]))
        return self.create(search_replace(self.operands, singleton, rt))

    def conversionC21(self):
        from genus.utils import flat_map
        from rte.r_and import andp
        from rte.r_or import orp
        from rte.r_singleton import singletonp
        from rte.r_not import notp

        def f(r):
            if andp(self) and singletonp(r):
                return [r.operand]
            elif orp(self) and notp(r) and singletonp(r.operand):
                return [r.operand.operand]
            else:
                return []
        singletons = flat_map(f, self.operands)
        if any(singletons[i].disjoint(singletons[j]) is True
               for i in range(len(singletons))
               for j in range(i+1, len(singletons))):
            return self.zero()
        else:
            return self

    def conversionC99(self):
        return self.create([r.canonicalize_once() for r in self.operands])

    def derivative_down(self, wrt, factors, disjoints):
        return self.create([ob.derivative(wrt, factors, disjoints) for ob in self.operands])
