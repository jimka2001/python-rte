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


def genSigmaStar():
    from rte.r_sigma import Sigma
    from rte.r_star import Star
    return Star(Sigma)


sigmaStar = genSigmaStar()


def genSigmaSigmaStarSigma():
    from rte.r_sigma import Sigma
    from rte.r_cat import Cat
    return Cat(Sigma, Sigma, sigmaStar)


sigmaSigmaStarSigma = genSigmaSigmaStarSigma()


def genNotSigma():
    from rte.r_epsilon import Epsilon
    from rte.r_or import Or
    return Or(sigmaSigmaStarSigma, Epsilon)


notSigma = genNotSigma()


def genNotEpsilon():
    from rte.r_cat import Cat
    from rte.r_sigma import Sigma
    return Cat(Sigma, sigmaStar)


notEpsilon = genNotEpsilon()
sigmaSigmaStar = notEpsilon


def genSingletonSTop():
    from rte.r_singleton import Singleton
    from genus.s_top import STop
    return Singleton(STop)


singletonSTop = genSingletonSTop()


def genSingletonSEmpty():
    from rte.r_singleton import Singleton
    from genus.s_empty import SEmpty
    return Singleton(SEmpty)


singletonSEmpty = genSingletonSEmpty()
