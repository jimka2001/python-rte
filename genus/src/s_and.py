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
create 0
unit 0
zero 0
annihilator 0
same_combination 0
typep 0
inhabited_down 0
_disjoint_down 0
subtypep 0
canonicalize_once 0
compute_dnf 0
"""
import simple_type_d

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

	def unit:
		#implement when STop is implemented
		raise NotImplementedError

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