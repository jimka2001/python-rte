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
                              f" computing derivative of {rt.canonicalize()} instead")
                        return rt.canonicalize().derivative(wrt).canonicalize()
            return [(td, d(td, factors, disjoints)) for [td, factors, disjoints] in wrts]

        return trace_graph(self, edges)
