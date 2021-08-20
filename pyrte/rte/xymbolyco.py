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

class State:
    def __init__(self, index, initial, accepting, pattern, transitions):
        self.index = index  # int
        self.initial = initial  # bool
        self.accepting = accepting  # bool
        self.pattern = pattern  # Rte
        self.transitions = transitions  # Map SimpleTypeD -> Int
        super().__init__()

class Dfa:
    def __init__(self, pattern, canonicalized, states, exit_map, combine_labels ):
        self.pattern = pattern  # Rte
        self.canonicalized = canonicalized  # bool
        self.states = states  # vector of State objects
        self.exit_map = exit_map  # map index -> return_value
        self.combine_labels = combine_labels  # function (SimpleTypeD,SimpleTypeD)->SimpleTypeD

    def simulate(self, sequence):
        state_id = 0
        for element in sequence :
            transitions = self.states[state_id].transitions
            itr = iter(transitions)
            state_id = next((transitions[td] for td in itr if td.typep(element)),
                            None)
            if state_id is None:
                return None

        if not self.states[state_id].accepting:
            return None
        else:
            return self.exit_map[state_id]
