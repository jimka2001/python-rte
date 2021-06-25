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

from abc import ABCMeta, abstractmethod
from simple_type_d import SimpleTypeD
from s_not import SNot
from utils import find_simplifier

"""
[0-3] Advancement tracker

__init__ 1
create 1
unit 1
zero 1
annihilator 1
same_combination 1
canonicalize_once 1
cmp_to_same_class 0
"""


class SCombination(SimpleTypeD):
    """SCombination is abstract because it has at least one abstractmethod and inherits from an abstract class"""

    def __init__(self, tds):
        self.tds = list(tds)
        assert all(isinstance(td, SimpleTypeD) for td in tds)
        super().__init__()

    @abstractmethod
    def create(self, tds):
        pass

    def __eq__(self, that):
        return type(self) is type(that) \
               and self.tds == that.tds

    def __hash__(self):
        return hash(tuple(self.tds))

    @property
    @abstractmethod
    def unit(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def zero(self):
        raise NotImplementedError

    @abstractmethod
    def annihilator(self, a, b):
        # apparently this name may change, so keep track of it
        raise NotImplementedError

    def same_combination(self, td):
        return type(self) == type(td)

    def dual_combination(self, td):
        raise NotImplementedError

    def combo_filter(self, pred, xs):
        raise NotImplementedError

    def combinator(self, a, b):
        raise NotImplementedError

    def dual_combinator(self, a, b):
        raise NotImplementedError

    def create_dual(self, tds):
        raise NotImplementedError

    def conversion1(self):
        # (and) -> STop, unit = STop, zero = SEmpty
        # (or) -> SEmpty, unit = SEmpty, zero = STop
        if not self.tds:  # tds == []
            return self.unit()
        elif len(self.tds) == 1:
            return self.tds[0]
        else:
            return self

    def conversion2(self):
        # (and A B SEmpty C D)-> SEmpty, unit = STop, zero = SEmpty
        # (or A B STop C D) -> STop, unit = SEmpty, zero = STop
        if self.zero() in self.tds:
            return self.zero()
        else:
            return self

    def conversion3(self):
        # (and A ( not A)) --> SEmpty, unit = STop, zero = SEmpty
        # (or A ( not A)) --> STop, unit = SEmpty, zero = STop
        if any(SNot(td) in self.tds for td in self.tds):
            return self.zero()
        else:
            return self

    def conversion4(self):
        # SAnd(A, STop, B) == > SAnd(A, B), unit = STop, zero = SEmpty
        # SOr(A, SEmpty, B) == > SOr(A, B), unit = SEmpty, zero = STop
        if self.unit() in self.tds:
            return self.create([td for td in self.tds if td is not self.unit()])
        else:
            return self

    def conversion5(self):
        # (and A B A C) -> (and A B C)
        # (or A B A C) -> (or A B C)
        from utils import uniquify
        return self.create(uniquify(self.tds))

    def conversion6(self):
        # (and A ( and B C) D) --> (and A B C D)
        # (or A ( or B C) D) --> (or A B C D)
        if not any(self.same_combination(td) for td in self.tds):
            return self
        else:
            from genus_types import combop
            from utils import flat_map

            def f(td):
                if not combop(td):
                    return [td]
                elif self.same_combination(td):
                    return td.tds
                else:
                    return [td]

            return self.create(flat_map(f, self.tds))

    def conversion7(self, nf):
        import functools
        from genus_types import cmp_type_designators
        ordered = sorted(self.tds, key=functools.cmp_to_key(cmp_type_designators))
        return self.create(ordered).maybe_dnf(nf).maybe_cnf(nf)

    def conversion8(self):
        # (or A (not B)) --> STop if B is subtype of A, zero = STop
        # (and A (not B)) --> SEmpty if B is supertype of A, zero = SEmpty
        from genus_types import notp
        for a in self.tds:
            for n in self.tds:
                if notp(n) and self.annihilator(a, n.s):
                    return self.zero()
        return self

    def conversion9(self):
        # (A + B + C)(A + !B + C)(X) -> (A + B + C)(A + C)(X)
        # (A + B +!C)(A +!B + C)(A +!B+!C) -> (A + B +!C)(A +!B + C)(A +!C)
        # (A + B +!C)(A +!B + C)(A +!B+!C) -> does not reduce to(A + B +!C)(A +!B+C)(A)
        from genus_types import combop, notp
        from utils import search_replace, remove_element, find_first
        combos = list(filter(combop, self.tds))
        duals = list(filter(lambda td: self.dual_combination(td), combos))

        def f(td):
            if td not in duals:
                return td
            else:
                # A + !B + C -> A + C
                # A + B + C -> A + B + C
                # X -> X
                def pred(n):
                    return notp(n) and any(d.tds == search_replace(td.tds, n, n.s) for d in duals)

                # find to_remove=!B such that (A+!B+C) and also (A+B+C) are in the arglist
                to_remove = find_first(pred, td.tds)
                if to_remove is not None:
                    # if we found such a !B, then return (A+C)
                    return td.create(remove_element(td.tds, to_remove))
                else:
                    return td

        # if the arglist contains both (A+!B+C) and (A+B+C)
        #    then replace (A+!B+C) with (A+C) in the arglist
        newargs = [f(td) for td in self.tds]
        return self.create(newargs)

    def conversion10(self):
        # (and A B C) --> (and A C) if A is subtype of B
        # (or A B C) -->  (or B C) if A is subtype of B
        from utils import find_first

        def pred(sub):
            return any(sub != sup and self.annihilator(sub, sup) is True for sup in self.tds)

        sub = find_first(pred, self.tds)
        if sub is None:
            return self
        else:
            # for SAnd
            #   throw away all proper superclasses of sub, i.e., keep everything that is not
            #   a superclass of sub and also keep sub itself.  keep false and dont-know
            # for SOr
            #   throw away all proper subclasses of sub, i.e., keep everything that is not
            #   a subclass of sub and also keep sub itself.  keep false and dont-know
            keep = [sup for sup in self.tds if sup == sub or not self.annihilator(sub, sup) is True]
            return self.create(keep)

    def conversion11(self):
        # A + !A B -> A + B
        # A + !A BX + Y = (A + BX + Y)
        # A + ABX + Y = (A + Y)
        from utils import find_first, flat_map, remove_element
        from genus_types import combop
        combos = list(filter(combop, self.tds))
        duals = list(filter(self.dual_combination, combos))

        def pred(a):
            n = SNot(a)
            return any(td for td in duals
                       if (a in td.tds or n in td.tds))

        ao = find_first(pred, self.tds)
        if ao is None:
            return self
        else:
            def consume(td):
                if not combop(td):
                    return [td]
                elif self.same_combination(td):
                    return [td]
                elif ao in td.tds:
                    return []  # (A + ABX + Y) --> (A + Y)
                elif SNot(ao) in td.tds:
                    # td is a dual, so td.create creates a dual
                    # (A + !ABX + Y) --> (A + BX + Y)
                    return [td.create(remove_element(td.tds, SNot(ao)))]
                else:
                    return [td]

            return self.create(flat_map(consume, self.tds))

    def conversion12(self):
        # AXBC + !X = ABC + !X
        # find !X
        from genus_types import combop, notp
        from utils import remove_element
        combos = filter(combop, self.tds)
        duals = filter(lambda td: self.dual_combination(td), combos)
        comp = next((n for n in self.tds if notp(n) and any(td for td in duals if n.s in td.tds)),
                    None)
        if comp is None:
            return self
        else:
            def f(td):
                if not combop(td):
                    return td
                elif not self.dual_combination(td):
                    return td
                else:
                    # td is a dual so td.create() creates a dual
                    # convert AXBC -> ABC by removing X because we found !X elsewhere
                    return td.create(remove_element(td.tds, comp.s))
            return self.create([f(td) for td in self.tds])

    def conversion13(self):
        # multiple !member
        # SOr(x,!{-1, 1},!{1, 2, 3, 4})
        # --> SOr(x,!{1}) // intersection of non-member
        # SAnd(x,!{-1, 1},!{1, 2, 3, 4})
        # --> SOr(x,!{-1, 1, 2, 3, 4}) // union of non-member
        from genus_types import notp, memberimplp, createSMember
        from utils import uniquify
        not_members = [td for td in self.tds if notp(td) and memberimplp(td.s)]
        if len(not_members) <= 1:
            return self
        else:
            import functools
            # find all the items in all the SNot(SMember(...)) elements
            #    this is a list of lists
            items = [n.s.arglist for n in not_members]
            # flatten the list of lists into a single list, either by
            #   union or intersection depending on SOr or SAnd
            combined = functools.reduce(lambda x, y: self.dual_combinator(x, y),
                                        items)
            new_not_member = SNot(createSMember(combined))

            def f(td):
                if td in not_members:
                    return new_not_member
                else:
                    return td
            # we replace all SNot(SMember(...)) with the newly computed
            #  SNot(SMember(...)), the remove duplicates.  This effectively
            #  replaces the right-most one, and removes all others.
            return self.create(uniquify([f(td) for td in self.tds]))

    def conversion14(self):
        # multiple member
        # (or (member 1 2 3) (member 2 3 4 5)) --> (member 1 2 3 4 5)
        # (or String (member 1 2 "3") (member 2 3 4 "5")) --> (or String (member 1 2 4))
        # (and (member 1 2 3) (member 2 3 4 5)) --> (member 2 3)
        from genus_types import memberimplp, createSMember
        import functools
        from utils import uniquify

        members = [td for td in self.tds if memberimplp(td)]
        if len(members) <= 1:
            return self
        else:
            items = [m.arglist for m in members]
            combined = functools.reduce(lambda x, y: self.combinator(x, y),
                                        items)
            new_member = createSMember(combined)

            def f(td):
                if td in members:
                    return new_member
                else:
                    return td

            return self.create(uniquify([f(td) for td in self.tds]))

    def conversion15(self):
        # SAnd(X, member, not-member)
        # SOr(X, member, not-member)
        # after conversion13 and conversion14 there is a maximum of one SMember(...) and
        # a maximum of one SNot(SMember(...))
        from utils import find_first, flat_map
        from genus_types import memberimplp, notp, andp, orp, createSMember

        def diff(xs, ys):
            return [x for x in xs if x not in ys]

        member = find_first(memberimplp, self.tds, None)
        not_member = find_first(lambda x: notp(x) and memberimplp(x.s), self.tds, None)
        if member is None:
            return self
        elif not_member is None:
            return self
        # so we have a member and a not_member
        else:
            def f(td):
                if andp(self) and td == not_member:
                    return []
                elif orp(self) and td == member:
                    return []
                elif andp(self) and td == member:
                    return [createSMember(diff(member.arglist, not_member.s.arglist))]
                elif orp(self) and td == not_member:
                    return [SNot(createSMember(diff(not_member.s.arglist, member.arglist)))]
                else:
                    return [td]
            return self.create(flat_map(f, self.tds))

    def conversion16(self):
        # Now(after conversions 13, 14, and 15, there is at most one SMember(...) and
        # at most one SNot(SMember(...))

        # (and Double (not (member 1.0 2.0 "a" "b"))) --> (and Double (not (member 1.0 2.0)))
        from genus_types import memberimplp, notp, createSMember
        fewer = [td for td in self.tds
                 if not memberimplp(td)
                 and not (notp(td) and memberimplp(td.s))]
        stricter = self.create(fewer)

        def f(td):
            if memberimplp(td):
                return createSMember(list(self.combo_filter(stricter.typep, td.arglist)))
            elif notp(td) and memberimplp(td.s):
                return SNot(createSMember(list(self.combo_filter(stricter.typep, td.s.arglist))))
            else:
                return td

        newargs = [f(td) for td in self.tds]
        return self.create(newargs)

    def conversionD1(self):
        raise NotImplementedError

    def conversionD3(self):
        raise NotImplementedError

    def conversion99(self, nf):
        return self.create([td.canonicalize(nf) for td in self.tds])

    def canonicalize_once(self, nf=None):
        simplifiers = [lambda: self.conversion1(),  # should also work self.conversion1, self.conversion2 ...
                       lambda: self.conversion2(),
                       lambda: self.conversion3(),
                       lambda: self.conversion4(),
                       lambda: self.conversion5(),
                       lambda: self.conversion6(),
                       lambda: self.conversion7(nf),
                       lambda: self.conversion8(),
                       lambda: self.conversion9(),
                       lambda: self.conversion10(),
                       lambda: self.conversion11(),
                       lambda: self.conversion12(),
                       lambda: self.conversion13(),
                       lambda: self.conversion14(),
                       lambda: self.conversion15(),
                       lambda: self.conversion16(),
                       lambda: self.conversionD1(),
                       lambda: self.conversionD3(),
                       lambda: self.conversion99(nf)]
        return find_simplifier(self, simplifiers)

    def cmp_to_same_class_obj(self, td):
        from utils import compare_sequence
        if type(self) != type(td):
            return super().cmp_to_same_class_obj(td)
        elif self == td:
            return False
        else:
            return compare_sequence(self.tds, td.tds)
