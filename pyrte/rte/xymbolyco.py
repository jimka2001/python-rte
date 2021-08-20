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
                 canonicalized=None,
                 states=[createSinkState(0)],
                 exit_map=dict([]),
                 combine_labels=default_combine_labels):
        assert pattern is None or isinstance(pattern, Rte)
        assert canonicalized is None or isinstance(canonicalized, Rte)
        assert isinstance(states, list)
        for st in states:
            assert isinstance(st, State)
        assert isinstance(exit_map, dict)
        for i in exit_map:
            assert isinstance(i, int)
            assert i >= 0
        assert callable(combine_labels)
        self.pattern = pattern  # Rte
        self.canonicalized = canonicalized  # bool
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


def createDfa(transition_triples, accepting_states, exit_map, combine_labels):
    from functools import reduce

    def f(acc,triple):
        src, _, dst = triple
        return max(acc, src, dst)

    max_index = reduce(f,transition_triples,0)

    def make_state(i):
        transitions = dict([(td,dst) for src,td,dst in transition_triples if src == i])
        if transitions:
            return State(index=i,
                         initial= i == 0,
                         accepting= i in accepting_states,
                         pattern=None,
                         transitions=transitions)
        else:
            return createSinkState(i)

    states = [make_state(i) for i in range(1+max_index)]
    return Dfa(states=states,
               exit_map=exit_map,
               combine_labels=combine_labels)
