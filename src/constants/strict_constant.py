# -*- coding: utf-8 -*-

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/08 (Created: 2024/10/20)"

from .constant import ConstantMeta


class StrictConstantMeta(ConstantMeta):
    @staticmethod
    def is_constant_attr(name: str) -> bool:
        """
        特殊属性以外の全ての属性を定数として扱う

        Args:
            name (str): 属性名
        Returns:
            bool: 特殊属性以外全てTrue
        """
        is_special = name.startswith("__") and name.endswith("__")
        return not is_special

    @staticmethod
    def is_settable_attr(name: str) -> bool:  # noqa: ARG004
        """
        変更可能な属性を一切許可しない

        Args:
            name (str): 属性名
        Returns:
            bool: 常にFalse
        """
        return False

class StrictConstant(metaclass=StrictConstantMeta):
    """
    完全に不変な定数を提供するクラス
    """
