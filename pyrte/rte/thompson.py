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


from typing import Any, List, Tuple, Optional, TypeVar, Callable, Set

from genus.simple_type_d import SimpleTypeD
from genus.utils import trace_graph, group_map, group_by, makeCounter, fixed_point, generate_lazy_val
from rte.r_rte import Rte

V = TypeVar('V', int, Tuple[int, int])
E = TypeVar('E')

count: Callable[[], int] = makeCounter()


def makeNewState(ini,
                 outs,
                 transitions: List[Tuple[int, Optional[SimpleTypeD], int]],
                 count: Callable[[], int]) -> int:
    while True:
        q = count()
        if ini == q:
            continue
        if q in outs:
            continue
        if any(x == q or y == q for x, _tr, y in transitions):
            continue
        return q


def findAllStates(transitions: List[Tuple[int, Optional[SimpleTypeD], int]]) -> Set[int]:
    return {q
            for x, _tr, y in transitions
            for q in [x, y]}


def constructEpsilonFreeTransitions(rte: Rte) \
        -> (int, List[int], List[Tuple[int, SimpleTypeD, int]]):
    ini, out, transitions = constructTransitions(rte)
    return removeEpsilonTransitions(ini, out, transitions)


def accessible(ini: int,
               outs: List[int],
               transitions: List[Tuple[int, SimpleTypeD, int]]) \
        -> Tuple[int, List[int], List[Tuple[int, SimpleTypeD, int]]]:
    grouped = group_map(lambda trans: trans[0],
                        transitions,
                        lambda _x, y, z: (y, z))
    accessibleOuts, accessibleTransitions = traceTransitionGraph(ini,
                                                                 lambda q: grouped.get(q, []),
                                                                 lambda q: q in outs)
    return (ini, accessibleOuts, accessibleTransitions)


def coaccessible(ini: int,
                 outs: List[int],
                 transitions: List[Tuple[int, SimpleTypeD, int]]) \
        -> Tuple[int, List[int], List[Tuple[int, SimpleTypeD, int]]]:
    proxy = makeNewState(ini, outs, transitions, count)
    augmentedTransitions = transitions + [(q, STop, proxy)
                                          for q in outs]
    grouped = group_map(lambda trans: trans[2],  # lambda _x,_tr, y: y,
                        augmentedTransitions,
                        lambda trans: (trans[1], trans[0])  # lambda x,tr,_z: (tr,x)
                        )
    _co, reversedTransitions = traceTransitionGraph(proxy,
                                                    lambda q: grouped.get(q, []),
                                                    lambda q: q == ini)
    coaccessibleTransitions = [(x, td, y)
                               for y, td, x in reversedTransitions
                               if y != proxy]
    return (ini, outs, coaccessibleTransitions)


def trim(ini: int,
         finals: List[int],
         transitions: List[Tuple[(int, SimpleTypeD, int)]]) \
        -> Tuple[int, List[int], List[Tuple[int, SimpleTypeD, int]]]:
    aIn, aFinals, aTransitions = accessible(ini, finals, transitions)
    return coaccessible(aIn, aFinals, aTransitions)


def removeEpsilonTransitions(ini: int,
                             out: int,
                             transitions: List[Tuple[int, Optional[SimpleTypeD], int]]
                             ) -> Tuple[int, List[int], List[Tuple[int, SimpleTypeD, int]]]:
    epsilonTransitions = {(x, y) for x, tr, y in transitions
                          if tr is None}
    normalTransitions = [trans for trans in transitions
                         if trans[1] is not None]
    allStates: List[int] = findAllStates(transitions)

    def reachableFrom(q: int) -> Set[int]:
        return {y for x, y in epsilonTransitions
                if x == q}

    def extendClosure(m: List[Set[int]]) -> List[Set[int]]:
        return [set().union(*los)  # compute the union of a list of sets
                for qs in m  # qs:Set[int]
                for los in [[reachableFrom(q) for q in qs]]  # los is a List[Set[int]]
                ]

    epsilonClosure = fixed_point([{q} for q in allStates],
                                 extendClosure,
                                 lambda set1, set2: set1 == set2)

    transitions2 = [(q, label, y)
                    for q, closure in zip(allStates, epsilonClosure)
                    for c in closure
                    for x, label, y in normalTransitions
                    if x == c
                    if x != q]

    updatedTransitions = normalTransitions + transitions2
    remainingStates = findAllStates(updatedTransitions)
    finals = [q for q, closure in zip(allStates, epsilonClosure)
              if q in remainingStates or q == ini
              if out in closure]
    return (trim(ini, finals, updatedTransitions))


def simulateRte(sequence: List[Any],
                exitValue: E,
                rte: Rte) -> Optional[E]:
    ini, outs, transitions = constructEpsilonFreeTransitions(rte)
    return simulateTransitions(sequence, exitValue,
                               ini, outs, transitions)


