# Changes since v0.1.2

* `random_type_generator` function was added.  Given a depth (integer) the function returns a randomly selected/generated type descriptor whose tree depty is at most that depth.   The global variable, `test_values` is a list of perspective values which can be used in calls to `random_type_designator(depth).typep(...)`.

* `STop` and `SEmpty` are now global variables which are intended to be single instances of the respective classes `STopImpl` and `SEmptyImpl`.  `__init__` and `__hash__` methods have been defined to enforce that two instances of `STop` or of `SEmpty` are equal to each other; However, there is also code in the `__init__` function to ensure that only one such object of each class can be instantiated.  Subsequent calls to `STopImpl.get_omega()` or `SEmptyImpl.get_epsilon()` return the same cached object.

* `SAnd` and `SOr` are now called with varargs.  e.g., `SAnd(a,b,c)` or `SOr(a,b,c)` whereas in the past they were called with a single list argument such as  `SAnd([a,b,c])` or `SOr([a,b,c])`.  The functions `createSAnd()` and `createSOr()` are the corresponding factory functions which are called with a single list argument.   However, `createSAnd` and `createSOr` only create an instance of `SAnd` or `SOr` if the length of the list is two or more.  In the degenerate case of 0 elements `createSAnd([])` returns `STop` and `createSOr([])` returns `SEmpty`, while `createSAnd([x])` and `createSOr([x])` return `x`.

* The files `utils.py` and `genus_types.py` contain lots of helper functions, some of which were previous static methods.  For example `find_simpifier` is now located in `utils.py` and is a normal function, rather than a method.

* `zero` and `unit` are now methods on `SAnd` and `SOr` rather than attributes.

* `SAnd.canonicalize()` and `SOr.canonicalize()` have been implemented via calls to the `find_simpifier` function.  Most of the work is done by the `SCombination.canonicalize()` method which preforms many so-called *conversions* in a generic work which work for `SOr` and also for `SAnd` making use of methods such as `create`, `create_dual`, `unit`, `zero`, `annihilator`, `dual_combination`, `combinator`, `dual_combinator`, `combo_filter`, 

* Many `__init__` functions now contain assertions about the types of arguments given.  For example `SAtomic()` now asserts that its argument is a class, via `assert inspect.isclass(wrapped_class)`.   `SNot`, `SAnd`, and `SOr` assert that their arguments are instances of class `SimpleTypeD`.

* The `disjoint` method on `SAtomic` has been changed to something simpler which seems to work.  Although remainign corner cases still need to be identified.  The algorithm is basically a check of the following
** are the classes equal, then, not disjoint
** is one class a subclass of the other, then not disjoint
** do the two classes have a common subclass, then not disjoint.
** otherwise they are disjoint

