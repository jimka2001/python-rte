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
"""
[0-3] Advancement tracker
get_epsilon 3
__init__ 3
__str__ 3
typep 3
_inhabited_down 3
_disjoint_down 3
subtypep 3
cmp_to_same_class_obj 3

TODO: move the tests on their own
"""
class SEmpty(SimpleTypeD):
    """The empty type, subtype of all types."""
    __instance = None

    @staticmethod
    def get_epsilon():
        if SEmpty.__instance is None:
            SEmpty()
        return SEmpty.__instance

    def __init__(self):
        super(SEmpty, self).__init__()
        if SEmpty.__instance is not None:
           raise Exception("Please use SEmpty.get_epsilon() as SEmpty is unique and can't be duplicated")
        else:
           SEmpty.__instance = self

    def __str__(self):
        return "Empty"

    def typep(self, any):
        return False

    def _inhabited_down(self):
        return False

    def _disjoint_down(self, t):
        return True

    def subtypep(self, t):
        return True

    def cmp_to_same_class_obj(self, t):
        return False

""" Scala code to print values used for testing:

object t_SEmpty {
  def main(args: Array[String]): Unit = {
    println(SEmpty.toString() == "Empty")
    println(!SEmpty.typep(Types.Integer))
    println(SEmpty.inhabitedDown.contains(false))

    //println(SEmpty.disjointDown(SAtomic(Types.Integer)).contains(true))
    println(SEmpty.subtypep(SAtomic(Types.Integer)).contains(true))
    println(SEmpty.subtypep((SEmpty)).contains(true))

    println(!SEmpty.cmpToSameClassObj(SEmpty))
    println(!SEmpty.cmpToSameClassObj(SAtomic(Types.Integer)))
  }
}
"""
