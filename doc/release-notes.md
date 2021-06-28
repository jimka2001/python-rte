# Changes since v0.1.2

* I am using [PyCharm](https://www.jetbrains.com/pycharm/) to edit 
  the Python code.  PyCharm suggested lots of formatting changed, 
  99% of which I accepted.  Some of the formatting seems weird, but 
  I am supposing that it is considered idiomatic.  For example, 
  always put a space after a comma, such as `f(a, b, c)` as opposed 
  to `f(a,b,c)`.

* `random_type_generator` function was added.  Given a depth 
  (integer) the function returns a randomly selected/generated 
  type descriptor whose tree depth is at most that depth.   The 
  global variable, `test_values` is a list of perspective values 
  which can be used in calls to 
  `random_type_designator(depth).typep(...)`.

* `STop` and `SEmpty` are now global variables which are intended 
  to be single instances of the respective classes `STopImpl` and
  `SEmptyImpl`.  `__new__`  methods have been defined 
  to enforce that two instances of `STop` or of `SEmpty` are equal 
  to each other. Subsequent calls to `STopImpl()` or 
  `SEmptyImpl()` return the same cached object.

* `SAnd` and `SOr` are now called with varargs.  e.g., `SAnd(a,b,c)` 
  or `SOr(a,b,c)` whereas in the past they were called with a single 
  list argument such as  `SAnd([a,b,c])` or `SOr([a,b,c])`.  The 
  functions `createSAnd()` and `createSOr()` are the corresponding 
  factory functions which are called with a single list 
  argument.  However, `createSAnd` and `createSOr` only create an 
  instance of `SAnd` or `SOr` if the length of the list is two or 
  more.  In the degenerate case of 0 elements `createSAnd([])` 
  returns `STop` and `createSOr([])` returns `SEmpty`, while 
  `createSAnd([x])` and `createSOr([x])` return `x`.

* The files `utils.py` and `genus_types.py` contain lots of helper 
  functions, some of which were previous static methods.  For example:
  `find_simplifier` is now located in `utils.py` and is a normal 
  function, rather than a method.  Admittedly, some/many of the 
  functions in `utils.py` are not very idiomatic-Python, e.g., 
  `flat_map`, `find_first`, `search_replace`, and 
  `remove_element`.  Nevertheless, I have added these functions to 
  aid with the translation from Scala to Python.

* Refactored `generate_lazy_val`.  It now takes a 0-ary client function 
  (a thunk) and returns a 0-ary function.  The refactoring using 
  Python's closures to greatly simplify the code.  The function 
  returned by `generate_lazy_val` promises to call the client function
  at most 1 time, memoizing its return value, and thereafter if called,
  will return that same return value.

* `zero` and `unit` are now methods on `SAnd` and `SOr` rather than 
  attributes.

* `SAnd.canonicalize()` and `SOr.canonicalize()` have been implemented 
  via calls to the `find_simplifier` function.  Most of the work is done 
  by the `SCombination.canonicalize()` method which performs many 
  so-called *conversions* in a generic work which work for `SOr` and 
  also for `SAnd` making use of methods such as `create`, 
  `create_dual`, `unit`, `zero`, `annihilator`, `dual_combination`, 
  `combinator`, `dual_combinator`, `combo_filter`, 

* Many `__init__` functions now contain assertions about the types 
  of arguments given.  For example `SAtomic()` now asserts that its 
  argument is a class, via `assert inspect.isclass(wrapped_class)`.   
  `SNot`, `SAnd`, and `SOr` assert that their arguments are instances 
  of class `SimpleTypeD`.

* The `disjoint` method on `SAtomic` has been changed to something 
  simpler which seems to work--although remaining corner cases still 
  need to be identified.  The algorithm is basically a check of the 
  following

    * are the classes equal, then, not disjoint
    * is one class a subclass of the other, then not disjoint
    * do the two classes have a common subclass, then not disjoint.
    * otherwise, they are disjoint

* The utility functions `orp`, `andp`, `combop`, `notp`, `atomicp`, 
  `topp`, `empty`, `memberimplp`, `memberp`, and `eqlp` have been 
  provided as replacements for `isinstance(_,SOr)`, 
  `isinstance(_,SAnd)`, `isinstance(_,SCombination)`, etc.  
  Honestly, I don't know whether this is better or worse.

* All test cases have been moved into `all_tests.py` and many new 
  tests have been added.   Having the code in one file seems 
  compatible with PyCharm, as there is a single button displayed in 
  the IDE to run the tests.  However, the tests fail and abort on 
  first failure.   Suggest refactoring the tests into some *standard* 
  unit test platform/library.  I don't know which one to suggest.

* Added class `CallStack` as a means of debugging infinite loops.  
  The code is not perfect, but can be used to monitor whether a 
  function eventually re-calls itself with the same argument list 
  as previous pending call.

* eliminated the binary operator overloading __or__, __and__, etc.

* implemented to_cnf and t_dnf

* The Python sorting functions use a compare function which is expected
  to return -1, 0, or 1 whereas in Scala the corresponding function 
  expects a return value of True or False.  I have updated several
  functions to use the Python protocol. `compare_to_same_class_obj`,
  `compare_sequence`, and `compare_type_designators`.

* Some methods have changed name.  `_subtypep_down` changed to `subtypep_down`
  and `_inhabited_down` changed to `inhabited_down`.  This change is
  an artifact of using PyCharm which thinks that method names beginning
  with `_` are in some sense *private* and it flags many of the calls
  to the method in the current code base.

<!--  LocalWords:  PyCharm varargs Scala Refactored ary IDE
 -->
