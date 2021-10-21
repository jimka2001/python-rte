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


from functools import reduce
from rte.r_rte import Rte
from genus.simple_type_d import SimpleTypeD
from genus.ite import eval_ite, transitions_to_ite
from typing import List, Union, Tuple, Any, Dict, Callable, Optional, TypeVar

L = TypeVar('L', Rte, SimpleTypeD)
Triple = Tuple[Union[int, str],
               L,  # Union[Rte, SimpleTypeD],
               Union[int, Tuple[str, Any]]]
verbose = False


class State:
    def __init__(self, index, initial, accepting, pattern, transitions):
        from genus.utils import generate_lazy_val
        assert isinstance(index, int)
        assert index >= 0
        assert isinstance(initial, bool)
        assert isinstance(accepting, bool)
        assert pattern is None or isinstance(pattern, Rte)
        assert isinstance(transitions,
                          dict), f"transitions has type {type(transitions)} expecting dict: transitions={transitions}"
        for tr in transitions:
            assert isinstance(tr, SimpleTypeD), f"tr={tr} (type={type(tr)}) is not a SimpleTypeD"
            assert isinstance(transitions[tr], int)
        tr_list = list(transitions)
        for i in range(len(tr_list)):

            for j in range(i):
                tr1 = tr_list[i]
                tr2 = tr_list[j]
                assert tr1.disjoint(tr2) is not False, f"expecting disjoint transitions: not {tr1} vs {tr2}"

        self.index = index  # int
        self.initial = initial  # bool
        self.accepting = accepting  # bool
        self.pattern = pattern  # Rte
        self.transitions = transitions  # Map SimpleTypeD -> Int
        # it is not clear whether this ite structure needs to be generated at state creation time,
        #  or at simulation time.  Here we delay its generation to the first time dfa.simulate(...)
        #  encounters this State.
        self.ite = generate_lazy_val(lambda: transitions_to_ite([(td, transitions[td]) for td in transitions]))
        super().__init__()


EqvClass = Tuple[State, ...]


def createSinkState(index: int) -> State:
    from genus.s_top import STop

    return State(index=index,
                 initial=(index == 0),
                 accepting=False,
                 pattern=None,
                 transitions={STop: index})


def default_combine_labels(_l1, _l2):
    raise Exception('Missing combine_labels for Dfa')


