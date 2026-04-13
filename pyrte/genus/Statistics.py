# Copyright (c) 2021 EPITA Research and Development Laboratory
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

from genus import simple_type_d
from genus.depthgenerator import random_type_designator
from genus.depthgenerator import random_type_designator_filter


def measureSubtypeComputability(n, depth, inh):
    if n <= 0:
        print(f"measureSubtypeComputability does not support n={n}")
    else:
        m = {
            "inhabited": 0,
            "inhabited DNF": 0,
            "equal": 0,
            "subtype True": 0,
            "subtype False": 0,
            "subtype Some": 0,
            "subtype None": 0,
            "subtype DNF True": 0,
            "subtype DNF False": 0,
            "subtype DNF Some": 0,
            "subtype DNF None": 0,
            # how many were not computed `a` original but became computable after DNF
            "gained": 0,
            # how many lost computability after DNF
            "lost": 0
        }

        for i in range(0, n):
            if inh:
                rt1 = random_type_designator_filter(depth, lambda td: td.inhabited() is True)
                rt2 = random_type_designator_filter(depth, lambda td: td.inhabited() is True
                                                                      and td.typeEquivalent(rt1) is False)
            else:
                rt1 = random_type_designator(depth)
                rt2 = random_type_designator(depth)

            can1 = rt1.canonicalize(simple_type_d)
            can2 = rt2.canonicalize(simple_type_d)

            s1 = rt1.subtypep(rt2)
            s2 = can1.subtypep(can2)

            m["inhabited"] += 1 if rt1.inhabited() is True else 0
            m["inhabited DNF"] += 1 if can1.inhabited() is True else 0
            m["equal"] += 1 if can1.typeEquivalent(can2) is True else 0
            m["subtype True"] += 1 if s1 is True else 0
            m["subtype False"] += 1 if s1 is False else 0
            m["subtype Some"] += 1 if s1 is not None else 0
            m["subtype None"] += 1 if s1 is None else 0
            m["subtype DNF True"] += 1 if s2 is True else 0
            m["subtype DNF False"] += 1 if not s2 else 0
            m["subtype DNF Some"] += 1 if s2 is not None else 0
            m["subtype DNF None"] += 1 if s2 is None else 0
            m["gained"] += 1 if s1 is None and s2 is not None else 0
            m["lost"] += 1 if s1 is not None and s2 is None else 0

        for key, value in m.items():
            m[key] = 100 * float(value) / n
        return m


def main():
    p = measureSubtypeComputability(1000, 4, True)
    for k, v in p.items():
        print(str(k) + " = " + str(v))
