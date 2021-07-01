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

from enum import Enum


class NormalForm(Enum):
	DNF = 1
	CNF = 2


def is_even(x):
	return isinstance(x, int) and not (x & 1)


# return 0 if a == b
#        -1 if a < b
#        1 if a > b
def cmp_type_designators(a, b):
	if a == b:
		return 0
	elif type(a) == type(b):
		return a.cmp_to_same_class_obj(b)
	elif type(a).__name__ < type(b).__name__:
		return -1
	else:
		return 1


def createSAnd(tds):
	from pyrte.genus.s_top import STop
	from pyrte.genus.s_and import SAnd
	if not tds:
		return STop
	elif len(tds) == 1:
		return tds[0]
	else:
		return SAnd(*tds)


def createSOr(tds):
	from pyrte.genus.s_empty import SEmpty
	from pyrte.genus.s_or import SOr
	if not tds:
		return SEmpty
	elif len(tds) == 1:
		return tds[0]
	else:
		return SOr(*tds)


def createSMember(items):
	from pyrte.genus.s_empty import SEmpty
	from pyrte.genus.s_member import SMember
	from pyrte.genus.s_eql import SEql
	if not items:
		return SEmpty
	elif len(items) == 1:
		return SEql(items[0])
	else:
		return SMember(*items)


def orp(this):
	from pyrte.genus.s_or import SOr
	return isinstance(this, SOr)


def andp(this):
	from pyrte.genus.s_and import SAnd
	return isinstance(this, SAnd)


def combop(this):
	from pyrte.genus.s_combination import SCombination
	return isinstance(this, SCombination)


def notp(this):
	from pyrte.genus.s_not import SNot
	return isinstance(this, SNot)


def atomicp(this):
	from pyrte.genus.s_atomic import SAtomic
	return isinstance(this, SAtomic)


def topp(this):
	from pyrte.genus.s_top import STopImpl
	return isinstance(this, STopImpl)


def emptyp(this):
	from pyrte.genus.s_empty import SEmptyImpl
	return isinstance(this, SEmptyImpl)


def memberimplp(this):
	from pyrte.genus.s_member import SMemberImpl
	return isinstance(this, SMemberImpl)


def memberp(this):
	from pyrte.genus.s_member import SMember
	return isinstance(this, SMember)


def eqlp(this):
	from pyrte.genus.s_eql import SEql
	return isinstance(this, SEql)