class Dfa:
    def __init__(self,
                 pattern: Optional[Rte] = None,
                 states: Optional[List[State]] = None,
                 exit_map: Optional[Dict[int, Any]] = None,
                 combine_labels: Callable[[SimpleTypeD, SimpleTypeD], SimpleTypeD] = default_combine_labels):
        if exit_map is None:
            exit_map = dict([])
        if not states:
            states = [createSinkState(0)]
        assert pattern is None or isinstance(pattern, Rte)
        assert isinstance(states, list)
        for st in states:
            assert isinstance(st, State)
        assert isinstance(exit_map, dict)
        for i in exit_map:
            assert isinstance(i, int)
            assert i >= 0
        assert callable(combine_labels)
        for q in states:
            if q.accepting:
                assert q.index in exit_map, f"accepting state {q.index} missing from exit_map {exit_map}"
        self.pattern = pattern  # Rte
        self.states = states  # vector of State objects
        self.exit_map = exit_map  # map index -> return_value
        self.combine_labels = combine_labels  # function (SimpleTypeD,SimpleTypeD)->SimpleTypeD

    def to_dot(self,
               title: Optional[str],
               view: bool = False,
               abbrev: bool = True,
               draw_sink: bool = False,
               state_legend: bool = True,
               verbose: bool = False):
        from genus.utils import dot_view
        import io
        text = io.StringIO()

        if view:
            dot_string = self.to_dot(title=title,
                                     verbose=verbose,
                                     view=False,
                                     abbrev=abbrev,
                                     draw_sink=draw_sink,
                                     state_legend=state_legend)
            # print(f"{dot_string}")
            return dot_view(dot_string, verbose=verbose, title=title)
        sink_state_indices = self.find_sink_states()
        if draw_sink:
            visible_states = self.states
        else:
            visible_states = [q for q in self.states if q.index not in sink_state_indices]
        transition_labels = list(set([td for q in visible_states
                                      for td in q.transitions
                                      for dst_id in [q.transitions[td]]
                                      if self.states[dst_id] in visible_states
                                      ]))
        abbrevs = dict(zip(transition_labels, range(len(transition_labels))))
        labels = dict([(abbrevs[td], td) for td in abbrevs])
        text.write("digraph G {\n")
        if title:
            text.write(f"  // {title}\n")
        text.write("  rankdir=LR;\n")
        text.write("  fontname=courier;\n")
        if abbrev:
            text.write(f"   label=\"{title} ")
            for index in labels:
                text.write(f"\\lt{index}= {labels[index]}")
            text.write("\\l\"\n")
        text.write("  graph [labeljust=l,nojustify=true];\n")
        text.write("  node [fontname=Arial, fontsize=25];\n")
        text.write("  edge [fontname=Helvetica, fontsize=20];\n")
        for q in self.states:
            if q.index in sink_state_indices:
                pass
            else:
                if q.accepting:
                    text.write(f"   q{q.index} [shape=doublecircle] ;\n")
                    text.write(f"   X{q.index} [label=\"{self.exit_map[q.index]}\", shape=rarrow]\n")
                    text.write(f"   q{q.index} -> X{q.index} ;\n")
                if q.initial:
                    text.write(f"   H{q.index} [label=\"\", style=invis, width=0]\n")
                    text.write(f"   H{q.index} -> q{q.index};\n")
                for td in q.transitions:
                    next_state_id = q.transitions[td]
                    if not draw_sink and next_state_id in sink_state_indices:
                        pass
                    else:
                        if abbrev:
                            label = f"t{abbrevs[td]}"
                        else:
                            label = f"{td}"
                        text.write(f"   q{q.index} -> q{next_state_id} [label=\"{label}\"];\n")
        text.write("}\n")
        return text.getvalue()

    def delta(self, source_state, target_label) -> State:
        return self.states[source_state.transitions[target_label]]

    def simulate(self, sequence: List[Any]) -> Any:
        state_id = 0
        for element in sequence:
            state_id = eval_ite(self.states[state_id].ite(), element)
            if state_id is None:
                return None

        if self.states[state_id].accepting:
            return self.exit_map[state_id]
        else:
            return None

    def serialize(self):
        def transitions():
            return [(state.index, tr, state.transitions[tr])
                    for state in self.states
                    for tr in state.transitions]

        def accepting():
            return [state.index for state in self.states if state.accepting]

        def exit_map():
            # return [(id, self.exit_map[id]) for id in self.exit_map]
            return self.exit_map

        return [self.pattern, transitions(), accepting(), exit_map(), self.combine_labels]

    def find_sink_states(self) -> List[int]:  # returns a list of integers
        from genus.s_top import STop
        return [q.index for q in self.states
                if not q.accepting
                and 1 == len(q.transitions)
                and q.transitions[STop] == q.index]

    def complete(self) -> 'Dfa':
        from rte.r_not import Not
        from rte.r_or import createOr
        from genus.s_top import STop
        pattern, transitions, accepting, exit_map, combine_labels = self.serialize()
        sink_states = self.find_sink_states()
        if sink_states:
            sink_id = sink_states[0]
        else:
            sink_id = len(self.states)
        extra_transitions = [(q.index, td, sink_id)
                             for q in self.states
                             for tds in [[td for td, _ in q.transitions]]
                             for td in [Not(createOr(tds)).canonicalize()]
                             if td.inhabited() is not False
                             ]

        if not extra_transitions:
            return self
        else:
            return createDfa(pattern=pattern,
                             transition_triples=transitions + extra_transitions + [[sink_id, STop, sink_id]],
                             accepting_states=accepting,
                             exit_map=exit_map,
                             combine_labels=combine_labels)

    def complement(self, exit_map: Dict[int, Any]) -> 'Dfa':
        from rte.r_not import createNot
        pattern_old, transitions, accepting, _, combine_labels = self.complete().serialize()
        if pattern_old is None:
            pattern = None
        else:
            pattern = createNot(self.pattern)
        return createDfa(pattern=pattern,
                         transition_triples=transitions,
                         accepting_states=[i for i in range(len(self.states)) if i not in accepting],
                         exit_map=exit_map,
                         combine_labels=combine_labels)

    def find_accessibles(self) -> Tuple[List[int],
                                        List[int]]:
        # returns a pair of two lists of indices (accessibles, co-accessibles)
        def reachable(seen, triples):
            # returns pair (reachables,remaining_triples),
            # reachables is list of int, triples are remaining triples to consider on future iteration
            frontier = [(src, label, dst) for src, label, dst in triples if src in seen]
            remaining = [triple for triple in triples if triple not in frontier]
            return (seen + [dst for _, _, dst in frontier if dst not in seen],
                    remaining)

        def expand_reachable(seen, triples):
            while triples:
                s = len(seen)
                seen, triples = reachable(seen, triples)
                if s == len(seen):
                    return seen
            return seen

        _, transitions, accepting_ids, _, _ = self.serialize()
        accessibles = expand_reachable([0], transitions)
        # now reverse src and dst and recompute reachable, these are coaccessible.
        coaccessibles = expand_reachable(accepting_ids, [(dst, label, src) for src, label, dst in transitions])
        return accessibles, coaccessibles

    def trim(self, compact: bool = True) -> 'Dfa':
        pattern, transitions, accepting_ids, exit_map, combine_labels = self.serialize()
        accessibles, coaccessibles = self.find_accessibles()
        useful_states = set(accessibles + coaccessibles)
        useful_transitions = [(src, label, dst) for src, label, dst in transitions
                              if src in useful_states or dst in useful_states]
        if compact:
            # after removing useless transitions, thus effectively removing useless states
            # there may now be gaps.  ie. a Dfa is constructed with an array/list of states
            # where the index in the array is the same as the index of the state.
            # so we may need to decrease some of the higher indices to fill the gaps.
            def rename_index(old, new, idx):
                if idx == old:
                    return new
                else:
                    return idx

            def rename_state(old, new, xitions, accepting, em):
                xitions = [(rename_index(old, new, src),
                            label,
                            rename_index(old, new, dst))
                           for src, label, dst in xitions]
                accepting = [rename_index(old, new, idx) for idx in accepting]
                em = dict([(rename_index(old, new, idx), label)
                           for idx in em
                           for label in [em[idx]]])
                return xitions, accepting, em

            for new_index, old_index in enumerate(sorted(list(useful_states))):
                useful_transitions, accepting_ids, exit_map = rename_state(old_index,
                                                                           new_index,
                                                                           useful_transitions,
                                                                           accepting_ids,
                                                                           exit_map)

        return createDfa(pattern, useful_transitions, accepting_ids, exit_map, combine_labels)

    def combine_parallel_triples(self,
                                 triples: List[Triple],
                                 combine_parallel_labels: Callable[[List[L]], L]
                                 ) -> List[Triple]:
        if verbose:
            print(f"combine_parallel_triples self={self}")
        #  accepts a sequence of triples, each of the form [from label to]
        #   groups them by common from/to, these are parallel transitions
        #   combines the labels of the parallel transitions, into one single label
        #   and collects a sequence of transitions, none of which are parallel.
        #   This action is important because it greatly reduces the number of transitions
        #   created.  The caller, the computation of new-triples, makes an NxM loop
        #   creating NxM new triples.   This reduces N and M by eliminating parallel
        #   transitions.
        sources = list(set([s for s, _, _ in triples]))
        return [(src,
                 combine_parallel_labels([l for _, l, d in from_src if d == dst]),
                 dst)
                for src in sources
                for from_src in [[[s, l, d] for s, l, d in triples if s == src]]  # singleton
                for dst in list(set([d for _, _, d in from_src]))
                ]

    def extract_rte(self) -> Dict[Any, Rte]:
        from functools import reduce
        from rte.r_epsilon import Epsilon
        from rte.r_singleton import Singleton
        from rte.r_or import createOr
        from rte.r_cat import createCat
        from rte.r_star import Star
        #    1. minimize and trim the given dfa
        #    2. generate a list of transition triples [from label to]
        #    3. add transitions from extra-state-I to all initial states with :epsilon transition
        #    4. add transitions from all accepting states to extra-state-F (one per exit value) with :epsilon transition
        #    5. loop on each state
        #    6.    partition transitions into 4 groups [to-this-state loops-on-state from-state everything-else]
        #    7.    combine parallel transitions
        #    8.    n^2 iteration to-this-state x from-this-state
        #    9.    append new transitions in next iteration of loop 5.
        #    10. this reduces to one transition per exit value, returns the map of exit-value to label

        # step 1
        dfa = self.trim().minimize()

        # it is not really necessary to set self to None, but previous versions of the code
        # were accessing self rather than accessing dfa.
        self = None

        # step 2
        _, old_transition_triples, accepting, _, _ = dfa.serialize()
        old_transitions: List[Triple] = [(src, Singleton(td), dst)
                                         for src, td, dst in old_transition_triples]
        # step 3  # adding state whose index is NOT integer
        new_initial_transitions: List[Triple] = [("I", Epsilon, 0)]
        # step 4  # adding state whose index is NOT integer
        new_final_transitions: List[Triple] = [(qid, Epsilon, ("F", dfa.exit_map[qid]))
                                               for qid in accepting]

        def combine_parallel_labels(rtes: List[Rte]) -> Rte:
            return createOr(rtes).canonicalize()

        def extract_labels(triples) -> List[Rte]:
            return [l for _, l, _ in triples]

        def eliminate_state(triples: List[Triple], qid: int) -> List[Triple]:
            def f(acc, triple: Triple) -> Tuple[List[Triple],
                                                List[Triple],
                                                List[Triple],
                                                List[Triple]]:
                x_to_q, q_to_q, q_to_x, others = acc
                src, _, dst = triple
                if src == qid and dst == qid:
                    return x_to_q, q_to_q + [triple], q_to_x, others
                elif src == qid:
                    return x_to_q, q_to_q, q_to_x + [triple], others
                elif dst == qid:
                    return x_to_q + [triple], q_to_q, q_to_x, others
                else:
                    return x_to_q, q_to_q, q_to_x, others + [triple]

            # step 6
            x_to_q, q_to_q, q_to_x, others = reduce(f, triples, ([], [], [], []))

            # step 7
            self_loop_label = combine_parallel_labels(extract_labels(q_to_q))
            # step 8
            new_triples = [(src, lab, dst)
                           for src, pre_label, _ in dfa.combine_parallel_triples(x_to_q, combine_parallel_labels)
                           for _, post_label, dst in dfa.combine_parallel_triples(q_to_x, combine_parallel_labels)
                           for lab in [createCat([pre_label,
                                                  Star(self_loop_label),
                                                  post_label]
                                                 ).canonicalize()
                                       ]
                           ]

            return others + new_triples  # from eliminate_state

        # step 5 and 9
        new_transition_triples = reduce(eliminate_state,
                                        # we eliminate all states whose id is an integer,
                                        #  recall we have added states with id ("F",?) and also with
                                        #  id "I".  These will remain.
                                        range(len(dfa.states)),
                                        new_initial_transitions + old_transitions + new_final_transitions)
        exit_values = list(set([dfa.exit_map[qid] for qid in accepting]))
        for triple in new_transition_triples:
            assert isinstance(triple, tuple)
            assert 3 == len(triple)
            assert "I" == triple[0]
            assert isinstance(triple[1], Rte)
            assert isinstance(triple[2], tuple)
            assert 2 == len(triple[2])
            assert "F" == triple[2][0]
            assert triple[2][1] in exit_values

        els = [(exit_value, labels)
               for exit_value in exit_values  # step 10
               for labels in [[l for i, l, [f, e] in new_transition_triples
                               if e == exit_value
                               if f == "F"
                               if i == "I"]]]

        d = [(exit_value,
              combine_parallel_labels(labels).canonicalize())
             for exit_value, labels in els]
        return dict(d)

    def to_rte(self) -> Dict[Any, Rte]:
        from rte.r_emptyset import EmptySet
        extracted = self.extract_rte()
        if extracted:
            return extracted
        else:
            return dict([(True, EmptySet)])

    def paths_to_accepting(self, allow_maybe_satisfiable=False) -> List[List[State]]:
        # returns a list of paths
        # each path is a list of states starting with self.states[0]
        # and ending in an accepting state.
        # no path contains the same state twice, i.e. no paths with loops
        # The parameter allow_maybe_satisfiable controls how strict the
        #  the satisfiability criteria is honored.
        #  If allow_maybe_satisfiable is False (the default)
        #  then only transitions which are definitely satisfiable
        #  are traversed.  i.e., the type-descriptor labeling the transition
        #  is td.inhabited() returns True.
        #  However, lack of such a path does not guarantee that there
        #  is no accepting path, because there might be a transition such as satisfies-f
        #  for which we do not know if the type is inhabited.
        #  if allow_maybe_satisfiable is true, then we also traverse such
        #  transitions.    If this relaxed search yields no path from initial state
        #  to a final state, then there is definitely no accepting path, and
        #  the language of the Dfa is empty.
        from genus.utils import flat_map

        def acceptable(td: SimpleTypeD) -> bool:
            inh = td.inhabited()
            if inh is True:
                return True
            elif allow_maybe_satisfiable is False:
                return False
            elif inh is None:
                return True
            else:
                return False

        def extend_path_1(path: List[State]) -> List[List[State]]:
            tail = path[-1]
            return [path + [self.states[qid]]
                    for td in tail.transitions
                    for qid in [tail.transitions[td]]
                    if self.states[qid] not in path  # avoid loops
                    if acceptable(td)
                    ]

        def extend_paths_1(paths: List[List[State]]) -> List[List[State]]:
            return flat_map(extend_path_1, paths)

        def extend_paths(paths: List[List[State]]) -> List[List[State]]:
            if not paths:
                return paths
            else:
                return [p for p in paths if p[-1].accepting] + extend_paths(extend_paths_1(paths))

        initials = [[self.states[0]]]
        return extend_paths(initials)

    def vacuous(self) -> Optional[bool]:
        # this function returns True, False, or None.
        #   True ==> there is no accepting path from initial state to final state
        #   False ==> There is an accepting path from initial state to final state
        #   None ==> There may be an accepting path, but we can neither verify nor falsify
        #            because every path between initial and final contains at least one
        #            label, td, for which td.inhabited() returns None (i.e., dont-know).
        if not self.states:
            return True
        # if every state is non-accepting then the dfa is vacuous
        elif all(not q.accepting for q in self.states):
            return True
        # otherwise if there is not satisfiable path to an accepting state
        #   then it is vacuous.
        elif self.paths_to_accepting(allow_maybe_satisfiable=False):
            return False  # there is an accepting path, so not vacuous
        elif self.paths_to_accepting(allow_maybe_satisfiable=True):
            return None
        else:
            return False

    def inhabited(self) -> Optional[bool]:
        v = self.vacuous()
        if v is None:
            return None
        else:
            return not v

    def find_hopcroft_partition(self) -> List[EqvClass]:
        from genus.utils import split_eqv_class, flat_map, fixed_point, find_eqv_class, group_by
        from genus.s_empty import SEmpty
        finals = tuple([q for q in self.states if q.accepting])
        non_finals = tuple([q for q in self.states if not q.accepting])
        pi_0 = split_eqv_class(finals, lambda q: self.exit_map[q.index]) + [non_finals]

        def refine(partition: List[EqvClass]) -> List[EqvClass]:
            def phi(source_state: State, label: SimpleTypeD) -> Optional[EqvClass]:
                return find_eqv_class(partition, self.delta(source_state, label))

            def Phi_1(s) -> List[Tuple[SimpleTypeD, Optional[EqvClass]]]:
                return [(label, phi(s, label)) for label in s.transitions]

            def Phi(s) -> Tuple[Tuple[SimpleTypeD, EqvClass], ...]:
                grouped = group_by(lambda v: tuple(v[1]), Phi_1(s))
                vec = [(label, k) for k in grouped
                       # k is a Tuple[State]
                       for pairs in [grouped[k]]
                       for labels in [[a for a, _ in pairs]]
                       for label in [reduce(self.combine_labels, labels, SEmpty)]]
                return tuple(vec)

            def repartition(eqv_class: EqvClass) -> List[EqvClass]:
                return split_eqv_class(eqv_class, Phi)

            return [tuple(eqv_class) for eqv_class in flat_map(repartition, partition)]

        return fixed_point(pi_0, refine, lambda a, b: a == b)

    def minimize(self) -> 'Dfa':
        from genus.utils import find_eqv_class
        from genus.s_or import createSOr

        def min_int(a: int, b: int) -> int:
            return a if a < b else b

        def min_state(eqv_class) -> int:
            # using min_int with reduce, rather than int, because otherwise
            # mypy cannot figure out the min_state returns int.
            return reduce(min_int, [q.index for q in eqv_class])

        pi_minimized = self.find_hopcroft_partition()
        ids: List[int] = [min_state(eqv_class) for eqv_class in pi_minimized]
        ids_map: Dict[EqvClass, int] = dict(zip(pi_minimized, ids))  # map eqv_class -> old_state_id

        def merge_parallel(transitions):
            return self.combine_parallel_triples(transitions, lambda labels: createSOr(labels).canonicalize())

        def new_id(old_state):
            assert isinstance(old_state, State) or isinstance(old_state, int)
            if isinstance(old_state, State):
                return ids_map[find_eqv_class(pi_minimized, old_state)]
            else:
                return new_id(next(q for q in self.states if q.index == old_state))

        new_fids: List[int] = [idx for idx, eqv_class in zip(ids, pi_minimized)
                               if any(q.accepting for q in eqv_class)]
        new_exit_map = dict([(new_id(f), self.exit_map[f]) for f in self.exit_map])
        new_transitions = [(src, label, dst) for eqv_class in pi_minimized
                           for q in [eqv_class[0]]
                           for src in [new_id(q)]
                           for label in q.transitions
                           for dst in [new_id(q.transitions[label])]
                           ]
        return createDfa(self.pattern,
                         merge_parallel(new_transitions),
                         new_fids,
                         new_exit_map,
                         self.combine_labels)

    def sxp(self, dfa2, f_arbitrate_accepting, f_arbitrate_exit_value) -> 'Dfa':
        from genus.s_and import SAnd
        from genus.genus_types import NormalForm
        dfa1 = self  # IDE warns if I name the parameter dfa1 rather than self. :-(

        def compute_cross_transitions(src1, src2):
            state1 = next(q for q in dfa1.states if src1 == q.index)
            state2 = next(q for q in dfa2.states if src2 == q.index)
            return [((src1, src2), label_sxp, (dst1, dst2))
                    for label1 in state1.transitions
                    for dst1 in [state1.transitions[label1]]
                    for label2 in state2.transitions
                    for dst2 in [state2.transitions[label2]]
                    if label1.disjoint(label2) is not True  # continue if not-disjoint or if dont-know
                    for label_sxp in [SAnd(label1, label2).canonicalize(NormalForm.DNF)]
                    if label_sxp.inhabited is not False  # continue if is inhabited or if dont-know
                    ]

        def compute_all_cross_transitions():
            triples = compute_cross_transitions(0, 0)
            done_pairs = {(0, 0)}
            i = 0
            while i < len(triples):
                _, label, (dst1, dst2) = triples[i]
                if (dst1, dst2) not in done_pairs:
                    triples.extend(compute_cross_transitions(dst1, dst2))
                    done_pairs.add((dst1, dst2))
                i = i + 1
            return triples

        cross_transitions = compute_all_cross_transitions()
        cross_states = sorted(list(set([i for src, _, dst in cross_transitions
                                        for i in [src, dst]])))
        cross_state_to_new_id = dict([(cross_states[i], i) for i in range(len(cross_states))])
        transition_triples = [(cross_state_to_new_id[src],
                               label,
                               cross_state_to_new_id[dst])
                              for src, label, dst in cross_transitions]
        accepting_states = [cross_state_to_new_id[(id1, id2)]
                            for id1, id2 in cross_state_to_new_id
                            for q1 in [next(q for q in dfa1.states if id1 == q.index)]
                            for q2 in [next(q for q in dfa2.states if id2 == q.index)]
                            if f_arbitrate_accepting(q1.accepting, q2.accepting)]

        def compute_exit_value(q1, q2):
            if q1.accepting and q2.accepting:
                return f_arbitrate_exit_value(q1, q2)
            elif q1.accepting and not q2.accepting:
                return dfa1.exit_map[q1.index]
            elif q2.accepting and not q1.accepting:
                return dfa2.exit_map[q2.index]
            else:
                return f_arbitrate_exit_value(q1, q2)

        exit_map = [(cross_state_to_new_id[(id1, id2)], compute_exit_value(q1, q2))
                    for id1, id2 in cross_state_to_new_id
                    if cross_state_to_new_id[(id1, id2)] in accepting_states
                    for q1 in [next(q for q in dfa1.states if id1 == q.index)]
                    for q2 in [next(q for q in dfa2.states if id2 == q.index)]
                    ]
        return createDfa(pattern=None,
                         transition_triples=transition_triples,
                         accepting_states=accepting_states,
                         exit_map=dict(exit_map),
                         combine_labels=dfa1.combine_labels)

    def equivalent(self, dfa2) -> Optional[bool]:
        # returns True, False, or None
        return self.xor(dfa2).vacuous()

    def union(self, dfa2) -> 'Dfa':
        return self.sxp(dfa2,
                        lambda a, b: a or b,
                        lambda q1, _: self.exit_map[q1.index])

    def intersection(self, dfa2) -> 'Dfa':
        return self.sxp(dfa2,
                        lambda a, b: a and b,
                        lambda q1, _: self.exit_map[q1.index])

    def xor(self, dfa2) -> 'Dfa':
        return self.sxp(dfa2,
                        lambda a, b: (a and not b) or (b and not a),
                        lambda q1, _: self.exit_map[q1.index])


