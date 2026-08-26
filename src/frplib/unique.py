"""Singleton objects used as markers throughout.

This can be imported where needed without any circularity.

"""
from __future__ import annotations


# Attribute used to signal that the info system should
# get the info document path for this object from
# the object's name.

INFO_AUTO = object()
