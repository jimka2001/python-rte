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

# python-rte

This project implements rational type expressions (RTEs) for the 
Python programming language.
The implementation is based on a similar package for 
[Common Lisp](https://lisp-lang.org).
The theory of how RTEs work can be found here: 
[Type-Checking of Heterogeneous Sequences in Common Lisp](https://www.lrde.epita.fr/wiki/Publications/newton.16.els) and [Representing and Computing with Types in Dynamically Typed Languages](https://www.lrde.epita.fr/wiki/Publications/newton.18.phd)

## Installation

Download from [LRDE](https://www.lrde.epita.fr/wiki/Home) GitLab 

```
git clone git@gitlab.lrde.epita.fr:jnewton/python-rte.git
```
 or
```
git clone https://gitlab.lrde.epita.fr/jnewton/python-rte.git
```

## RTE in more depth

* [Genus: A Simple Extensible Type System](doc/genus.md)


## Usage


## Not yet implemented

There are several outstanding issues.  
[See them here](https://gitlab.lrde.epita.fr/jnewton/python-rte/-/issues).

## Package dependencies overview

##Coverage tool
To run the coverage tool you need to use the "coverage run -m unittest tests\genus_tests.py" 
command on the terminal and then "coverage report" for the result. You can
also use "coverage html" to have more readable results.

## Contributors

[Jim Newton](https://www.lrde.epita.fr/wiki/User:Jnewton)
[Mehdi Oueslati](https://www.linkedin.com/in/mehdi-oueslati/)

[Release Notes](doc/release-notes.md)

## License
```
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
```

<!--  LocalWords:  
 -->
<!--  LocalWords:  
 -->
