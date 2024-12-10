# -*- coding: utf-8 -*-

"""
This module defines a `StrictConstant` class and its metaclass `StrictConstantMeta`
which enforce strict immutability on class attributes.
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/08 (Created: 2024/10/20)"

from .constant import ConstantMeta


class StrictConstantMeta(ConstantMeta):
    @staticmethod
    def is_constant_attr(name: str) -> bool:
        """
        Treat all attributes as constants except special attributes.

        Args:
            name (str): Attribute name

        Returns:
            bool: True if the attribute is not special, False

        Note:
            Special attributes are those that start and end with double underscores.
        """
        is_special = name.startswith("__") and name.endswith("__")
        return not is_special

    @staticmethod
    def is_settable_attr(name: str) -> bool:  # noqa: ARG004
        """
        Do not allow any mutable attributes.

        Args:
            name (str): Attribute name

        Returns:
            bool: False

        Note:
            This method always returns False to enforce strict immutability.
        """
        return False

class StrictConstant(metaclass=StrictConstantMeta):
    """
    A class that enforces strict immutability on its attributes.
    """
