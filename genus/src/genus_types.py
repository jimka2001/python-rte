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
	return type(x) is int and not (x & 1)


def cmp_type_designators(a, b):
	def cmp(a, b):
		if a == b:
			return False
		elif type(a) == type(b):
			return a.cmp_to_same_class_obj(b)
		else:
			return type(a).__name__ < type(b).__name__

	return -1 if cmp(a,b) else 0


def createSAnd(tds):
	from s_top import STop
	from s_and import SAnd
	if not tds:
		return STop
	elif len(tds) == 1:
		return tds[0]
	else:
		return SAnd(*tds)


def createSOr(tds):
	from s_empty import SEmpty
	from s_or import SOr
	if not tds:
		return SEmpty
	elif len(tds) == 1:
		return tds[0]
	else:
		return SOr(*tds)


def createSMember(items):
	from s_empty import SEmpty
	from s_member import SMember
	from s_eql import SEql
	if not items:
		return SEmpty
	elif len(items) == 1:
		return SEql(items[0])
	else:
		return SMember(*items)


def orp(this):
	from s_or import SOr
	return isinstance(this, SOr)


def andp(this):
	from s_and import SAnd
	return isinstance(this, SAnd)


def combop(this):
	from s_combination import SCombination
	return isinstance(this, SCombination)


def notp(this):
	from s_not import SNot
	return isinstance(this, SNot)


def atomicp(this):
	from s_atomic import SAtomic
	return isinstance(this, SAtomic)


def topp(this):
	from s_top import STopImpl
	return isinstance(this, STopImpl)


def emptyp(this):
	from s_empty import SEmptyImpl
	return isinstance(this, SEmptyImpl)


def memberimplp(this):
	from s_member import SMemberImpl
	return isinstance(this, SMemberImpl)


def memberp(this):
	from s_member import SMember
	return isinstance(this, SMember)


def eqlp(this):
	from s_eql import SEql
	return isinstance(this, SEql)