def simulateTransitions(sequence: List[Any],
                        exitValue: E,
                        ini: int,
                        outs: List[int],
                        transitions: List[Tuple[int, SimpleTypeD, int]]) -> Optional[E]:
    groups = group_by(lambda trans: trans[0],
                      transitions)

    def simulate() -> Optional[E]:
        qs = set(ini)
        for v in sequence:
            if not qs:
                return None
            qs = {y for q in qs
                  for _x, td, y in groups.get(q, [])
                  if td.typep(v)}
        return qs

    computation = simulate()
    if computation is None:
        return None
    for f in computation:
        if f in outs:
            return exitValue
    return None


def constructDeterminizedTransitions(rte: Rte) \
        -> Tuple[int, List[int], List[Tuple[int, SimpleTypeD, int]]]:
    in2, outs2, clean = constructEpsilonFreeTransitions(rte)
    completed = complete(in2, outs2, clean)
    return determinize(in2, outs2, completed)


# Transform a sequence of transitions (either deterministic or otherwise)
# into a set of completed transitions.  I.e., the union of the types labeling
# any arbitrary transition is STop.  In the case when it cannot be determined
# whether the transitions are already locally complete, an additional transition
# is added with is the complement of the existing transitions.  This may be
# empty but if it is empty, .inhabited returns None (dont-know).
def complete(ini: int,
             outs: List[int],
             clean: List[Tuple[int, SimpleTypeD, int]]
             ) -> List[Tuple[int, SimpleTypeD, int]]:
    from genus.s_top import STop

    allStates = findAllStates(clean)
    sink = generate_lazy_val(lambda: makeNewState(ini, outs, clean, count))
    grouped = group_by(lambda trans: a[0],
                       clean)
    completingTransitions = [(q, remaining, sink())
                             for q in allStates
                             for transitions in [grouped[q]]
                             if transitions is not None
                             for tds in [[b for a, b, c in transitions]]
                             for remaining in [SNot(createSOr(tds))]
                             if remaining.inhabited is not False
                             ]
    if not clean:
        return [(ini, STop, sink()),
                (sink(), STop, sink())]
    elif not completingTransitions:
        return clean
    else:
        return clean + completingTransitions + [(sink(), STop, sink())]

def renumberTransitions(ini:int,
                        outs:List[int],
                        transitions:List[Tuple[int,SimpleTypeD,int]],
                        count:Callable[[],int]) \
    -> Tuple[int,List[int],List[Tuple[int,SimpleTypeD,int]]]:
    mapping_list = [ini] + [q for q in outs
                            if not q == ini] + list({q for x, tr, y in transitions
                                                     for q in [x,y]
                                                     if q != ini
                                                     if not q in outs})
    mapping = dict((qq,count()) for qq in mapping_list)

    return (mapping[ini],
            [mapping[q] for q in outs],
            [(mapping[xx],td,mapping[yy]) for xx, td, yy in transitions])

# Given a description of a non-deterministic FA, with epsilon transitions
#   already removed, use a graph-tracing algorithm to compute the reachable
#   states in the determinized automaton.
def determinize(ini: int,
                finals: List[int],
                transitions: List[Tuple[int, SimpleTypeD, int]]
                ) -> Tuple[int, List[int], List[Tuple[int, SimpleTypeD, int]]]:
    # This can be done with a call to traceTransitionGraph.
    #   to generate a graph (list of transitions) whose vertices are
    #   each a Set[int].  Then you'll have to renumber back to
    #   states as int.
    #   BTW, you can also use traceTransitionGraph to implement
    #   the cartesian product needed for And, as well as to remove
    #   non-accessible, and non-coaccessible vertices.
    # Use the mdtd function to partition a set/list of types into
    #   a set of disjoint types.

    grouped = group_by(lambda trans: trans[0],
                       transitions)

    def expandOneState(qs: Set[int]) -> List[Tuple[SimpleTypeD, Tuple[int]]]:
        from genus.mdtd import mdtd

        tds: Set[SimpleTypeD] = {td for q in qs
                                 for _x, td, _y in grouped.get(q, [])
                                 }
        tr2: Set[Tuple[SimpleTypeD, int]] = {(td, y) for td, factors, _disjoints in mdtd(tds)
                                             for q in qs
                                             for _x, td1, y in grouped.get(q, [])
                                             if td1 in factors}
        print(f"  tr2={tr2}")

        newTransitions = [(td, tuple(sorted(list(nextStates))))
                          for g in [group_by(lambda trans: trans[0],
                                             tr2)]
                          for td in g
                          for pairs in [g[td]]
                          for _1 in [print(f"pairs = {pairs}")]
                          for nextStates in [[y for _x, y in pairs]]]

        return newTransitions

    inX = (ini,)
    expandedFinals, expandedTransitions = traceTransitionGraph(inX,
                                                               expandOneState,
                                                               lambda qs: any(f in qs for f in finals))

    return renumberTransitions(inX, expandedFinals, expandedTransitions, count)


