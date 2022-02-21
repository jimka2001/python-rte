# Copyright (©) 2022 EPITA Research and Development Laboratory
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


from typing import Any, List, Tuple, Optional, TypeVar, Callable

from genus.simple_type_d import SimpleTypeD
from genus.utils import trace_graph
from rte.r_rte import Rte
from rte.xymbolyco import Dfa, createDfa


def constructEpsilonFreeTransitions(rte: Rte) -> (int, List[int], List[(int, SimpleTypeD, int)]):
    ini, out, transitions = constructTransitions(rte)
    return removeEpsilonTransitions(ini, out, transitions)


def removeEpsilonTransitions(ini:int,
                             out:int,
                             transitions:List[Tuple[int,Optional[SimpleTypeD],int]]
                             ) -> Tuple[int, int, List[Tuple[int, SimpleTypeD, int]]]:
    assert False, "not yet implemented"


def constructDeterminizedTransitions(rte: Rte) -> (int, List[int], List[(int, SimpleTypeD, int)]):
    in2, outs2, clean = constructEpsilonFreeTransitions(rte)
    completed = complete(in2, outs2, clean)
    return determinize(in2, outs2, completed)

def complete(ini:int,
             outs:List[int],
             transitions:List[Tuple[int, SimpleTypeD, int]]
             ) -> List[Tuple[int,SimpleTypeD,int]]:
    assert False, "not yet implemented"


def determinize(ini:int,
                outs:List[int],
                transitions:List[Tuple[int, SimpleTypeD, int]]
                ) -> (int, List[int], List[(int, SimpleTypeD, int)]):
    # this can be done with a call to traceTransitionGraph.
    #   to generate a graph (list of transitions) whose vertices are
    #   each a Set[int].  Then you'll have to renumber back to
    #   states as int.
    # use the mdtd function to partition a set/list of types into
    # a set of disjoint types.
    assert False, "not yet implemented"


# start with a given vertex of a graph (yet to be determined).
# We discover all the vertices by calling the edges function on each vertex
# yet discovered, starting with the given initial vertex.
# Once all the vertices have been discovered, filter them with the isAccepting predicate
# to determine the final / accepting states.
# Return a pair(sequence - of - final - states,
# sequence - of - transitions of the form(vertex, label, vertex)
V = TypeVar('V', int, Tuple[int, int])


def traceTransitionGraph(q0: V,
                         edges: Callable[[V], List[Tuple[SimpleTypeD, V]]],
                         is_final: Callable[[V], bool]
                         ) -> Tuple[List[V], List[Tuple[V, SimpleTypeD, V]]]:
    qs, transitions = trace_graph(q0, edges)
    return ([f for f in qs if is_final(f)],
            [(x, label, qs[y])
             for x, pairs in zip(qs, transitions)
             for label, y in pairs])


# Construct a sequence of transitions specifying an epsilon - nondeterministic - finite - automaton.
# Also return the initial and final state.
def constructTransitions(rte: Rte) -> Tuple[int, int, List[(int, Optional[SimpleTypeD], int)]]:
    assert False, "not yet implemented"


def constructDeterminizedTransitions(rte: Rte
                                     ) -> Tuple[int, List[int], List[Tuple[int, SimpleTypeD, int]]]:
    assert False, "not yet implemented"


def constructThompsonDfa(pattern: Rte, ret: Any = True) -> Dfa:
    next_state = 0

    def count() -> int:
        nonlocal next_state
        next_state = next_state + 1
        return next_state

    # createDfa requires the initial state to be 0
    def renumber(ini1: int,
                 outs1: List[int],
                 transitions1: List[Tuple[int, SimpleTypeD, int]]
                 ) -> Tuple[int, List[int], List[Tuple[int, SimpleTypeD, int]]]:
        mapping = {ini1: 0}
        for x, td, y in transitions1:
            for q in (x, y):
                if q not in mapping:
                    mapping[x] = count()
        for f in outs1:
            if f not in mapping:
                mapping[f] = count()
        return (mapping[ini1],
                [mapping[f] for f in outs1],
                [(mapping[x], td, mapping[y]) for x, td, y in transitions1])

    ini, outs, determinized = constructDeterminizedTransitions(pattern)
    ini2, outs2, determinized2 = renumber(ini, outs, determinized)
    assert ini2 == 0
    fmap = dict([(f, ret) for f in outs2])

    return createDfa(pattern=pattern,
                     transition_triples=determinized2,
                     accepting_states=outs2,
                     exit_map=fmap,
                     )
