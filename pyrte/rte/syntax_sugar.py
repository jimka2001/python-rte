from typing import TypeGuard

from rte.r_rte import Rte


def Plus(r: Rte) -> 'Cat':
    from rte.r_cat import Cat
    from rte.r_star import Star
    assert isinstance(r, Rte)
    return Cat(r, Star(r))


def Member(*vs) -> 'Singleton':
    from genus.s_member import SMember
    from rte.r_singleton import Singleton
    return Singleton(SMember(*vs))


def Eql(v) -> 'Singleton':
    from genus.s_eql import SEql
    from rte.r_singleton import Singleton
    return Singleton(SEql(v))


def Satisfies(f, printable) -> 'Singleton':
    from genus.s_satisfies import SSatisfies
    from rte.r_singleton import Singleton
    return Singleton(SSatisfies(f, printable))


def Atomic(cl) -> 'Singleton':
    from genus.s_atomic import SAtomic
    from rte.r_singleton import Singleton
    return Singleton(SAtomic(cl))


def plusp(rte: Rte) -> TypeGuard['Cat']:
    from rte.r_cat import catp
    from rte.r_star import starp
    return catp(rte) \
        and 2 == len(rte.operands) \
        and ((starp(rte.operands[1]) and rte.operands[1].operand == rte.operands[0])
             or (starp(rte.operands[0]) and rte.operands[0].operand == rte.operands[1]))
