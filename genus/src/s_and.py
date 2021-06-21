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
from simple_type_d import SimpleTypeD
from s_top import STop
from s_empty import SEmpty
from s_atomic import SAtomic
from s_combination import SCombination
from utils import generate_lazy_val
from genus_types import NormalForm,createSAnd

class SAnd(SCombination):
	"""An intersection type, which is the intersection of zero or more types.
	@param tds list, zero or more types"""

	#equivalent to the scala "create"
	#def __init__(self, tds):
	#	super(SAnd, self).__init__()
	#	self.tds = tds
	
	def __str__(self):
		return "[SAnd " + ",".join([str(td) for td in self.tds]) + "]"

	@staticmethod
	def create(tds):
		return createSAnd(tds)

	unit = STop.get_omega()
	zero = SEmpty.get_epsilon()

	def annihilator(this, a, b):
		return b.supertypep(a)

	def typep(self,a):
		return all(t.typep(a) for t in self.tds)

	def inhabited_down(self, opt):

		dnf = generate_lazy_val(lambda : self.canonicalize(NormalForm.DNF))
		cnf = generate_lazy_val(lambda : self.canonicalize(NormalForm.CNF))

		inhabited_dnf = generate_lazy_val(lambda : dnf.inhabited())
		inhabited_cnf = generate_lazy_val(lambda : cnf.inhabited())

		if any(t.contains(False) for t in self.tds):
			return False
		elif all(type(t) == SAtomic for t in self.tds):
		#   here we would like to check every 2-element subset
		#   if we find a,b such that a and b are disjoint,
		#   then we know self is not inhabited
			any(self.tds[a].disjointp( self.tds[b])
				for a in range(self.tds.length)
				for b in range(a,self.tds.length)
				if a > b)
		elif dnf() != self and inhabited_dnf():
			return inhabited_dnf()
		elif cnf() != self and inhabited_cnf():
			return inhabited_cnf()
		else:
			return super()._inhabited_down

	def _disjoint_down(self, t):
		inhabited_t = generate_lazy_val(lambda : t.inhabited())
		inhabited_self = generate_lazy_val(lambda: self.inhabited())

		if any(t.disjoint(t2) for t2 in self.tds):
			return True
		elif t in self.tds and inhabited_t() and inhabited_self():
			return False
		elif inhabited_t() \
				and inhabited_self() \
				and any(x.subtypep(t)==True
						or t.subtypep(x)==True
						for x in self.tds):
			return False
		else:
			return super()._disjoint_down(t)

	def _subtypep_down(self,t):
		if not self.tds:
			return STop.subtypep(t)
		elif any(t2.subtypep(t) for t2 in self.tds):
			return True
		elif t.inhabited() and self.inhabited() and all(x.disjoint(t) for x in self.tds):
			return False
		else:
			return super()._subtypep_down(t)

	def canonicalize_once(self,nf):
		#TODO
		return self

	def compute_dnf(self):
		#TODO I need explanation for this one
		return self

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