<!--
 Copyright (c) 2021 EPITA Research and Development Laboratory

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

# genus

Python implementation of [SETS](https://www.lrde.epita.fr/dload/papers/newton.21.els.pdf).

# Constructors

* `SAnd(td, ...)` --- The intersection of the set of specified types. `And()` is equivalent to `STop`.
* `SOr(td, ...)` --- The union of the set of specified types.  `Or()` is equivalent to `SEmpty`.
* `SAtomic(python_type)` --- The set of objects of the specified Python type.
* `SNot(td)` --- The complement of the set represented by `td`.
* `SEql(object)` --- The singleton set of the given object.  Any object of the same type which is equal according to `==`.
* `SMember(ob1, obj2, ...)` --- takes zero or more objects of any type as argument --- Equivalent to `SOr(SEql(ob1), SEql(obj2), ...)`.   `SMember()` is equivalent to `SEmpty`.
* `SSatisfies(f,text)` --- takes predicate function, and printable text as argument --- represents the set of all Python objects for which f(ob) returns a Boolean True value.
* `STop` --- set of all Python objects
* `SEmpty` --- empty set of Python objects

# Internal programmer API

Here are some of the methods which a programmer might find useful.


* `td.typep(obj)` --- test whether an object is of the designated type.
* `td1.disjoint(td2)` --- determine whether two types are disjoint, returns `True`, `False`, or `None`.
* `td.inhabited()` --- determine whether a type is inhabited as opposed to empty,  returns `True`, `False`, or `None`.
* `td1.subtypep(td2)` --- determine whether `td1` is a subtype of `td2`, returns `True`, `False`, or `None`.
* `td.compute_dnf()` --- compute a type designator to Disjunctive Normal Form.
* `td.compute_cnf()` --- compute a type designator to Conjunctive Normal Form.
* `td.canonicalize()` --- reduce a type designator to a canonical form.
* `td1.typeEquivalent(td2)` --- determine whether two types are equivalent,  returns `True`, `False`, or `None`.
* `mdtd(list_of_tds)` --- or Set of tds --- computes the Maximal
  Disjoint Type Decomposition, which is a set of disjoint type
  designators whose union is `STop`, each of which is a subtype of at
  least one of the given types.

