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

import random
from pyrte.rte import *


leaf_rtes = [EmptySet,
             Epsilon,
             Sigma]


def random_rte(depth):
    def random_and():
        return And(random_rte(depth - 1),
                   random_rte(depth - 1))

    def random_or():
        return Or(random_rte(depth - 1),
                  random_rte(depth - 1))

    def random_cat():
        return Cat(random_rte(depth - 1),
                   random_rte(depth - 1))

    def random_not():
        return Not(random_rte(depth - 1))

    def random_singleton():
        return Singleton(random_type_designator(depth - 1))

    def random_fixed():
        return random.choice(leaf_rtes)

    if depth <= 0:
        return random_fixed()
    else:
        randomizer = random.choice([random_and, random_or, random_not,
                                    random_cat, random_singleton, random_fixed])
        return randomizer()
