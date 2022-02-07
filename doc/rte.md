<!--
 Copyright (c) 2022 EPITA Research and Development Laboratory

 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without restriction,
 including without limitation the rights to use, copy, modify, merge,
 publish, distribute, sublicense, and/or sell copies of the Software,
 and to permit persons to whom the Software is furnished to do so,
 subject to the following conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-->

# rte

Rtes are rational expression objects which match sequences according to the
types (in the [genus](genus.md) sense) of the sequence elements.

# Public API

* `rte.simulate(exit_value,sequence)` returns the given `exit_value` if the sequence matches the given rte, or `None` otherwise.
E.g., `Star(Singleton(SAtomic(int))).simulate(True,[1,2,3,3,2])` returns `True`.
E.g., `Star(Or(Singlegon(SAtomic(int)),Singleton(SAtomic(float)))).simulate(True,[1,2.0,3,33.0,"two"])` returns `None`.

# Constructors

* `Cat(rte, ...)` --- zero or more rtes can be given as arguments --- matches the concatenation of the languages matched by the given rtes, or matches `EmptyWord` if no rtes are given
* `And(rte, ...)` --- zero or more rtes can be given as arguments --- matches the intersection of the languages matched by the given rtes, or matches `Star(Sigma)` if no rtes are given.
* `Or(rte, ...)` --- zero or more rtes can be given as arguments --- matches the union of the languages matched by the given rtes, or matches `EmptySet` if no rtes are given.
* `Star(rte)` --- one required rte argument --- matches the Kleene start of the language of the given rte.
* `Not(rte)` --- one required rte argument --- matches the complement of the language of the given rte.  I.e., matches all sequences in `Star(Sigma)` but which are not matched by `rte`.
* `Singleton(td)` --- td is an object of type `SimpleTypeD` --- matches the set of singleton sequences for which the sequence element is of type `td` according to `td.typep(...)`.
* `Sigma` --- matches the set of singleton sequences.
* `EmptySet` --- matches the empty set of sequences
* `Epsilon` --- matches the set containing the empty sequence.

# Internal programmer API

Here are some of the methods which a programmer might find useful.

* `rte.canonicalize()` --- reduce an rte to a canonicalized form
* `rte.to_dot(...)` --- great a graphical (graphviz) representation of the Dfa of the rte.
* `rte.to_dfa(...)` --- generate a Dfa from this rte
* `rte.inhabited(...)` --- compute whether the language matched by the rte is inhabited as opposed to vacuous.
* `rte.equivalent(rte2)` --- determine whether two given rtes match the same language.
* `random_rte(depth)` --- construct a randomly generated rte of the given depth; useful for testing.
