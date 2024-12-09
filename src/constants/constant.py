# -*- coding: utf-8 -*-

"""
This module defines a constant class and its associated metaclass to enforce immutability
and prevent redefinition of constants.
"""

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/08 (Created: 2024/10/20)"

class ConstantError(Exception):
    """Exception class for constant error
    """

    INHERITANCE_ERROR = "Can't inheritance of [{0}] and [{1}] together"
    COLLISION_ERROR = "Collision the constant [{0}]"
    REBIND_ERROR = "Can't rebind constant [{0}]"
    INSTANCE_ERROR = "Can't make instance of Constant class"
    ATTRIBUTE_ERROR = "Attribute [{0}] were not constant or not settable."
    SET_ERROR = "Can't set attribute to Constant [{0}]"

class ConstantMeta(type):
    """Metaclass for constant class
    """

    def __new__(cls, classname: str, bases: tuple, class_dict: dict) -> "ConstantMeta":
        """
        Create a new class instance while ensuring it adheres to specific constraints.
        This method performs the following checks and operations:
            1. Validates that the class does not inherit from multiple different `ConstantMeta` classes.
            2. Ensures there are no constant attribute collisions among parent classes.
            3. Checks that constants are not redefined in the new class.
            4. Replaces the `__init__` method to prevent instance creation, raising a `ConstantError` if attempted.

        Args:
            classname (str): The name of the new class.
            bases (tuple): A tuple of base classes for the new class.
            class_dict (dict): A dictionary of attributes for the new class.
        Returns:
            ConstantMeta: The newly created class instance.
        Raises:
            ConstantError: If any of the validation checks fail or if an instance creation is attempted.
        """

        sub_clses = [cls for cls in bases if isinstance(cls, ConstantMeta)]
        for sub_cls in sub_clses[1:]:
            if sub_clses[0] != sub_cls:
                raise ConstantError(
                    ConstantError.INHERITANCE_ERROR.format(
                        sub_clses[0].__name__, sub_cls.__name__
                    )
                )

        # 親クラス同士で定数の衝突が起こっていないか確認
        super_consts: set[str] = set()
        for base in bases:
            base_consts = ConstantMeta.__get_constant_attr(base.__dict__)
            collisions = (super_consts & base_consts)
            if collisions:
                collis_str = ", ".join(collisions)
                raise ConstantError(
                    ConstantError.COLLISION_ERROR.format(collis_str)
                )
            super_consts |= base_consts

        # 定義するクラスで定数の再定義をしていないか確認
        new_consts = ConstantMeta.__get_constant_attr(class_dict)
        rebinds = (super_consts & new_consts)
        if rebinds:
            rebinds_str = ", ".join(rebinds)
            raise ConstantError(ConstantError.REBIND_ERROR.format(rebinds_str))

        # __init__関数置き換えてインスタンス生成を禁止する
        def _meta__init__(*_):
            """Raise ConstantError when trying to create

            Raises:
                ConstantError: When trying to create an instance
            """
            # インスタンスの生成をしようとした際、ConstantErrorを送出する。
            raise ConstantError(ConstantError.INSTANCE_ERROR)
        # __init__関数を置き換えてインスタンス生成を禁止する。
        class_dict["__init__"] = _meta__init__

        return type.__new__(cls, classname, bases, class_dict)

    @staticmethod
    def __get_constant_attr(class_dict: dict) -> set[str]:
        """Get the set of attributes to be treated as constants.

        Args:
            class_dict (dict): The dictionary of attributes for the class.

        Returns:
            set[str]: The set of attributes to be treated as constants.

        Raises:
            ConstantError: If an attribute is not a constant or cannot be stored in a class variable.

        Note:
            Special attributes are excluded from the set of attributes to be treated as constants.
        """
        # 特殊なアトリビュートを除くアトリビュートを取得する
        attrs = {
            attr for attr in class_dict if not ConstantMeta.__is_special_func(attr)
        }
        # アトリビュートがすべて定数または例外的にクラス変数に格納可能な
        # 変数であることを確認する
        cnst_attr = {attr for attr in attrs if ConstantMeta.is_constant_attr(attr)}
        var_attr = {attr for attr in attrs if ConstantMeta.is_settable_attr(attr)}
        wrong_attr = attrs - (cnst_attr | var_attr)
        if wrong_attr:
            wrong_attr_str = ", ".join(wrong_attr)
            raise ConstantError(
                ConstantError.ATTRIBUTE_ERROR.format(wrong_attr_str)
            )
        return cnst_attr

    @staticmethod
    def __is_special_func(name):
        """Check if the attribute is a special attribute.

        Args:
            name (str): The name of the attribute.

        Returns:
            bool: True if the attribute is special, False otherwise.

        Note:
            Special attributes are those that start and end with "__
        """
        return name.startswith("__") and name.endswith("__")

    @classmethod
    def is_constant_attr(cls, name):
        """Check if the attribute should be treated as a constant.

        Args:
            name (str): The name of the attribute.

        Returns:
            bool: True if the attribute should be treated as a constant, False otherwise

        Note:
            By default, attributes that start with "__" are considered special and not constants.
        """
        return (not name.startswith("__"))

    @classmethod
    def is_settable_attr(cls, name):
        """Check if the attribute can be stored in a class variable exceptionally.

        Args:
            name (str): The name of the attribute.

        Returns:
            bool: True if the attribute can be stored in a class variable, False otherwise

        Note:
            By default, all attributes are considered constants and cannot be set.
        """
        return (not cls.is_constant_attr(name))

    def __setattr__(cls, name, value):
        """Set the attribute value.
        Args:
            name (str): The name of the attribute.
            value: The value to set.

        Raises:
            ConstantError: If the attribute is a constant or cannot be set.

        Note:
            If the attribute is a constant or cannot be set, a `ConstantError` is raised.
        """
        cls_type = type(cls)
        if cls.is_constant_attr(name) or (not cls_type.is_settable_attr(name)):
            raise ConstantError(ConstantError.SET_ERROR.format(name))
        super().__setattr__(name, value)

class Constant(metaclass=ConstantMeta):
    """A class for defining constants.
    """


