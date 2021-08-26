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
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.r_rte.py

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
    def __repr__(self):
        return self.__str__()

    def first_types(self):
        return set()  # empty set

    def nullable(self):
        raise Exception(f"nullable not implemented for {self} of type {type(self)}")

    def canonicalize(self):
        from genus.utils import fixed_point

        def good_enough(a, b):
            return type(a) == type(b) and a == b

        return fixed_point(self, lambda r: r.canonicalize_once(), good_enough)

    def canonicalize_once(self):
        return self

    def cmp_to_same_class_obj(self, t):
        assert type(self) == type(t), f"expecting same type {self} is {type(self)}, while {t} is {type(t)}"
        raise TypeError(f"cannot compare rtes of type {type(self)}")

    def derivative(self, wrt, factors, disjoints):
        from rte.r_emptyset import EmptySet
        if wrt is None:
            return self
        elif wrt.inhabited() is False:
            return EmptySet
        else:
            return self.derivative_down(wrt, factors, disjoints)

    def derivative1(self, wrt):
        return self.derivative(wrt, [], [])

    def derivative_down(self, wrt, factors, disjoints):
        raise TypeError(f"derivative_down not implemented for {self} of type {type(self)}")

    # Computes a pair of Vectors: (Vector[Rte], Vector[Seq[(SimpleTypeD,Int)]])
    #   Vector[Rte] is a mapping from Int to Rte designating the states
    #      of a Dfa.  Each state, i, corresponds to the i'th Rte in this vector.
    #   Vector[Seq[(SimpleTypeD,Int)]] designates the transitions from each state.
    #      the i'th component designates a Seq of transitions, each of the form
    #      (td:SimpleTypeD, j:Int), indicating that in state i, an object of type
    #      td transitions to state j.
    def derivatives(self):
        from genus.utils import trace_graph
        from genus.mdtd import mdtd

        def edges(rt):
            assert isinstance(rt, Rte)
            fts = rt.first_types()
            wrts = mdtd(fts)

            def d(wrt, factors, disjoints):
                try:
                    deriv = rt.derivative(wrt, factors, disjoints).canonicalize()
                    #print(f"{rt}.derivative.({wrt}) = {deriv}")
                    return deriv
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
                              f" computing derivative of {rt.canonicalize()} instead")
                        return rt.canonicalize().derivative(wrt).canonicalize()

            return [(td, d(td, factors, disjoints)) for [td, factors, disjoints] in wrts]

        return trace_graph(self, edges)

    def to_dfa(self, exit_value=True):
        from rte.xymbolyco import createDfa
        from genus.s_or import createSOr
        rtes, transitions = self.derivatives()
        # transitions is a vector of sequences, each sequence contains pairs (SimpleTypeD,int)
        transition_triples = [(src, td, dst)
                              for src in range(len(transitions))
                              for td, dst in transitions[src]
                              ]

        def combine_labels(td1, td2):
            return createSOr([td1, td2]).canonicalize()

        accepting_states = [i for i in range(len(rtes)) if rtes[i].nullable()]
        return createDfa(pattern=self,
                         transition_triples=transition_triples,
                         accepting_states=accepting_states,
                         exit_map=dict([(i, exit_value) for i in accepting_states]),
                         combine_labels=combine_labels)

    def simulate(self, exit_value, sequence):
        return self.to_dfa(exit_value).simulate(sequence)

    def to_dot(self, title, exit_value=True, view=False, abbrev=True, draw_sink=False, state_legend=True,
               verbose=False):
        return self.to_dfa(exit_value).to_dot(title=title,
                                              view=view,
                                              abbrev=abbrev,
                                              draw_sink=draw_sink,
                                              state_legend=state_legend,
                                              verbose=verbose)

    def equivalent(self, rte2):
        rte1 = self
        return rte1.to_dfa(True).equivalent(rte2.to_dfa(True))


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
        return random_type_designator(depth)

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
