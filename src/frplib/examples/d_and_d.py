"""Dungeons and Dragons character generator example in Chapter 4.2 of the text.

Exports:

dice_roll - an FRP factory for a roll of a balanced 6-sided die
dnd_attribute - an FRP factory representing a D&D character attribute
dnd_character - an FRP factory representing a D&D character's attributes

"""
# pylint: disable=invalid-name

from __future__ import annotations

from frplib.frps       import frp_factory
from frplib.kinds      import uniform
from frplib.statistics import Sum

__all__ = [
    'dice_roll',
    'dnd_attribute',
    'dnd_character',
]


@frp_factory
def dice_roll():
    "the roll of a balanced 6-sided die"
    return uniform(1, 2, ..., 6)

@frp_factory
def dnd_attribute():
    "a score for a D&D character attribute"
    D_1, D_2, D_3 = dice_roll(), dice_roll(), dice_roll()
    return Sum(D_1 * D_2 * D_3)

@frp_factory
def dnd_character():
    "a D&D character's attribute scores"
    S = dnd_attribute()    # Strength
    I = dnd_attribute()    # Intelligence
    W = dnd_attribute()    # Wisdom
    Co = dnd_attribute()   # Constitution
    D = dnd_attribute()    # Dexterity
    Ch = dnd_attribute()   # Charisma

    return S * I * W * Co * D * Ch
