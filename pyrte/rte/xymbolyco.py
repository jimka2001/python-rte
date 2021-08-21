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
from genus.simple_type_d import SimpleTypeD


class State:
    def __init__(self, index, initial, accepting, pattern, transitions):
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
        super().__init__()


def createSinkState(index):
    from genus.s_top import STop

    return State(index=index,
                 initial=(index == 0),
                 accepting=False,
                 pattern=None,
                 transitions={STop: index})


def default_combine_labels(l1, l2):
    raise Exception('Missing combine_labels for Dfa')


class Dfa:
    def __init__(self,
                 pattern=None,
                 states=[createSinkState(0)],
                 exit_map=dict([]),
                 combine_labels=default_combine_labels):
        assert pattern is None or isinstance(pattern, Rte)
        assert isinstance(states, list)
        for st in states:
            assert isinstance(st, State)
        assert isinstance(exit_map, dict)
        for i in exit_map:
            assert isinstance(i, int)
            assert i >= 0
        assert callable(combine_labels)
        self.pattern = pattern  # Rte
        self.states = states  # vector of State objects
        self.exit_map = exit_map  # map index -> return_value
        self.combine_labels = combine_labels  # function (SimpleTypeD,SimpleTypeD)->SimpleTypeD

    def simulate(self, sequence):
        state_id = 0
        for element in sequence:
            transitions = self.states[state_id].transitions
            itr = iter(transitions)
            state_id = next((transitions[td] for td in itr if td.typep(element)),
                            None)
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

    def find_sink_states(self):  # returns a list of integers
        from genus.s_top import STop
        return [q.index for q in self.states
                if not q.accepting
                and 1 == len(q.transitions)
                and q.transitions[STop] == q.index]

    def complete(self):
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

    def complement(self, exit_map):
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

    def trim(self):
        # TODO implement trimming
        return self

    def minimize(self):
        # TODO implement minimization
        return self

    def extract_rte(self):
        from functools import reduce
        from rte.r_epsilon import Epsilon
        from rte.r_singleton import Singleton
        from rte.r_or import createOr
        from rte.r_cat import createCat
        from rte.r_star import Star
        from genus.utils import stringify
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

        # step 2
        _, old_transition_triples, accepting, _, _ = dfa.serialize()
        old_transitions = [(src, Singleton(td), dst) for src, td, dst in old_transition_triples]
        # step 3  # adding state whose index is NOT integer
        new_initial_transitions = [("I", Epsilon, 0)]
        # step 4  # adding state whose index is NOT integer
        new_final_transitions = [(qid, Epsilon, ("F", self.exit_map[qid])) for qid in accepting]

        def combine_parallel_labels(rtes):
            return createOr(rtes).canonicalize()

        def extract_labels(triples):
            return [l for _, l, _ in triples]

        def combine_parallel(triples):
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

        def eliminate_state(triples, qid):
            def f(acc, triple):
                x_to_q, q_to_q, q_to_x, others = acc
                src, _, dst = triple
                if src == qid and dst == qid:
                    return x_to_q, q_to_q+[triple], q_to_x, others
                elif src == qid:
                    return x_to_q, q_to_q, q_to_x+[triple], others
                elif dst == qid:
                    return x_to_q+[triple], q_to_q, q_to_x, others
                else:
                    return x_to_q, q_to_q, q_to_x, others+[triple]

            # step 6
            x_to_q, q_to_q, q_to_x, others = reduce(f, triples, ([], [], [], []))

            # step 7
            self_loop_label = combine_parallel_labels(extract_labels(q_to_q))
            # step 8
            new_triples = [(src, lab, dst)
                           for src, pre_label, _ in combine_parallel(x_to_q)
                           for _, post_label, dst in combine_parallel(q_to_x)
                           for lab in [createCat([pre_label,
                                                  Star(self_loop_label),
                                                  post_label]
                                                 ).canonicalize()]
                           ]
            return others + new_triples  # from eliminate_state

        # step 5 and 9
        new_transition_triples = reduce(eliminate_state,
                                        # we eliminate all states whose id is an integer,
                                        #  recall we have added states with id ("F",?) and also with
                                        #  id "I".  These will remain.
                                        range(len(self.states)),
                                        new_initial_transitions + old_transitions + new_final_transitions)
        exit_values = list(set([self.exit_map[qid] for qid in accepting]))
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
        d = [(exit_value,combine_parallel_labels(labels).canonicalize())
             for exit_value, labels in els]
        return dict(d)

    def to_rte(self):
        from rte.r_emptyset import EmptySet
        extracted = self.extract_rte()
        if extracted:
            return extracted
        else:
            return dict([(True, EmptySet)])


def createDfa(pattern, transition_triples, accepting_states, exit_map, combine_labels):
    from functools import reduce

    assert isinstance(accepting_states, list)
    for i in accepting_states:
        assert isinstance(i, int)
        assert i >= 0

    def f(acc, triple):
        src, _, dst = triple
        return max(acc, src, dst)

    max_index = reduce(f, transition_triples, 0)

    def merge_tds(dst1, transitions):
        assert transitions, "merge_tds expected transitions to be non-empty"
        tds = [td for td, dst2 in transitions if dst1 == dst2]
        return reduce(combine_labels, tds)

    def make_state(i):
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
