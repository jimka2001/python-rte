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

"""
[0-3] Advancement tracker
__init__ 3
__str__ 3
create 3
unit 3
zero 3
annihilator 1
same_combination 3
typep 3
inhabited_down 0
_disjoint_down 1
subtypep 3
canonicalize_once 0
compute_dnf 0
"""
from genus.simple_type_d import SimpleTypeD 
from genus.s_empty import SEmpty
from genus.s_top import STop
from genus.utils import generate_lazy_val

class SAnd(SimpleTypeD):
    """An intersection type, which is the intersection of zero or more types.
    @param tds list, zero or more types"""

    #equivalent to the scala "create"
    def __init__(self, tds):
        super(SAnd, self).__init__()
        self.tds = tds
    
    def __str__(self):
        s = "[And "
        for arg in self.tds:
            s += str(arg)
            s += ","
        s += "]"
        return s

    @staticmethod
    def create(tds):
        return SAnd(tds)

    unit = STop.get_omega()
    zero = SEmpty.get_epsilon()

    @staticmethod
    def annihilator(a, b):
        return b.supertypep(a)

    def same_combination(self, t):
        if not type(t) == type(self):
            return False
        for arg in self.tds:
            if not arg in t.tds:
                return False
        for arg in t.tds:
            if not arg in self.tds:
                return False
        return True

    def typep(self, a):
        return all(t.typep(a) for t in self.tds)

    def inhabited_down(self, opt):
        pass
        # dnf = generate_lazy_val(canonicalize, Dnf)
        # cnf = generate_lazy_val(canonicalize, Cnf)

        # dot_inhabited = lambda x : x.inhabited
        # inhabited_dnf = generate_lazy_val(dot_inhabited, dnf)
        # inhabited_cnf = generate_lazy_val(dot_inhabited, cnf)

        # if any(t.contains(False) for t in self.tds):
        #     return False
        # elif all(type(t) == SAtomic for t in self.tds):
        #     #TODO I may need explanations on this one
        # elif dnf() != self and inhabited_dnf():
        #     return inhabited_dnf()
        # elif cnf() != self and inhabited_cnf():
        #     return inhabited_cnf()
        # else:
        #     super()._inhabited_down

    def _disjoint_down(self, t):
        dot_inhabited_true = lambda x: x.inhabited() == True
        inhabited_t = generate_lazy_val(dot_inhabited_true, t)
        inhabited_self = generate_lazy_val(dot_inhabited_true, self)

        if any(t._disjoint_down(t)):
            return True
        elif t in self.tds and inhabited_t() and inhabited_self():
            return False
        elif inhabited_t() and inhabited_self() and any(x.subtypep(t) or t.subtypep(x) for x in self.tds):
            return False
        else:
            return super()._disjoint_down(t)

    def subtypep(self, t):
        if not self.tds:
            return STop.get_omega().subtypep(t)  
        elif t in self.tds:
            return True          
        elif hasattr(t, "typep") and any(t.typep(arg) for arg in self.tds):
            return True
        #elif hasattr(t, "inhabited") and t.inhabited() and self.inhabited() and all(x.disjoint(t) for x in self.tds):
        #    return False
        else:
            return super().subtypep(t)

    def canonicalize_once(nf):
        #TODO
        pass

    def compute_dnf():
        #TODO I need explanation for this one
        pass