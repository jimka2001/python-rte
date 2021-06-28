import random
import math

from s_top import STop
from s_empty import SEmpty
from s_custom import SCustom
from s_and import SAnd
from s_or import SOr
from s_not import SNot
from s_member import SMember
from s_eql import SEql
from s_atomic import SAtomic
from genus_types import createSAnd, createSOr


class depth_generator(object):
    """docstring for depth_generator"""

    depth_adders = ["SNot", "SAnd", "SOr"]
    leaves = ["SCustom", "STop", "SEmpty"]

    def __init__(self, k):
        if k < 1:
            raise ValueError("Depth has to be of at least 1")
        super(depth_generator, self).__init__()
        self.k = k

    def rand_lambda_str_generator(self):
        rand_k = random.randint(1, int(math.pow(2, self.k)))
        return lambda x: isinstance(x, int) and x % rand_k == 0, "mod" + str(rand_k)

    def _generate_tree(self, c):
        curr_depth = c - 1
        if curr_depth == 0:
            rand_choice = random.choice(self.leaves)
            if rand_choice == "SCustom":
                oracle, printable = self.rand_lambda_str_generator()
                return SCustom(oracle, printable)
            elif rand_choice == "STop":
                return STop
            else:
                return SEmpty
        else:
            rand_choice = random.choice(self.depth_adders)
            if rand_choice == "SNot":
                return SNot(self._generate_tree(curr_depth))
            else:
                rand_k = random.randint(0, 3)
                tds = [self._generate_tree(curr_depth) for _i in range(rand_k)]
                return createSAnd(tds) if rand_choice == "SAnd" else createSOr(tds)

    def generate_tree(self):
        return self._generate_tree(self.k)


class TestA:
    pass


class Test1(TestA):
    pass


class TestB:
    pass


class Test2(TestA, TestB):
    pass


leaf_tds = [STop,
            SEmpty,
            SEql(1),
            SEql(0),
            SEql(-1),
            SEql(3.14),
            SEql(""),
            SEql("a"),
            SMember(),
            SMember(1, 2, 3),
            SMember("a", "b", "c"),
            SAtomic(int),
            SAtomic(float),
            SAtomic(Test1),
            SAtomic(Test2),
            SAtomic(TestA),
            SAtomic(TestB),
            SCustom(lambda a: isinstance(a, int) and a % 2 == 0, "even"),
            SCustom(lambda a: isinstance(a, int) and a % 2 == 1, "odd")
            ]

test_values = [True, False, None,
               -2, -1, 0, 1, 2, 3,
               "", "a", "b", "c", "d",
               Test1(), Test2(),
               3.14, -1.1,
               ]


def random_type_designator(depth):
    def random_and():
        return SAnd(random_type_designator(depth - 1),
                    random_type_designator(depth - 1))

    def random_or():
        return SOr(random_type_designator(depth - 1),
                   random_type_designator(depth - 1))

    def random_not():
        return SNot(random_type_designator(depth - 1))

    def random_fixed():
        return random.choice(leaf_tds)

    if depth <= 0:
        return random_fixed()
    else:
        randomizer = random.choice([random_and, random_or, random_not, random_fixed])
        return randomizer()
