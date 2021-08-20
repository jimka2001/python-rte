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

        return [transitions(), accepting(), exit_map(), self.combine_labels]
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

def createDfa(pattern, transition_triples, accepting_states, exit_map, combine_labels):
    from functools import reduce

    assert isinstance(accepting_states,list)
    for i in accepting_states:
        assert isinstance(i,int)
        assert i >= 0

    def f(acc,triple):
        src, _, dst = triple
        return max(acc, src, dst)

    max_index = reduce(f,transition_triples,0)

    def merge_tds(dst1,transitions):
        assert transitions, "merge_tds expected transitions to be non-empty"
        tds = [td for td, dst2 in transitions if dst1 == dst2]
        return reduce(combine_labels, tds)

    def make_state(i):
        transitions_pre = [(td,dst) for src,td,dst in transition_triples if src == i]
        # error if a td appears more than once.
        #   we would like to error if the tds are not disjoint, but this is already
        #   checked in State initialization
        tds = [td for td, _ in transitions_pre]
        assert len(tds) == len(set(tds)), f"transitions from state {i} are ambiguous: {transition_triples}"
        destinations = list(set([dst for _, dst in transitions_pre]))

        if transitions_pre:
            transitions = dict([(merge_tds(dst, transitions_pre), dst) for dst in destinations])
            return State(index=i,
                         initial= i == 0,
                         accepting= i in accepting_states,
                         pattern=None,
                         transitions=transitions)
        else:
            return createSinkState(i)

    states = [make_state(i) for i in range(1+max_index)]
    return Dfa(pattern=pattern,
               states=states,
               exit_map=exit_map,
               combine_labels=combine_labels)
