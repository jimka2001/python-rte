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
__init__ 1
__str__ 1
create 1
unit 1
zero 1
annihilator 1
same_combination 1
typep 1
inhabited_down 0
_disjoint_down 1
subtypep 1
canonicalize_once 0
compute_dnf 0
"""
import simple_type_d
import utils

class SAnd(SimpleTypeD):
	"""An intersection type, which is the intersection of zero or more types.
    @param tds list, zero or more types"""

	#equivalent to the scala "create"
	def __init__(self, tds):
		super(SAnd, self).__init__()
		self.tds = tds
	
	def __str__(self):
		s = "["
		for arg in self.arg_list:
			s += str(arg)
			s += ","
		s += "]"
		return s

    @staticmethod
    def create(tds):
        return SAnd(tds)

	unit = STop
    zero = SEmpty

    @staticmethod
    def annihilator(a, b):
        return b.supertypep(a)

    @staticmethod
    def same_combination(td):
        return type(td) == SAnd

    def typep(a):
        return any(t.typep(a) for t in self.tds)

    def inhabited_down(self, opt):

        dnf = generate_lazy_val(canonicalize, Dnf)
        cnf = generate_lazy_val(canonicalize, Cnf)

        dot_inhabited = lambda x : x.inhabited
        inhabited_dnf = generate_lazy_val(dot_inhabited, dnf)
        inhabited_cnf = generate_lazy_val(dot_inhabited, cnf)

        if any(t.contains(False) for t in self.tds):
            return False
        elif all(type(t) == SAtomic for t in self.tds):
            #TODO I may need explanations on this one
        elif dnf() != self and inhabited_dnf():
            return inhabited_dnf()
        elif cnf() != self and inhabited_cnf():
            return inhabited_cnf()
        else:
            super()._inhabited_down

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

    def subtypep(t):
        if not self.tds:
            return STop.subtypep(t)
        elif any(t.subtypep(t) for t in tds):
            return True
        elif t.inhabited() and self.inhabited() and all(x.disjoint(t) for x in self.tds):
            return False
        else:
            return super().subtypep(t)

    def canonicalize_once(nf):
        #TODO
        pass

    def compute_dnf():
        #TODO I need explanation for this one


"""
object t_SAnd {
  def main(args: Array[String]): Unit = {

    //test empty SAnd()
    val a = new SAnd()
    println(a.toString())

    //test SAnd with primal types
    val b = new SAnd(SAtomic(Types.Integer), SAtomic(Types.String), SAtomic(Types.Double))
    println(b.toString())

    //check Unit is valid
    println(a.unit == b.unit && a.unit == STop)

    //check Zero is valid
    println(a.zero == b.zero && a.zero == SEmpty)

    //check that create is working properly
    val c = a.create(SAtomic(Types.Integer))
    println(c.getClass() == a.getClass)
    println(c.toString == SAnd(SAtomic(Types.Integer)).toString)

  }
}
"""