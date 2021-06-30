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

from .genus_types import NormalForm, createSAnd
from .genus_types import NormalForm, orp, andp, topp, notp
from .genus_types import cmp_type_designators
from .genus_types import combop
from .genus_types import createSAnd, createSOr
from .genus_types import memberimplp, notp, createSMember, notp, orp, andp, atomicp
from .s_and import SAnd
from .s_atomic import SAtomic
from .s_combination import SCombination
from .s_custom import SCustom
from .s_empty import SEmptyImpl, SEmpty
from .s_eql import SEql
from .s_member import SMemberImpl, SMember
from .s_not import SNot
from .s_or import SOr
from .s_top import STopImpl, STop
from .simple_type_d import SimpleTypeD, TerminalType
from .utils import compare_sequence
from .utils import find_simplifier, find_first
from .utils import fixed_point, generate_lazy_val
from .utils import flat_map
from .utils import flat_map, generate_lazy_val
from .utils import generate_lazy_val
from .utils import get_all_subclasses
from .utils import remove_element
from .utils import search_replace
from .utils import uniquify
