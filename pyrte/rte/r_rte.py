# Copyright (©) 2021,22 EPITA Research and Development Laboratory
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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.r_rte.py

from typing import List, Set, Tuple, Any, Callable, Optional, TypeGuard


class CannotComputeDerivative(Exception):
    def __init__(self, msg, rte, wrt, factors, disjoints):
        self.msg = msg
        self.rte = rte
        self.wrt = wrt
        self.factors = factors
        self.disjoints = disjoints
        super().__init__(msg)


class CannotComputeDerivatives(Exception):
    def __init__(self, msg, rte, wrt, first_types, mdtd, factors, disjoints):
        self.msg = msg
        self.rte = rte
        self.wrt = wrt
        self.first_types = first_types
        self.mdtd = mdtd
        self.factors = factors
        self.disjoints = disjoints
        super().__init__(msg)


class Rte:
    from genus.simple_type_d import SimpleTypeD
    #  from rte.xymbolyco import Dfa

    def __repr__(self):
        return self.__str__()

    def first_types(self) -> Set[SimpleTypeD]:
        return set()  # empty set

    def nullable(self):
        raise Exception(f"nullable not implemented for {self} of type {type(self)}")

    def canonicalize(self) -> 'Rte':
        from genus.utils import fixed_point

        def good_enough(a, b):
            return type(a) == type(b) and a == b

        return fixed_point(self, lambda r: r.canonicalize_once(), good_enough)

    def canonicalize_once(self) -> 'Rte':
        return self

    def cmp_to_same_class_obj(self, t: 'Rte'):
        assert type(self) == type(t), f"expecting same type {self} is {type(self)}, while {t} is {type(t)}"
        raise TypeError(f"cannot compare rtes of type {type(self)}")

    def derivative(self,
                   wrt: Optional[SimpleTypeD],
                   factors: List[SimpleTypeD],
                   disjoints: List[SimpleTypeD]) -> 'Rte':
        from rte.r_emptyset import EmptySet
        if wrt is None:
            return self
        elif wrt.inhabited() is False:
            return EmptySet
        else:
            return self.derivative_down(wrt, factors, disjoints)

    def derivative1(self, wrt: Optional[SimpleTypeD]):
        return self.derivative(wrt, [], [])

    def derivative_down(self,
                        wrt: Optional[SimpleTypeD],
                        factors: List[SimpleTypeD],
                        disjoints: List[SimpleTypeD]) -> 'Rte':
        raise TypeError(f"derivative_down not implemented for {self} of type {type(self)}")

    # Computes a pair of Vectors: (Vector[Rte], Vector[Seq[(SimpleTypeD,Int)]])
    #   Vector[Rte] is a mapping from Int to Rte designating the states
    #      of a Dfa.  Each state, i, corresponds to the i'th Rte in this vector.
    #   Vector[Seq[(SimpleTypeD,Int)]] designates the transitions from each state.
    #      the i'th component designates a Seq of transitions, each of the form
    #      (td:SimpleTypeD, j:Int), indicating that in state i, an object of type
    #      td transitions to state j.
    #   E.g., ([And(Cat(And(∅, ε), Cat(ε, ε)), ∅), ∅],
    #          [[(STop, 1)],
    #           [(STop, 1)]])
    #   E.g., ([Cat(Singleton(SOr(SAtomic(Test2), SEmpty)), Or(Cat(∅, ε), Or(∅, ε))),
    #          ε,
    #          ∅],
    #   [[(SAtomic(Test2), 1), (SNot(SAtomic(Test2)), 2)],
    #    [(STop, 2)],
    #    [(STop, 2)]])

    def derivatives(self) -> Tuple[List['Rte'],
                                   List[List[Tuple[SimpleTypeD, int]]]]:
        from genus.utils import trace_graph
        from genus.mdtd import mdtd
        from genus.simple_type_d import SimpleTypeD

        def edges(rt: Rte) -> List[Tuple[SimpleTypeD, Rte]]:
            assert isinstance(rt, Rte)
            fts = rt.first_types()
            wrts = mdtd(fts)

            def d(wrt: Optional[SimpleTypeD],
                  factors: List[SimpleTypeD],
                  disjoints: List[SimpleTypeD]) -> Rte:
                try:
                    return rt.derivative(wrt, factors, disjoints).canonicalize()
                except CannotComputeDerivative as e:
                    if rt == rt.canonicalize():
                        msg = "\n".join([f"When generating derivatives from {self}",
                                         f"  when computing edges of {rt}",
                                         f"  which canonicalizes to {rt.canonicalize()}",
                                         f"  computing derivative of {e.rte}",
                                         f"  wrt={e.wrt}",
                                         f"  factors={factors}",
                                         f"  disjoints={disjoints}",
                                         f"  derivatives() reported: {e.msg}"])
                        raise CannotComputeDerivatives(msg=msg,
                                                       rte=rt,
                                                       wrt=wrt,
                                                       factors=factors,
                                                       disjoints=disjoints,
                                                       first_types=fts,
                                                       mdtd=wrts) from None
                    else:
                        print(f"failed to compute derivative of {rt} wrt={wrt}," +
                              f"\n  computing derivative of {rt.canonicalize()} instead")
                        return rt.canonicalize().derivative(wrt, factors, disjoints).canonicalize()

            return [(td, d(td, factors, disjoints))
                    for [td, factors, disjoints] in wrts]

        return trace_graph(self, edges)

    def to_dfa(self, exit_value: Any = True):
        from rte.xymbolyco import rte_to_dfa
        return rte_to_dfa(self, exit_value)

    def simulate(self, exit_value: Any, sequence: List[Any]) -> Any:
        return self.to_dfa(exit_value).simulate(sequence)

    def to_dot(self,
               title,
               exit_value: Any = True,
               view=False,
               abbrev=True,
               draw_sink=False,
               state_legend=True,
               verbose=False):
        return self.to_dfa(exit_value).to_dot(title=title,
                                              view=view,
                                              abbrev=abbrev,
                                              draw_sink=draw_sink,
                                              state_legend=state_legend,
                                              verbose=verbose)

    def inhabited(self):
        return self.to_dfa(True).inhabited()

    def vacuous(self):
        inh = self.inhabited()
        if inh is None:
            return None
        else:
            return not inh

    def equivalent(self, rte2):
        rte1 = self
        return rte1.to_dfa(True).equivalent(rte2.to_dfa(True))

    def search(self, test: Callable[['Rte'], bool]) -> Optional['Rte']:
        # search the Rte for any node satisfying the given predicate, test
        # return that node (of type Rte) else return None
        if test(self):
            return self
        else:
            return None

    def constructThompson(self,ini:Callable[[],int],out:Callable[[],int]) \
            -> (int, int, List[Tuple[int,Optional[SimpleTypeD],int]]):
        raise TypeError(f"generateThompson not implemented for {self} of type {type(self)}")


def random_rte(depth):
    import random

    def random_and():
        from rte.r_and import And
        return And(random_rte(depth - 1),
                   random_rte(depth - 1))

    def random_or():
        from rte.r_or import Or
        return Or(random_rte(depth - 1),
                  random_rte(depth - 1))

    def random_not():
        from rte.r_not import Not
        return Not(random_rte(depth - 1))

    def random_star():
        from rte.r_star import Star
        return Star(random_rte(depth - 1))

    def random_cat():
        from rte.r_cat import Cat
        return Cat(random_rte(depth - 1),
                   random_rte(depth - 1))

    def random_singleton():
        from genus.depthgenerator import random_type_designator
        from rte.r_singleton import Singleton
        return Singleton(random_type_designator(depth))

    def random_leaf():
        from rte.r_sigma import Sigma
        from rte.r_emptyset import EmptySet
        from rte.r_epsilon import Epsilon
        return random.choice([Sigma, EmptySet, Epsilon])

    if depth <= 0:
        return random_singleton()
    else:
        randomizer = random.choice([random_and,
                                    random_or,
                                    random_not,
                                    random_star,
                                    random_cat,
                                    random_singleton,
                                    random_leaf])
        return randomizer()