# start with a given vertex of a graph (yet to be determined).
# We discover all the vertices by calling the edges function on each vertex
# yet discovered, starting with the given initial vertex.
# Once all the vertices have been discovered, filter them with the isAccepting predicate
# to determine the final / accepting states.
# Return a pair(sequence - of - final - states,
# sequence - of - transitions of the form(vertex, label, vertex)
def traceTransitionGraph(q0: V,
                         edges: Callable[[V], List[Tuple[SimpleTypeD, V]]],
                         is_final: Callable[[V], bool]
                         ) -> Tuple[List[V], List[Tuple[V, SimpleTypeD, V]]]:
    qs, transitions = trace_graph(q0, edges)
    return ([f for f in qs if is_final(f)],
            [(x, label, qs[y])
             for x, pairs in zip(qs, transitions)
             for label, y in pairs])


# remove non-accessible transitions, and non-accessible final states
def accessible(ini: int,
               outs: List[int],
               transitions: List[Tuple[int, SimpleTypeD, int]]
               ) -> (int, List[int], List[Tuple[int, SimpleTypeD, int]]):
    grouped = group_map(lambda triple: triple[0],
                        transitions,
                        lambda triple: (triple[1], triple[2]))

    accessibleOuts, accessibleTransitions = \
        traceTransitionGraph(ini,
                             lambda q: grouped[q] if q in grouped else [],
                             lambda q: q in outs)

    return (ini, accessibleOuts, accessibleTransitions)


# Construct a sequence of transitions specifying an epsilon - nondeterministic - finite - automaton.
# Also return the initial and final state.
def constructTransitions(rte: Rte) \
        -> Tuple[int, int, List[Tuple[int, Optional[SimpleTypeD], int]]]:
    from genus.utils import generate_lazy_val
    ini = generate_lazy_val(count)
    out = generate_lazy_val(count)
    return rte.constructThompson(ini, out)


def constructVarArgsTransitions(rte: Rte,
                                identity: Rte,
                                binop: Callable[[Rte, Rte], Rte],
                                varArgsOp: Callable[[List[Rte]], Rte],
                                continuation: Callable[
                                    [], Tuple[int, int, List[Tuple[int, Optional[SimpleTypeD], int]]]]) \
        -> Tuple[int, int, List[Tuple[int, Optional[SimpleTypeD], int]]]:
    if not rte.operands:
        return constructTransitions(identity)
    elif 1 == len(rte.operands):
        return constructTransitions(self.operands[0])
    elif 2 < len(rte.operands):
        return constructTransitions(binop(self.operands[0],
                                          varArgsOP(self.operands[1:])))
    else:
        return continuation()


def constructTransitionsAnd(rte1: Rte, rte2: Rte) -> (int, int, List[Tuple[int, Optional[SimpleTypeD], int]]):
    pass


def constructTransitionsNot(rte: Rte) -> (int, int, List[Tuple[int, Optional[SimpleTypeD], int]]):
    pass


# this function can be used for debugging,
# use the FA described by the transitions which might be deterministic or otherwise,
#   but without epsilon transitions, to test whether the FA recognizes the input sequence.
#   return the given exit_value if yes, and return None otherwise.
def simulateTransitions(sequence: List[Any], exit_value: E,
                        ini: int, outs: List[int], transitions: List[Tuple[int, SimpleTypeD, int]]
                        ) -> Optional[E]:
    groups = group_by(lambda trans: trans[0], transitions)
    states = {ini}
    for e in sequence:
        # if we reach zero number of next states, but haven't yet reached the end of
        #   the sequence, then return None
        if not states:
            return None
        # compute the set of next states for the next iteration
        states = {y for x in states
                  for _, td, y in (groups[x] if x in groups else set())
                  if td.typep(e)}
    for f in states:
        if f in outs:
            return exit_value
    return None


def constructThompsonDfa(pattern: Rte, ret: Any = True) -> 'Dfa':
    from rte.xymbolyco import Dfa, createDfa
    ini0, outs0, determinized0 = constructDeterminizedTransitions(pattern)
    ini, outs, determinized = renumberTransitions(ini0, outs0, determinized0,
                                                  makeCounter(0,1))
    fmap = dict([(f, ret) for f in outs])
    print(f"CTD ini={ini}")
    return createDfa(pattern=pattern,
                     ini=ini,
                     transition_triples=determinized,
                     accepting_states=outs,
                     exit_map=fmap,
                     )
