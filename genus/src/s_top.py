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

from simple_type_d import SimpleTypeD 
from s_empty import SEmpty

""" test-coverage as (method name, state[0-3] {0 not implemented, 1 implemented, 2 partially tested,  3 fully done})
__str__ 1
typep   1
_inhabited_down 1
_disjoint_down  1
subtypep    1
cmp_to_same_class_obj   1
"""
class STop(SimpleTypeD):
    """The super type, super type of all types."""
    __instance = None

    @staticmethod
    def get_omega():
        if STop.__instance == None:
            STop()
        return STop.__instance

    def __init__(self):
        super(STop, self).__init__()
        if STop.__instance != None:
           raise Exception("Please use STop.get_omega() as STop is unique and can't be duplicated")
        else:
           STop.__instance = self

    def __str__(self):
        return "Top"

    def typep(self, any):
        return True

    def _inhabited_down(self):
        return True

    def _disjoint_down(self, t):
        return type(t) is SEmpty

    def _subtypep_down(self, t):
        from s_not import SNot
        inh = SNot(t).inhabited()
        if inh is None:
            return None
        elif inh is True:
            return False
        else:
            return True

    def cmp_to_same_class_obj(self, t):
        return False

"""
object t_STop {
  def main(args: Array[String]): Unit = {
    println(STop.toString() == "Top")
    println(STop.typep(Types.Integer))
    println(STop.inhabitedDown.contains(true))

    //println(STop.disjointDown(SAtomic(Types.Integer)).contains(false))
    //println(STop.disjointDown((SEmpty)).contains(true))
    println(STop.subtypep(SAtomic(Types.Integer)).contains(false))
    println(STop.subtypep((STop)).contains(true))

    println(!STop.cmpToSameClassObj(STop))
    println(!STop.cmpToSameClassObj(SAtomic(Types.Integer)))
  }
}
"""
