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
from rte.r_rte import Rte
from rte.r_and import And
from rte.r_cat import Cat
from rte.r_emptyset import EmptySet
from rte.r_epsilon import Epsilon
from rte.r_not import Not
from rte.r_or import Or
from rte.r_sigma import Sigma
from rte.r_singleton import Singleton
from rte.r_star import Star
from genus.depthgenerator import random_type_designator

leaf_rtes = [EmptySet,
             Epsilon,
             Sigma]


def random_list(length: int, f) -> list:
    return [f()
            for _ in range(length)]


def random_rte(depth: int) -> Rte:
    def random_and():
        args = random_list(random.randint(0, 4),
                           lambda: random_rte(depth - 1))
        return And(*args)

    def random_or():
        args = random_list(random.randint(0, 4),
                           lambda: random_rte(depth - 1))
        return Or(*args)

    def random_cat():
        args = random_list(random.randint(0, 4),
                           lambda: random_rte(depth - 1))
        return Cat(*args)

    def random_not():
        return Not(random_rte(depth - 1))

    def random_star():
        return Star(random_rte(depth - 1))

    def random_singleton():
        return Singleton(random_type_designator(depth - 1))

    def random_fixed():
        return random.choice(leaf_rtes)

    if depth <= 0:
        return random_fixed()
    else:
        randomizer = random.choice([random_and, random_or, random_not,
                                    random_star,
                                    random_cat, random_singleton, random_fixed])
        return randomizer()
