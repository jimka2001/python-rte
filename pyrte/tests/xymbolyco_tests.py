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

import unittest
from rte.r_sigma import Sigma
from rte.r_emptyset import EmptySet
from rte.r_star import Star
from rte.r_and import And
from rte.r_or import Or, Xor
from rte.r_singleton import Singleton
from rte.r_not import Not
from rte.r_cat import Cat
from rte.r_random import random_rte
from genus.s_eql import SEql
from genus.s_top import STop
from genus.s_member import SMember
from genus.s_atomic import SAtomic
from genus.s_or import SOr
from genus.s_not import SNot

# default value of num_random_tests is 1000, but you can temporarily edit this file
#   and set it to a smaller number for a quicker run of the tests.
num_random_tests = 1000


class XymbolycoCase(unittest.TestCase):

    def test_createDfa(self):
        from rte.xymbolyco import createDfa
        for depth in range(4):
            for r in range(num_random_tests):
                rt = random_rte(depth)
                pattern, transitions, accepting, exit_map, combine_labels = rt.to_dfa(depth * 10).serialize()
                self.assertTrue(createDfa(pattern=pattern,
                                          transition_triples=transitions,
                                          accepting_states=accepting,
                                          exit_map=exit_map,
                                          combine_labels=combine_labels))

    def test_createDfaDeterminist(self):
        # test to make sure an exception is thrown if we try to create a Dfa
        # using createDfa with non-disjoint transitions.
        from rte.xymbolyco import createDfa
        from genus.simple_type_d import SimpleTypeD
        from genus.s_or import createSOr

        try:
            createDfa(pattern=None,
                      transition_triples=[(0, SOr(SAtomic(int), SAtomic(float)), 1),
                                          (0, SAtomic(int), 2),
                                          (1, STop, 3),
                                          (2, STop, 3),
                                          (3, STop, 3)],
                      accepting_states=[3],
                      exit_map={3: True})
        except AssertionError:
            pass
        else:
            self.fail('Expected exception because of non-disjoint transitions')

        try:
            createDfa(pattern=None,
                      transition_triples=[(0, SAtomic(float), 1),
                                          (0, SAtomic(int), 2),
                                          (1, STop, 3),
                                          (2, STop, 3),
                                          (3, STop, 3)],
                      accepting_states=[3],
                      exit_map={3: True})
        except AssertionError:
            self.fail('Expected no exception because of non-disjoint transitions')
        else:
            pass

    def test_extract_discovered_case_57(self):
        from genus.depthgenerator import Test2
        so = Singleton(SEql(1))

        for rt in [Cat(Not(EmptySet), Star(so)),
                   Cat(Star(Sigma), Star(so)),
                   Cat(Not(EmptySet), Star(Singleton(SAtomic(int)))),
                   Cat(Star(Not(EmptySet)), Star(Singleton(SAtomic(int)))),
                   Cat(Star(Not(EmptySet)), Star(Singleton(SAtomic(Test2)))),
                   Singleton(SNot(SOr(STop, SMember())))
                   ]:
            self.check_extraction_cycle(rt)

    def check_extraction_cycle(self, rt):
        from rte.xymbolyco import reconstructLabels
        rt1 = rt  # .canonicalize()
        extracted = rt1.to_dfa(True).to_rte()
        if extracted[True]:
            rt2 = extracted[True]
            # compute xor, should be empty set if rt1 is equivalent to rt2
            empty1 = Xor(rt1, rt2)
            empty_dfa = empty1.to_dfa(True)

            if empty_dfa.vacuous():
                label_path = None
            else:
                label_path = reconstructLabels(empty_dfa.paths_to_accepting()[0])
            self.assertTrue(empty_dfa.vacuous(),
                            f"\nrt1={rt1}\n" +
                            f"rt2={rt2}\n" +
                            f"empty={empty1}\n" +
                            f"path={label_path}"
                            )

    def test_extract_rte(self):
        for depth in range(3, 4):
            for r in range(num_random_tests):
                self.check_extraction_cycle(random_rte(depth))

    def test_canonicalize(self):
        for depth in range(4):
            for _rep in range(num_random_tests):
                rt = random_rte(depth)
                can = rt.canonicalize()
                self.assertTrue(Or(And(rt, Not(can)),
                                   And(Not(rt), can)).to_dfa(True).vacuous(),
                                f"\nrt={rt}\n" +
                                f"can={can}")

    def test_discovered_103(self):
        # rt=And(Or(Or(∅, Σ), Not(Σ)), Cat(Not(ε), Not(ε)))
        # can=Cat(Σ, Σ)
        from rte.r_epsilon import Epsilon
        Σ = Sigma
        ε = Epsilon

        for rt in [Or(Σ, Not(Σ)),
                   And(Star(Σ),
                       Cat(Not(ε), Not(ε))),
                   Or(And(Σ, Cat(Not(ε), Not(ε))),
                      And(Not(Σ), Cat(Not(ε), Not(ε)))),
                   Or(EmptySet, And(Or(Cat(Σ, Σ, Star(Σ)), ε), Cat(Cat(Σ, Star(Σ)), Cat(Σ, Star(Σ))))),
                   And(Or(Cat(Σ, Σ, Star(Σ)), ε),
                       Cat(Cat(Σ, Star(Σ)), Cat(Σ, Star(Σ)))),
                   Or(And(Cat(Σ, Σ, Star(Σ)), Cat(Cat(Σ, Star(Σ)), Cat(Σ, Star(Σ)))),
                      And(ε, Cat(Cat(Σ, Star(Σ)), Cat(Σ, Star(Σ))))),
                   And(Or(Σ, Not(Σ)), Cat(Not(ε), Not(ε))),
                   And(Or(Or(EmptySet, Σ),
                          Not(Σ)),
                       Cat(Not(ε), Not(ε)))
                   ]:
            can = rt.canonicalize()
            self.assertTrue(Or(And(rt, Not(can)),
                               And(Not(rt), can)).to_dfa(True).vacuous(),
                            f"\nrt={rt}\n" +
                            f"can={can}")

    def test_discovered_113(self):
        from rte.xymbolyco import reconstructLabels
        so = Singleton(SEql(1))
        samples = [

            Or(And(Cat(Star(so),
                       And(Not(so), Sigma),
                       Star(Or(And(Not(so), Sigma),
                               Cat(so, Star(so), And(Not(so), Sigma))))),
                   Not(Cat(Star(so),
                           And(Not(so), Sigma),
                           Star(Or(And(Not(so), Sigma), Cat(so, Star(so), And(Not(so), Sigma)))),
                           Star(so))),
                   Not(Star(so))),
               And(Cat(Star(so),
                       And(Not(so), Sigma),
                       Star(Or(And(Not(so), Sigma), Cat(so, Star(so), And(Not(so), Sigma)))),
                       Star(so)),
                   Not(Cat(Star(so),
                           And(Not(so), Sigma),
                           Star(Or(And(Not(so), Sigma), Cat(so, Star(so), And(Not(so), Sigma)))))),
                   Not(Star(so)))),

            Or(Cat(so, Star(so)),
               Cat(Or(And(Not(so), Sigma),
                      Cat(so, Star(so), And(Not(so), Sigma))),
                   Star(Or(And(Not(so), Sigma),
                           Cat(so, Star(so), And(Not(so), Sigma)))),
                   Star(so))),
        ]
        for i in range(len(samples)):
            rt = samples[i]
            can = rt.canonicalize_once()
            self.assertTrue(can.to_dfa(True).simulate([2, 1]))
            self.assertTrue(rt.to_dfa(True).simulate([2, 1]))

            xor = Xor(rt, can)
            dfa = xor.to_dfa(True)
            rt.to_dfa(True).to_dot(title=f"rt-{i}", view=False, draw_sink=True)
            can.to_dfa(True).to_dot(title=f"can-{i}", view=False, draw_sink=True)
            dfa.to_dot(title=f"empty_dfa={i}", view=False, draw_sink=True)
            # self.assertTrue(dfa.simulate([2, 1]))
            paths = dfa.paths_to_accepting()
            if paths:
                example = reconstructLabels(paths[0])
            else:
                example = None
            self.assertTrue(dfa.vacuous(),
                            f"\n{i} rt={rt}\n" +
                            f" can={can}\n" +
                            f"example={example}")

    def test_find_hopcroft_partition(self):
        for depth in range(4):
            for _rep in range(num_random_tests):
                rt = random_rte(depth).canonicalize()
                dfa = rt.to_dfa(True)
                self.assertTrue(dfa.find_hopcroft_partition())

    def test_minimize(self):
        for depth in range(4):
            for _rep in range(num_random_tests):
                rt = random_rte(depth).canonicalize()
                dfa = rt.to_dfa(True)
                minimized = dfa.minimize()
                self.assertTrue(minimized)
                self.assertTrue(len(minimized.states) <= len(dfa.states))

    def test_minimize_loop(self):
        for depth in range(4):
            for _rep in range(num_random_tests):
                rt1 = random_rte(depth).canonicalize()
                dfa1 = rt1.to_dfa(True)
                rt2 = dfa1.minimize().to_rte()[True]
                self.assertTrue(Xor(rt1, rt2))

    def test_sxp_1(self):
        for depth in range(4):
            for _rep in range(num_random_tests):
                rt1 = random_rte(depth).canonicalize()
                rt2 = random_rte(depth).canonicalize()
                dfa1 = rt1.to_dfa(1)
                dfa2 = rt2.to_dfa(2)
                u = dfa1.union(dfa2)
                self.assertTrue(u)
                i = dfa1.intersection(dfa2)
                self.assertTrue(i)
                x = dfa1.xor(dfa2)
                self.assertTrue(x)

    def test_sxp_2(self):
        for depth in range(4):
            for _rep in range(num_random_tests):
                rt1 = random_rte(depth).canonicalize()
                rt2 = random_rte(depth).canonicalize()
                dfa1 = rt1.to_dfa(True)
                dfa2 = rt2.to_dfa(True)
                u = dfa1.union(dfa2)
                self.assertTrue(u.equivalent(Or(rt1, rt2).to_dfa(True)),
                                f"rt1={rt1}\n" +
                                f"rt2={rt2}\n" +
                                "union of Dfas does not correspond to dfa of union")

                i = dfa1.intersection(dfa2)
                self.assertTrue(i.equivalent(And(rt1, rt2).to_dfa(True)),
                                f"rt1={rt1}\n" +
                                f"rt2={rt2}\n" +
                                "intersection of Dfas does not correspond to dfa of intersection")

                x = dfa1.xor(dfa2)
                self.assertTrue(x.equivalent(Xor(rt1, rt2).to_dfa(True)),
                                f"rt1={rt1}\n" +
                                f"rt2={rt2}\n" +
                                "xor of Dfas does not correspond to dfa of xor")


if __name__ == '__main__':
    unittest.main()