def reconstructLabels(path: List[State]) -> Optional[List[SimpleTypeD]]:
    # path is a list of states which form a path through (or partially through)
    # a Dfa
    def connecting_label(q1, q2):
        for td in q1.transitions:
            qid = q1.transitions[td]
            if qid == q2.index:
                return td
        return None

    if len(path) < 2:
        return None
    else:
        return [connecting_label(path[i], path[i + 1]) for i in range(len(path) - 1)]


def rte_to_dfa(rte: Rte, exit_value: Any = True) -> Dfa:
    from genus.s_or import createSOr
    rtes, transitions = rte.derivatives()
    # transitions is a vector of sequences, each sequence contains pairs (SimpleTypeD,int)
    transition_triples = [(src, td, dst)
                          for src in range(len(transitions))
                          for td, dst in transitions[src]
                          ]

    def combine_labels(td1, td2):
        return createSOr([td1, td2]).canonicalize()

    accepting_states = [i for i in range(len(rtes)) if rtes[i].nullable()]
    return createDfa(pattern=rte,
                     transition_triples=transition_triples,
                     accepting_states=accepting_states,
                     exit_map=dict([(i, exit_value) for i in accepting_states]),
                     combine_labels=combine_labels)


def createDfa(pattern: Optional[Rte],
              transition_triples: List[Tuple[int, SimpleTypeD, int]],
              accepting_states: Optional[List[int]],
              exit_map: Optional[Dict[int, Any]],
              combine_labels: Callable[[SimpleTypeD, SimpleTypeD], SimpleTypeD]) -> 'Dfa':
    from functools import reduce

    assert isinstance(accepting_states, list)
    for i in accepting_states:
        assert isinstance(i, int)
        assert i >= 0
    # every destination in the given transition_triples, but be mentioned
    #  in the sources, but a source need not be mentioned in the destinations
    srcs = [src for src, _, _ in transition_triples]
    for src, td, dst in transition_triples:
        assert dst in srcs, f"invalid transition {(src,td,dst)} because {dst} is not a given state"

    def f(acc: int, triple: Tuple[int, Any, int]) -> int:
        src, _, dst = triple
        return max(acc, src, dst)

    max_index = reduce(f, transition_triples, 0)

    def merge_tds(dst1: int, transitions: List[Tuple[SimpleTypeD, int]]) -> SimpleTypeD:
        assert transitions, "merge_tds expected transitions to be non-empty"
        tds = [td for td, dst2 in transitions if dst1 == dst2]
        return reduce(combine_labels, tds)

    def make_state(i: int) -> State:
        transitions_pre = [(td, dst) for src, td, dst in transition_triples if src == i]
        # error if a td appears more than once.
        #   we would like to error if the tds are not disjoint, but this is already
        #   checked in State initialization
        tds = [td for td, _ in transitions_pre]
        assert len(tds) == len(set(tds)), f"transitions from state {i} are ambiguous: {transition_triples}"
        destinations = list(set([dst for _, dst in transitions_pre]))

        if transitions_pre:
            transitions = dict([(merge_tds(dst, transitions_pre), dst) for dst in destinations])
            return State(index=i,
                         initial=i == 0,
                         accepting=i in accepting_states,
                         pattern=None,
                         transitions=transitions)
        else:
            return createSinkState(i)

    states = [make_state(i) for i in range(1 + max_index)]
    return Dfa(pattern=pattern,
               states=states,
               exit_map=exit_map,
               combine_labels=combine_labels)
