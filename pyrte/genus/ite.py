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


def transitions_to_ite(td_id_pairs, default=None):
    # compute an ite structure from a list of pairs. each pair is a SimpleTypeD and an exit_value.
    #  normally the exit_value is an int, but may actually be anything, even another ite.
    # An ite is either a 1-tuple, such as (42,), or it is a 3-tuple consisting of (SimpleTypeD,ite,ite).
    # The semantics are implemented by the function eval_ite
    from genus.s_top import STop
    from genus.s_empty import SEmpty
    from genus.s_and import SAnd
    from genus.s_not import SNot
    from genus.genus_types import NormalForm
    if not td_id_pairs:
        return (default,)
    else:
        pivot_pre, idx = td_id_pairs[0]
        pivot = pivot_pre.canonicalize(NormalForm.DNF)
        if pivot == STop:
            return (idx,)
        elif pivot == SEmpty:
            return transitions_to_ite(td_id_pairs[1:], default)
        else:
            ltd = pivot.find_first_leaf_td()
            assert ltd is not None, f"pivot={pivot} does not a valid first_leaf_type"
            positive = [(SAnd(td, ltd)
                         .canonicalize(NormalForm.DNF)
                         .replace(ltd, STop)
                         .canonicalize(NormalForm.DNF), idx) for td, idx in td_id_pairs]
            negative = [(SAnd(td, SNot(ltd))
                         .canonicalize(NormalForm.DNF)
                         .replace(ltd, SEmpty)
                         .canonicalize(NormalForm.DNF), idx) for td, idx in td_id_pairs]
            return (ltd,
                    transitions_to_ite(positive, default),
                    transitions_to_ite(negative, default))


def eval_ite(ite, element):
    # evaluate the semantics of an ite structure, given an element.
    # The ite structure represents an if-then-else tree where each internal node
    # is a type-designator, SimpleTypeD.
    # If the node is an internal node (td, positive_ite, negative_ite).
    # A test is made at the top node to determine whether the given element is a member
    # of the designated type td.typep(element).  If true, then recursively eval_ite
    # on the positive_ite (the then part), else eval_ite on the negative_ite (the else part).
    # If the node is a leaf node, (i.e., a 1-tuple), then return the 0'th element of that
    # 1-tuple.
    assert isinstance(ite,tuple)
    if 3 == len(ite):
        td, positive, negative = ite
        if td.typep(element):
            return eval_ite(positive,element)
        else:
            return eval_ite(negative,element)
    else:
        return ite[0]
